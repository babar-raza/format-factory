"""
sylk_to_toml.py — Dogfood export: SYLK → TOML using Format Factory libraries.

Reads a SYLK file using Format Factory's SYLK parser and writes the rows
as a TOML file using Format Factory's TOML writer.

Each SYLK row becomes a [[rows]] array table entry in TOML.

Sprint: SYLK-TO-TOML-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-SYLK-TO-TOML-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python" / "sylk"))

from sylk.sylk_parser import parse_sylk_strict  # FF source reader
from toml.toml_codec import write_toml  # FF target writer


def sylk_to_toml(
    sylk_path: str | Path,
    dest_path: str | Path,
    *,
    table_key: str = "rows",
) -> int:
    """Convert a SYLK file to a TOML file, one [[rows]] entry per row.

    Cell values are coerced to strings. The SYLK cell grid is rebuilt into
    row-major order. Columns are named col_0, col_1, etc.

    Args:
        sylk_path: Path to the source .slk file.
        dest_path: Path for the output .toml file (parent dirs created).
        table_key: Name for the TOML array table (default "rows").

    Returns:
        Number of rows written.
    """
    sylk_path = Path(sylk_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_sylk_strict(sylk_path)  # Format Factory sylk reader

    # Rebuild grid from sparse cell list (1-based row/col)
    grid: dict[int, dict[int, str]] = {}
    for cell in doc.cells:
        r, c = cell.row, cell.col
        grid.setdefault(r, {})[c] = str(cell.value) if cell.value is not None else ""

    toml_rows: list[dict] = []
    if grid:
        max_row = max(grid)
        max_col = max(c for row_cells in grid.values() for c in row_cells)
        for row_idx in range(1, max_row + 1):
            entry: dict[str, str] = {}
            row_cells = grid.get(row_idx, {})
            for col_idx in range(1, max_col + 1):
                entry[f"col_{col_idx - 1}"] = row_cells.get(col_idx, "")
            toml_rows.append(entry)

    write_toml({table_key: toml_rows}, dest_path)  # Format Factory toml writer
    return len(toml_rows)


__all__ = ["sylk_to_toml"]
