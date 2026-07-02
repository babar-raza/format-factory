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

    # Workbook dimension properties (FACT-GNUMERIC-001)

    @property
    def is_empty(self) -> bool:
        """True if the workbook has no cells."""
        return self.cell_count == 0

    @property
    def is_single_sheet(self) -> bool:
        """True if the workbook has exactly one sheet."""
        return self.sheet_count == 1

    @property
    def is_multi_sheet(self) -> bool:
        """True if the workbook has more than one sheet."""
        return self.sheet_count > 1

    @property
    def has_cells(self) -> bool:
        """True if the workbook contains at least one cell."""
        return self.cell_count > 0

    @property
    def avg_cells_per_sheet(self) -> float:
        """Average number of cells per sheet. Returns 0.0 if no sheets."""
        if self.sheet_count == 0:
            return 0.0
        return self.cell_count / self.sheet_count

    @property
    def is_sparse(self) -> bool:
        """True if the workbook has sheets but no cells."""
        return self.sheet_count > 0 and self.cell_count == 0

    # Workbook scale properties (FACT-GNUMERIC-001 R1231)

    @property
    def is_large_workbook(self) -> bool:
        """True if cell_count > 10000."""
        return self.cell_count > 10000

    @property
    def has_many_sheets(self) -> bool:
        """True if sheet_count > 5."""
        return self.sheet_count > 5

    @property
    def is_cell_dense(self) -> bool:
        """True if avg_cells_per_sheet > 1000."""
        return self.avg_cells_per_sheet > 1000

    # Metadata and content properties (FACT-GNUMERIC-001 R1248)

    @property
    def sheet_names(self) -> list[str]:
        """Names of all sheets in document order."""
        return [s.get("name", "") for s in self._data.get("sheets", [])]

    @property
    def max_cells_per_sheet(self) -> int:
        """Maximum cell count in any single sheet; 0 if no sheets."""
        sheets = self._data.get("sheets", [])
        if not sheets:
            return 0
        return max(len(s.get("cell_grid", {})) for s in sheets)

    @property
    def is_valid(self) -> bool:
        """True if source was a valid Gnumeric file (alias for is_gnumeric)."""
        return self.is_gnumeric

    # Cell distribution properties (FACT-GNUMERIC-001 R1268)

    @property
    def min_cells_per_sheet(self) -> int:
        """Minimum cell count in any single sheet; 0 if no sheets."""
        sheets = self._data.get("sheets", [])
        if not sheets:
            return 0
        return min(len(s.get("cell_grid", {})) for s in sheets)

    @property
    def cell_count_range(self) -> int:
        """max_cells_per_sheet - min_cells_per_sheet; 0 if no sheets."""
        sheets = self._data.get("sheets", [])
        if not sheets:
            return 0
        counts = [len(s.get("cell_grid", {})) for s in sheets]
        return max(counts) - min(counts)

    @property
    def has_uniform_cell_distribution(self) -> bool:
        """True if all sheets have the same cell count."""
        sheets = self._data.get("sheets", [])
        if not sheets:
            return True
        counts = [len(s.get("cell_grid", {})) for s in sheets]
        return len(set(counts)) == 1

    # Sheet richness and variance properties (FACT-GNUMERIC-001 R1284)

    @property
    def is_data_rich(self) -> bool:
        """True if avg_cells_per_sheet > 500."""
        return self.avg_cells_per_sheet > 500

    @property
    def sheet_cell_variance(self) -> float:
        """cell_count_range / max_cells_per_sheet; 0.0 if max=0."""
        mx = self.max_cells_per_sheet
        if mx == 0:
            return 0.0
        return self.cell_count_range / mx

    @property
    def has_large_sheets(self) -> bool:
        """True if max_cells_per_sheet > 1000."""
        return self.max_cells_per_sheet > 1000

    def to_dict(self) -> dict[str, Any]:
        """Return the underlying neutral model dict."""
        return dict(self._data)

    def __repr__(self) -> str:
        return (
            f"GnumericDocument(sheet_count={self.sheet_count}, "
            f"cell_count={self.cell_count})"
        )
