from __future__ import annotations
from typing import Any


class Table:
    """Canonical spec-shaped class for table:table in ODS context (ODF §9.1)."""

    spec_qname = "table:table"
    spec_fact_ref = "FACT-ODS-001"

    def __init__(self, data: dict[str, Any]):
        self._data = data

    @property
    def name(self) -> str:
        return self._data.get("name", "")

    @property
    def rows(self) -> list:
        return self._data.get("rows", [])

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)
