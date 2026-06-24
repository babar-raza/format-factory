"""
CSV structural element: csv:header

Spec ref: RFC 4180 — CSV header row
Fact ref: FACT-CSV-001
QName: csv:header
Canonical class: Header
Facade: CsvHeader
"""
from __future__ import annotations
from typing import Any


class Header:
    """Canonical spec-shaped class for csv:header."""

    spec_qname = "csv:header"
    spec_fact_ref = "FACT-CSV-001"
    namespace_uri = "urn:ietf:rfc:4180:csv"
    local_name = "header"
    facade_names = ["CsvHeader"]

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @property
    def names(self) -> list[str]:
        return list(self._data.get("names", []))

    @property
    def count(self) -> int:
        return len(self.names)

    @property
    def has_duplicates(self) -> bool:
        n = self.names
        return len(n) != len(set(n))

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    def __repr__(self) -> str:
        return f"Header(count={self.count}, names={self.names[:3]}{'...' if self.count > 3 else ''})"
