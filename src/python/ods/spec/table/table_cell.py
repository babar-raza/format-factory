from __future__ import annotations
from typing import Any, ClassVar


class TableCell:
    """Canonical spec-shaped class for table:table-cell in ODS context (ODF §9.5)."""

    spec_qname: ClassVar[str] = "table:table-cell"
    spec_fact_ref: ClassVar[str] = "SAL-ODS-01069"

    def __init__(self, data: dict[str, Any]):
        self._data = data

    @property
    def value(self) -> str:
        return self._data.get("value", "")

    @property
    def value_type(self) -> str:
        return self._data.get("value_type", "string")

    @property
    def col_span(self) -> int:
        return self._data.get("col_span", 1)

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)
