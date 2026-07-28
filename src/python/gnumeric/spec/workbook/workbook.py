"""
Gnumeric structural element: gnm:Workbook

Spec ref: Gnumeric XML format — Workbook root element
Fact ref: SAL-GNUMERIC-00001
QName: gnm:Workbook
Namespace: http://www.gnumeric.org/v10.dtd
Canonical class: Workbook
Facade: GnumericWorkbook
"""
from __future__ import annotations
from typing import Any, ClassVar


class Workbook:
    """Canonical spec-shaped class for gnm:Workbook."""

    spec_qname: ClassVar[str] = "gnumeric:workbook"
    spec_fact_ref: ClassVar[str] = "SAL-GNUMERIC-00001"
    namespace_uri: ClassVar[str] = "http://www.gnumeric.org/v10.dtd"
    local_name: ClassVar[str] = "Workbook"
    facade_names: ClassVar[list] = ["GnumericWorkbook"]

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @property
    def sheet_count(self) -> int:
        return int(self._data.get("sheet_count", len(self._data.get("sheets", []))))

    @property
    def cell_count(self) -> int:
        return int(self._data.get("cell_count", 0))

    @property
    def sheets(self) -> list:
        return list(self._data.get("sheets", []))

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    def __repr__(self) -> str:
        return f"Workbook(sheet_count={self.sheet_count}, cell_count={self.cell_count})"
