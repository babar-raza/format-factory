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

    def to_list(self) -> list[Any]:
        """Return the underlying records list."""
        return list(self._records)

    def __repr__(self) -> str:
        return f"NdjsonDocument(record_count={self.record_count})"
