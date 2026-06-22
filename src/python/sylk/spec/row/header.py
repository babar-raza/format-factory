"""
SYLK structural element: sylk:header

Spec ref: SYLK (Symbolic Link) format — ID record header
Fact ref: FACT-SYLK-001
QName: sylk:header
Canonical class: Header
Facade: SylkHeader
"""
from __future__ import annotations
from typing import Any


class Header:
    """Canonical spec-shaped class for sylk:header (SYLK ID record)."""

    spec_qname = "sylk:header"
    spec_fact_ref = "FACT-SYLK-001"
    namespace_uri = "urn:format:sylk:1.0"
    local_name = "header"
    facade_names = ["SylkHeader"]

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @property
    def program(self) -> str:
        return str(self._data.get("program", ""))

    @property
    def row_count(self) -> int:
        return int(self._data.get("row_count", 0))

    @property
    def col_count(self) -> int:
        return int(self._data.get("col_count", 0))

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    def __repr__(self) -> str:
        return f"Header(program={self.program!r}, rows={self.row_count})"
