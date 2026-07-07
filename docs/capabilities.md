# Capability Registry

`src/nlp_policy_nz/capabilities.py` defines the shared capability contract for the package.
It is intentionally standard-library only so it can be imported, validated, and serialized
deterministically in GitHub Actions.

## Shape

Each `CapabilityEntry` records:

* `id`: stable lowercase dotted identifier such as `cli.process` or `api.search`
* `surface`: one of `cli`, `api`, `sdk`, or `mcp`
* `name` and `summary`: human-readable contract metadata
* `maturity`: `current` or `future`
* `classification`: `public`, `internal`, or `future`
* `required_fields`: ordered machine-readable contract fields
* `implementation_ref`: source or documentation reference
* `contract_kind`: the kind of surface, such as `command`, `http_route`, or `python_function`
* `aliases`: optional secondary identifiers for versioned or routed variants

## Validation

The module provides:

* `validate_capability_entries(...)` for stable-ID and duplicate-ID checks
* `validate_capability_registry(...)` for required surface coverage
* `load_capability_registry(...)` for JSON loading or access to the checked-in default registry
* `dump_capability_registry(...)` for canonical JSON output

The default registry covers:

* current CLI commands
* current API routes
* current SDK helpers
* future MCP capabilities

## Example

```python
from nlp_policy_nz.capabilities import DEFAULT_CAPABILITY_REGISTRY

registry = DEFAULT_CAPABILITY_REGISTRY
registry.write_json("capabilities.json")
```

