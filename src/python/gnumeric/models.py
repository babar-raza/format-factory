"""Domain model classes for Gnumeric spreadsheet format.

Classes:
    GnumericDocument — typed wrapper over the dict returned by load()

spec_qname: gnumeric:workbook
spec_fact_ref: see shared/qname-registry/gnumeric.yaml
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


class GnumericDocument:
    """Typed domain model for a Gnumeric workbook.

    Wraps the neutral model dict returned by load().
    Neutral model keys: is_gnumeric (bool), sheet_count (int),
    sheets (list[dict]), cell_count (int).
    """

    spec_qname = "gnumeric:workbook"
    spec_fact_ref = "FACT-GNUMERIC-001"
    namespace_uri = "http://www.gnumeric.org/v10.dtd"
    local_name = "workbook"
    facade_names = []

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @classmethod
    def from_file(cls, path: str | Path) -> "GnumericDocument":
        """Load a Gnumeric file and return a GnumericDocument."""
        from .gnumeric_codec import load
        return cls(load(path))

    @property
    def sheet_count(self) -> int:
        """Number of sheets in the workbook."""
        return int(self._data.get("sheet_count", len(self._data.get("sheets", []))))

    @property
    def sheets(self) -> list[dict[str, Any]]:
        """Per-sheet data dicts in document order."""
        return list(self._data.get("sheets", []))

    @property
    def cell_count(self) -> int:
        """Total cell count across all sheets."""
        return int(self._data.get("cell_count", 0))

    @property
    def is_gnumeric(self) -> bool:
        """True if source was a valid Gnumeric file."""
        return bool(self._data.get("is_gnumeric", True))

    def get_sheet(self, index: int) -> dict[str, Any] | None:
        """Return the sheet dict at the given 0-based index, or None."""
        sheets = self._data.get("sheets", [])
        if 0 <= index < len(sheets):
            return sheets[index]
        return None

    def get_sheet_names(self) -> list[str]:
        """Return list of sheet name strings."""
        return [s.get("name", "") for s in self._data.get("sheets", [])]

    def get_cell_value(self, sheet_index: int, row: int, col: int) -> str:
        """Return a cell value string, or '' if out of bounds."""
        sheet = self.get_sheet(sheet_index)
        if sheet is None:
            return ""
        grid = sheet.get("cell_grid", {})
        return str(grid.get((row, col), ""))

    def to_dict(self) -> dict[str, Any]:
        """Return the underlying neutral model dict."""
        return dict(self._data)

    def __repr__(self) -> str:
        return (
            f"GnumericDocument(sheet_count={self.sheet_count}, "
            f"cell_count={self.cell_count})"
        )
