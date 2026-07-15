"""FodsWorksheet — Production facade for a FODS worksheet (table:table).

Spec authority: table:table (FACT-FODS-004, ODF 1.3 §9.1)
TC-W1-FODS-PY-002: Aspose-style deep navigation (FodsWorksheetCollection → FodsWorksheet → cells).
"""
from __future__ import annotations

from typing import Any, ClassVar

from .fods_cell_collection import FodsCellCollection


class FodsWorksheet:
    """Navigable worksheet facade.

    Provides:
      - name        → str
      - rows        → list of raw row dicts
      - cells       → FodsCellCollection for (row, col) navigation
      - is_visible  → bool
    """

    spec_qname: ClassVar[str] = "table:table"
    spec_fact_ref: ClassVar[str] = "FACT-FODS-004"

    def __init__(self, data: dict[str, Any]):
        self._data = data

    @property
    def name(self) -> str:
        """Return the worksheet name (table:name attribute)."""
        return self._data.get("name", "")

    @name.setter
    def name(self, value: str) -> None:
        """Set the worksheet name."""
        self._data["name"] = value

    @property
    def rows(self) -> list[dict[str, Any]]:
        """Return all table:table-row dicts for this worksheet."""
        return self._data.get("rows", [])

    @property
    def cells(self) -> FodsCellCollection:
        """Return the navigable cell collection for (row, col) access."""
        return FodsCellCollection(self.rows)

    @property
    def is_visible(self) -> bool:
        """Return True if the worksheet is visible (table:display != false)."""
        return self._data.get("display", "true").lower() != "false"

    def __repr__(self) -> str:
        return f"FodsWorksheet(name={self.name!r}, rows={len(self.rows)})"
