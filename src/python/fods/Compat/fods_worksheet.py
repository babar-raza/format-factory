"""FodsWorksheet — Production facade for a FODS worksheet (table:table).

Spec authority: table:table (FACT-FODS-004, ODF 1.3 §9.1)
TC-W1-FODS-PY-002: Aspose-style deep navigation (FodsWorksheetCollection → FodsWorksheet → cells).
"""
from __future__ import annotations

from typing import Any

from .fods_cell_collection import FodsCellCollection


class FodsWorksheet:
    """Navigable worksheet facade.

    Provides:
      - name        → str
      - rows        → list of raw row dicts
      - cells       → FodsCellCollection for (row, col) navigation
      - is_visible  → bool
    """

    spec_qname = "table:table"
    spec_fact_ref = "FACT-FODS-004"

    def __init__(self, data: dict[str, Any]):
        self._data = data

    @property
    def name(self) -> str:
        return self._data.get("name", "")

    @name.setter
    def name(self, value: str) -> None:
        self._data["name"] = value

    @property
    def rows(self) -> list[dict[str, Any]]:
        return self._data.get("rows", [])

    @property
    def cells(self) -> FodsCellCollection:
        return FodsCellCollection(self.rows)

    @property
    def is_visible(self) -> bool:
        return self._data.get("display", "true").lower() != "false"

    def __repr__(self) -> str:
        return f"FodsWorksheet(name={self.name!r}, rows={len(self.rows)})"
