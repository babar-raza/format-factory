"""FodsCellCollection — navigable cell collection for a worksheet.

Spec authority: table:table-row / table:table-cell (ODF 1.3 §9.4, §9.5)
TC-W1-FODS-PY-002: Aspose-style deep navigation (FodsWorksheet → FodsCellCollection → FodsCell).
"""
from __future__ import annotations

from typing import Any, Iterator

from .fods_cell import FodsCell


class FodsCellCollection:
    """Navigable cell collection for a single worksheet.

    Supports:
      - cells[row, col]  → FodsCell at (row, col)
      - iter(cells)      → iterate all FodsCell objects in row-major order
      - len(cells)       → total cell count across all rows
    """

    def __init__(self, rows: list[dict[str, Any]]):
        self._rows = rows

    def __getitem__(self, key: tuple[int, int] | int) -> FodsCell:
        if isinstance(key, tuple):
            row_idx, col_idx = key
            row_cells = self._get_row_cells(row_idx)
            if col_idx < 0 or col_idx >= len(row_cells):
                raise IndexError(f"Column index {col_idx} out of range.")
            return FodsCell(row_cells[col_idx])
        raise TypeError(f"FodsCellCollection index must be a (row, col) tuple; got {type(key).__name__}")

    def __iter__(self) -> Iterator[FodsCell]:
        for row in self._rows:
            row_cells = row.get("cells", []) if isinstance(row, dict) else row
            for cell_data in row_cells:
                yield FodsCell(cell_data)

    def __len__(self) -> int:
        return sum(len(r.get("cells", r) if isinstance(r, dict) else r) for r in self._rows)

    def _get_row_cells(self, row_idx: int) -> list[dict[str, Any]]:
        if row_idx < 0 or row_idx >= len(self._rows):
            raise IndexError(f"Row index {row_idx} out of range.")
        row = self._rows[row_idx]
        return row.get("cells", []) if isinstance(row, dict) else row
