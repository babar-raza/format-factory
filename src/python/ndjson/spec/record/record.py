"""
NDJSON structural element: ndjson:record

Spec ref: Newline Delimited JSON (ndjson.org) — one JSON object per line
Fact ref: FACT-NDJSON-001
QName: ndjson:record
Canonical class: Record
Facade: NdjsonRecord
"""
from __future__ import annotations
from typing import Any


class Record:
    """Canonical spec-shaped class for ndjson:record (one JSON line)."""

    spec_qname = "ndjson:record"
    spec_fact_ref = "FACT-NDJSON-001"
    namespace_uri = "urn:format:ndjson:1.0"
    local_name = "record"
    facade_names = ["NdjsonRecord"]

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = dict(data)

    @property
    def keys(self) -> list[str]:
        return list(self._data.keys())

    @property
    def field_count(self) -> int:
        return len(self._data)

    def get(self, key: str) -> Any:
        return self._data.get(key)

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    def __repr__(self) -> str:
        return f"Record(field_count={self.field_count})"
