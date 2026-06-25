"""Domain model classes for TOML (Tom's Obvious, Minimal Language).

Classes:
    TomlDocument — typed wrapper over the dict returned by load_toml()

spec_qname: toml:table
spec_fact_ref: see shared/qname-registry/toml.yaml
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


class TomlDocument:
    """Typed domain model for a TOML document.

    Wraps the neutral model dict returned by load_toml().
    Neutral model keys: data (dict), path (str, optional).
    """

    spec_qname = "toml:table"
    spec_fact_ref = "FACT-TOML-001"
    namespace_uri = "urn:format:toml:1.0"
    local_name = "table"
    facade_names = []

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @classmethod
    def from_file(cls, path: str | Path) -> "TomlDocument":
        """Load a TOML file and return a TomlDocument."""
        from .toml_codec import load_toml
        return cls(load_toml(path))

    def _doc(self) -> dict[str, Any]:
        """Return the inner data dict (handles load_toml wrapper)."""
        if "data" in self._data:
            return self._data["data"]
        return self._data

    @property
    def keys(self) -> list[str]:
        """Top-level key names."""
        return list(self._doc().keys())

    @property
    def key_count(self) -> int:
        """Number of top-level keys."""
        return len(self._doc())

    def get(self, key: str, default: Any = None) -> Any:
        """Return the value for a top-level key, or default if missing."""
        return self._doc().get(key, default)

    def has_key(self, key: str) -> bool:
        """Return True if the given top-level key exists."""
        return key in self._doc()

    @property
    def is_empty(self) -> bool:
        """True if the document has no top-level keys."""
        return self.key_count == 0

    @property
    def has_nested_tables(self) -> bool:
        """True if any top-level value is itself a table (dict)."""
        return any(isinstance(v, dict) for v in self._doc().values())

    @property
    def has_arrays(self) -> bool:
        """True if any top-level value is an array (list)."""
        return any(isinstance(v, list) for v in self._doc().values())

    @property
    def scalar_key_count(self) -> int:
        """Number of top-level keys whose value is a scalar (not a dict or list)."""
        return sum(1 for v in self._doc().values() if not isinstance(v, (dict, list)))

    def to_dict(self) -> dict[str, Any]:
        """Return the underlying neutral model dict."""
        return dict(self._data)

    def data(self) -> dict[str, Any]:
        """Return the inner TOML data dict."""
        return dict(self._doc())

    def __repr__(self) -> str:
        return f"TomlDocument(key_count={self.key_count})"
