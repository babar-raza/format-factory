from __future__ import annotations
from typing import Any


class TableCell:
    """Canonical spec-shaped class for table:table-cell in FODT context (ODF §9.5)."""

    spec_qname = "table:table-cell"
    spec_fact_ref = "FACT-FODT-007"

    def __init__(self, data: dict[str, Any]):
        self._data = data

    @property
    def text(self) -> str:
        return self._data.get("text", "")

    @property
    def spans(self) -> list:
        return self._data.get("spans", [])

    @property
    def col_span(self) -> int:
        return self._data.get("col_span", 1)

    @property
    def row_span(self) -> int:
        return self._data.get("row_span", 1)

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)
