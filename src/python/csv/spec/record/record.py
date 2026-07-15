"""
CSV structural element: csv:record

Spec ref: RFC 4180 — Common Format and MIME Type for Comma-Separated Values
Fact ref: FACT-CSV-001
QName: csv:record
Canonical class: Record
Facade: CsvRecord
"""
from __future__ import annotations
from typing import ClassVar


class Record:
    """Canonical spec-shaped class for csv:record (RFC 4180 row)."""

    spec_qname: ClassVar[str] = "csv:record"
    spec_fact_ref: ClassVar[str] = "FACT-CSV-001"
    namespace_uri: ClassVar[str] = "urn:ietf:rfc:4180:csv"
    local_name: ClassVar[str] = "record"
    facade_names: ClassVar[list] = ["CsvRecord"]

    def __init__(self, fields: list[str]) -> None:
        self._fields = list(fields)

    @property
    def fields(self) -> list[str]:
        return list(self._fields)

    @property
    def field_count(self) -> int:
        return len(self._fields)

    def get(self, index: int) -> str:
        if 0 <= index < len(self._fields):
            return self._fields[index]
        return ""

    def to_list(self) -> list[str]:
        return list(self._fields)

    def __repr__(self) -> str:
        return f"Record(field_count={self.field_count})"
