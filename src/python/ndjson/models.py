"""Domain model classes for NDJSON (Newline-Delimited JSON).

Classes:
    NdjsonDocument — typed wrapper over the list returned by load_ndjson()

spec_qname: ndjson:record
spec_fact_ref: see shared/qname-registry/ndjson.yaml
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


class NdjsonDocument:
    """Typed domain model for an NDJSON document.

    Wraps the list of records returned by load_ndjson().
    Each record is typically a dict, but may be any JSON-serializable value.
    """

    spec_qname = "ndjson:record"
    spec_fact_ref = "FACT-NDJSON-001"
    namespace_uri = "https://ndjson.org/"
    local_name = "record"
    facade_names = []

    def __init__(self, records: list[Any]) -> None:
        self._records = list(records)

    @classmethod
    def from_file(cls, path: str | Path) -> "NdjsonDocument":
        """Load an NDJSON file and return an NdjsonDocument."""
        from .ndjson_codec import load_ndjson
        return cls(load_ndjson(path))

    @property
    def records(self) -> list[Any]:
        """All records in document order."""
        return list(self._records)

    @property
    def record_count(self) -> int:
        """Number of records in the document."""
        return len(self._records)

    def get_record(self, index: int) -> Any:
        """Return the record at the given index, or None if out of bounds."""
        if 0 <= index < len(self._records):
            return self._records[index]
        return None

    def get_field(self, record_index: int, field: str, default: Any = None) -> Any:
        """Return a field value from a dict-type record, or default if missing."""
        record = self.get_record(record_index)
        if isinstance(record, dict):
            return record.get(field, default)
        return default

    # Document dimension properties (FACT-NDJSON-001)

    @property
    def is_empty(self) -> bool:
        """True if the document has no records."""
        return self.record_count == 0

    @property
    def is_single_record(self) -> bool:
        """True if the document has exactly one record."""
        return self.record_count == 1

    @property
    def has_records(self) -> bool:
        """True if the document has at least one record."""
        return self.record_count > 0

    @property
    def is_multi_record(self) -> bool:
        """True if the document has more than one record."""
        return self.record_count > 1

    @property
    def all_objects(self) -> bool:
        """True if all records are JSON objects (dicts)."""
        return bool(self._records) and all(isinstance(r, dict) for r in self._records)

    @property
    def all_arrays(self) -> bool:
        """True if all records are JSON arrays (lists)."""
        return bool(self._records) and all(isinstance(r, list) for r in self._records)

    # Additional record analysis properties (FACT-NDJSON-001)

    @property
    def has_mixed_types(self) -> bool:
        """True if records contain a mix of objects, arrays, or other types."""
        return bool(self._records) and not self.all_objects and not self.all_arrays

    @property
    def all_scalars(self) -> bool:
        """True if all records are scalar values (not objects or arrays)."""
        return bool(self._records) and all(
            not isinstance(r, (dict, list)) for r in self._records
        )

    @property
    def max_keys(self) -> int:
        """Maximum number of keys in any object record. Returns 0 if no object records."""
        key_counts = [len(r) for r in self._records if isinstance(r, dict)]
        return max(key_counts) if key_counts else 0

    def to_list(self) -> list[Any]:
        """Return the underlying records list."""
        return list(self._records)

    def __repr__(self) -> str:
        return f"NdjsonDocument(record_count={self.record_count})"
