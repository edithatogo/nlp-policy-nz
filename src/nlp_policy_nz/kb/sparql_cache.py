"""Small JSON cache for Wikidata SPARQL lookups."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class JsonSparqlCache:
    """Persist SPARQL lookup results in a JSON file."""

    def __init__(self, path: str | Path) -> None:
        """Create a cache backed by *path*."""
        self.path = Path(path)

    def get(self, key: str) -> dict[str, Any] | None:
        """Return a cached object for *key*, if present."""
        data = self._read()
        value = data.get(key)
        return dict(value) if isinstance(value, dict) else None

    def set(self, key: str, value: dict[str, Any]) -> None:
        """Store *value* under *key*."""
        data = self._read()
        data[key] = value
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True),
            encoding="utf-8",
        )

    def _read(self) -> dict[str, Any]:
        """Read the cache file, returning an empty dict for a missing file."""
        if not self.path.is_file():
            return {}
        return json.loads(self.path.read_text(encoding="utf-8"))
