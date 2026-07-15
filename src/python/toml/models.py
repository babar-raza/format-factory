"""Domain model classes for TOML (Tom's Obvious, Minimal Language).

Classes:
    TomlDocument — typed wrapper over the dict returned by load_toml()

spec_qname: toml:table
spec_fact_ref: see shared/qname-registry/toml.yaml
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar


class TomlDocument:
    """Typed domain model for a TOML document.

    Wraps the neutral model dict returned by load_toml().
    Neutral model keys: data (dict), path (str, optional).
    """

    spec_qname: ClassVar[str] = "toml:table"
    spec_fact_ref: ClassVar[str] = "FACT-TOML-001"
    namespace_uri: ClassVar[str] = "urn:format:toml:1.0"
    local_name: ClassVar[str] = "table"
    facade_names: ClassVar[list] = []

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

    # Additional structural properties (FACT-TOML-002, FACT-TOML-004)
    @property
    def is_flat(self) -> bool:
        """True if the document has no nested tables."""
        return not self.has_nested_tables

    @property
    def has_booleans(self) -> bool:
        """True if any top-level value is a boolean."""
        return any(isinstance(v, bool) for v in self._doc().values())

    @property
    def table_count(self) -> int:
        """Number of top-level keys whose value is a table (dict)."""
        return sum(1 for v in self._doc().values() if isinstance(v, dict))

    # Additional key analysis properties (FACT-TOML-001)

    @property
    def has_scalars(self) -> bool:
        """True if the document has at least one top-level scalar key."""
        return self.scalar_key_count > 0

    @property
    def is_single_key(self) -> bool:
        """True if the document has exactly one top-level key."""
        return self.key_count == 1

    @property
    def is_nested(self) -> bool:
        """True if the document has nested tables or arrays."""
        return self.has_nested_tables or self.has_arrays

    # Document classification properties (FACT-TOML-001)

    @property
    def has_only_scalars(self) -> bool:
        """True if all top-level values are scalars (no nested tables, no arrays)."""
        return self.has_scalars and self.is_flat and not self.has_arrays

    @property
    def is_mixed(self) -> bool:
        """True if the document has both scalar keys and at least one nested table or array."""
        return self.has_scalars and self.is_nested

    @property
    def array_count(self) -> int:
        """Number of top-level keys whose value is an array (list)."""
        return sum(1 for v in self._doc().values() if isinstance(v, list))

    # Size and value type properties (FACT-TOML-001 R1242)

    @property
    def is_large(self) -> bool:
        """True if key_count > 20."""
        return self.key_count > 20

    @property
    def has_numbers(self) -> bool:
        """True if any top-level value is int or float (not bool)."""
        return any(
            isinstance(v, (int, float)) and not isinstance(v, bool)
            for v in self._doc().values()
        )

    @property
    def has_strings(self) -> bool:
        """True if any top-level value is a str."""
        return any(isinstance(v, str) for v in self._doc().values())

    # Value type distribution properties (FACT-TOML-001 R1262)

    @property
    def has_mixed_values(self) -> bool:
        """True if more than one distinct Python type exists at top level."""
        types = {type(v) for v in self._doc().values()}
        return len(types) > 1

    @property
    def string_key_count(self) -> int:
        """Number of top-level string values."""
        return sum(1 for v in self._doc().values() if isinstance(v, str))

    @property
    def numeric_key_count(self) -> int:
        """Number of top-level numeric (int/float, not bool) values."""
        return sum(
            1 for v in self._doc().values()
            if isinstance(v, (int, float)) and not isinstance(v, bool)
        )

    # Value type inventory properties (FACT-TOML-001 R1282)

    @property
    def boolean_key_count(self) -> int:
        """Number of top-level boolean values."""
        return sum(1 for v in self._doc().values() if isinstance(v, bool))

    @property
    def list_key_count(self) -> int:
        """Number of top-level list/array values."""
        return sum(1 for v in self._doc().values() if isinstance(v, list))

    @property
    def max_array_length(self) -> int:
        """Maximum length of any top-level list value; 0 if no lists."""
        lengths = [len(v) for v in self._doc().values() if isinstance(v, list)]
        return max(lengths) if lengths else 0

    def set_key(self, key_path: str, value: Any) -> None:
        """Set a value at the given dot-separated key path, mutating this document in place.

        Args:
            key_path: Dot-separated key path (e.g., ``"section.key"``).
            value: The new value to set.
        """
        from .toml_codec import set_value
        updated = set_value(self._doc(), key_path, value)
        if "data" in self._data:
            self._data["data"] = updated
        else:
            self._data = updated

    def delete_key(self, key_path: str) -> None:
        """Delete the key at the given dot-separated key path, mutating this document in place.

        Args:
            key_path: Dot-separated key path (e.g., ``"section.key"``).
        """
        from .toml_codec import delete_key as _delete_key
        updated = _delete_key(self._doc(), key_path)
        if "data" in self._data:
            self._data["data"] = updated
        else:
            self._data = updated

    def to_toml_string(self) -> str:
        """Serialize this document back to a TOML-formatted string."""
        from .toml_codec import _write_section  # type: ignore[attr-defined]
        lines: list[str] = []
        _write_section(lines, self._doc())
        return "\n".join(lines) + "\n"

    def save_to_file(self, path: "str | Path") -> None:
        """Save this document to a TOML file (UTF-8).

        Args:
            path: Destination file path. Parent directories are created as needed.

        Raises:
            TomlError: If path is empty or None.
        """
        from .exceptions import TomlError
        from .toml_codec import write_toml
        if not path:
            raise TomlError("path must not be empty")
        dest = Path(path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        write_toml(self._doc(), dest)

    def to_dict(self) -> dict[str, Any]:
        """Return the underlying neutral model dict."""
        return dict(self._data)

    def data(self) -> dict[str, Any]:
        """Return the inner TOML data dict."""
        return dict(self._doc())

    def __repr__(self) -> str:
        return f"TomlDocument(key_count={self.key_count})"
