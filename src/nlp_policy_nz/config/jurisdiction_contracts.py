"""Shared document and JSON Schema boundary for jurisdiction configuration."""

from __future__ import annotations

import collections.abc
import json
from functools import lru_cache
from importlib.resources import files
from typing import TYPE_CHECKING, Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

if TYPE_CHECKING:
    from pathlib import Path


class ProfileLoadError(ValueError):
    """Raised when jurisdiction configuration fails its trusted boundary."""


class _UniqueKeySafeLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""


def _construct_unique_mapping(
    loader: _UniqueKeySafeLoader,
    node: yaml.nodes.MappingNode,
    deep: bool = False,
) -> dict[object, object]:
    mapping: dict[object, object] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise ProfileLoadError(f"duplicate key: {key}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


_UniqueKeySafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


def _unique_json_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ProfileLoadError(f"duplicate key: {key}")
        result[key] = value
    return result


def read_unique_document(path: Path) -> collections.abc.Mapping[str, Any]:
    """Read one JSON/YAML mapping while rejecting duplicate keys at every depth."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        raise ProfileLoadError(f"cannot read configuration: {path}") from error
    try:
        if path.suffix == ".json":
            payload = json.loads(text, object_pairs_hook=_unique_json_object)
        elif path.suffix in {".yaml", ".yml"}:
            payload = yaml.load(text, Loader=_UniqueKeySafeLoader)  # noqa: S506
        else:
            raise ProfileLoadError(f"unsupported configuration format: {path.suffix}")
    except ProfileLoadError:
        raise
    except (json.JSONDecodeError, yaml.YAMLError) as error:
        raise ProfileLoadError(f"invalid configuration syntax: {path}") from error
    if not isinstance(payload, collections.abc.Mapping):
        raise ProfileLoadError("configuration document must be an object")
    return payload


@lru_cache(maxsize=4)
def _schema_validator(schema_filename: str) -> Draft202012Validator:
    schema_resource = files("nlp_policy_nz.config.schemas").joinpath(schema_filename)
    schema = json.loads(schema_resource.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def validate_json_schema(
    payload: collections.abc.Mapping[str, Any],
    schema_filename: str,
) -> None:
    """Enforce a packaged Draft 2020-12 schema, including declared formats."""
    errors = sorted(
        _schema_validator(schema_filename).iter_errors(payload),
        key=lambda error: tuple(str(part) for part in error.absolute_path),
    )
    if not errors:
        return
    error = errors[0]
    location = ".".join(str(part) for part in error.absolute_path) or "<root>"
    format_name = error.validator_value if error.validator == "format" else None
    detail = f"format {format_name}: {error.message}" if format_name else error.message
    raise ProfileLoadError(f"JSON Schema validation failed at {location}: {detail}")
