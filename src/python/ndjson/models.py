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

    # Record count classification properties (FACT-NDJSON-001)

    @property
    def is_small(self) -> bool:
        """True if the document has 10 or fewer records."""
        return self.record_count <= 10

    @property
    def is_large(self) -> bool:
        """True if the document has more than 1000 records."""
        return self.record_count > 1000

    @property
    def min_keys(self) -> int:
        """Minimum number of keys in any object record. Returns 0 if no object records."""
        key_counts = [len(r) for r in self._records if isinstance(r, dict)]
        return min(key_counts) if key_counts else 0

    # Object shape analysis properties (FACT-NDJSON-001)

    @property
    def has_uniform_keys(self) -> bool:
        """True if all object records have the same number of keys.

        Returns True if there are no object records (vacuously true).
        """
        key_counts = [len(r) for r in self._records if isinstance(r, dict)]
        if not key_counts:
            return True
        return len(set(key_counts)) == 1

    @property
    def avg_keys(self) -> float:
        """Average number of keys across object records. Returns 0.0 if no object records."""
        key_counts = [len(r) for r in self._records if isinstance(r, dict)]
        if not key_counts:
            return 0.0
        return sum(key_counts) / len(key_counts)

    @property
    def is_wide_objects(self) -> bool:
        """True if the maximum key count in any object record exceeds 20."""
        return self.max_keys > 20

    # Key distribution analysis properties (FACT-NDJSON-001)

    @property
    def key_range(self) -> int:
        """Difference between max_keys and min_keys. Returns 0 if no object records."""
        return self.max_keys - self.min_keys

    @property
    def is_schema_consistent(self) -> bool:
        """True if all object records have the same key set (same keys, not just count).

        Returns True if there are no object records (vacuously true).
        """
        object_records = [r for r in self._records if isinstance(r, dict)]
        if not object_records:
            return True
        first_keys = frozenset(object_records[0].keys())
        return all(frozenset(r.keys()) == first_keys for r in object_records[1:])

    @property
    def object_count(self) -> int:
        """Number of records that are JSON objects (dicts)."""
        return sum(1 for r in self._records if isinstance(r, dict))

    # Record type distribution properties (FACT-NDJSON-001)

    @property
    def array_count(self) -> int:
        """Number of records that are JSON arrays (lists)."""
        return sum(1 for r in self._records if isinstance(r, list))

    @property
    def scalar_count(self) -> int:
        """Number of records that are scalar values (not dict or list)."""
        return sum(1 for r in self._records if not isinstance(r, (dict, list)))

    @property
    def object_fraction(self) -> float:
        """Fraction of records that are JSON objects. Returns 0.0 if no records."""
        if self.record_count == 0:
            return 0.0
        return self.object_count / self.record_count

    def append_record(self, record: Any) -> None:
        """Append a new record to this document in place.

        Args:
            record: Any JSON-serializable value (dict, list, scalar).

        Raises:
            NdjsonError: If record is None.
        """
        from .exceptions import NdjsonError
        if record is None:
            raise NdjsonError("record must not be None")
        self._records.append(record)

    def to_ndjson(self) -> str:
        """Serialize all records back to an NDJSON string (one JSON object per line, LF-terminated)."""
        import json as _json
        return "".join(_json.dumps(r, ensure_ascii=False) + "\n" for r in self._records)

    def save_to_file(self, path: "str | Path") -> None:
        """Save this document to a file as NDJSON (UTF-8, LF line endings, no BOM).

        Args:
            path: Destination file path. Parent directories are created as needed.

        Raises:
            NdjsonError: If path is empty or None.
        """
        from .exceptions import NdjsonError
        if not path:
            raise NdjsonError("path must not be empty")
        dest = Path(path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(self.to_ndjson(), encoding="utf-8")

    def to_list(self) -> list[Any]:
        """Return the underlying records list."""
        return list(self._records)

    def __repr__(self) -> str:
        return f"NdjsonDocument(record_count={self.record_count})"
