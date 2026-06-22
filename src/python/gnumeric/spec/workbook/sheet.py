"""
Gnumeric structural element: gnm:Sheet

Spec ref: Gnumeric XML format — Sheet element
Fact ref: FACT-GNUMERIC-002
QName: gnm:Sheet
Namespace: http://www.gnumeric.org/v10.dtd
Canonical class: Sheet
Facade: GnumericSheet
"""
from __future__ import annotations
from typing import Any


class Sheet:
    """Canonical spec-shaped class for gnm:Sheet."""

    spec_qname = "gnm:Sheet"
    spec_fact_ref = "FACT-GNUMERIC-002"
    namespace_uri = "http://www.gnumeric.org/v10.dtd"
    local_name = "Sheet"
    facade_names = ["GnumericSheet"]

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @property
    def name(self) -> str:
        return str(self._data.get("name", ""))

    @property
    def cell_count(self) -> int:
        return int(self._data.get("cell_count", len(self._data.get("cell_values", []))))

    @property
    def cell_values(self) -> list[str]:
        return list(self._data.get("cell_values", []))

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    def __repr__(self) -> str:
        return f"Sheet(name={self.name!r}, cell_count={self.cell_count})"
