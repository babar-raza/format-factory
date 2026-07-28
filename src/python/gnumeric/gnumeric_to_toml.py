"""
gnumeric_to_toml.py — Dogfood export: Gnumeric → TOML using Format Factory libraries.

Reads a Gnumeric file using Format Factory's Gnumeric codec and writes the rows
as a TOML file using Format Factory's TOML writer.

Each Gnumeric row becomes a [[rows]] array table entry in TOML.

Sprint: GNUMERIC-TO-TOML-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-GNUMERIC-TO-TOML-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path


from gnumeric.gnumeric_codec import load as load_gnumeric  # FF source reader
from toml.toml_codec import write_toml  # FF target writer


def gnumeric_to_toml(
    gnumeric_path: str | Path,
    dest_path: str | Path,
    *,
    sheet_index: int = 0,
    table_key: str = "rows",
) -> int:
    """Convert a Gnumeric file to a TOML file, one [[rows]] entry per row.

    Cell values are coerced to strings. Columns are named col_0, col_1, etc.

    Args:
        gnumeric_path: Path to the source .gnumeric file.
        dest_path: Path for the output .toml file (parent dirs created).
        sheet_index: Which sheet to export (0-based, default 0).
        table_key: Name for the TOML array table (default "rows").

    Returns:
        Number of rows written.
    """
    gnumeric_path = Path(gnumeric_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    model = load_gnumeric(gnumeric_path)  # Format Factory gnumeric reader
    sheets = model.get("sheets", [])

    toml_rows: list[dict] = []
    if sheets and sheet_index < len(sheets):
        cell_grid: dict = sheets[sheet_index].get("cell_grid", {})
        if cell_grid:
            max_row = max(r for r, c in cell_grid)
            max_col = max(c for r, c in cell_grid)
            for row_idx in range(max_row + 1):
                entry: dict[str, str] = {}
                for col_idx in range(max_col + 1):
                    entry[f"col_{col_idx}"] = str(cell_grid.get((row_idx, col_idx), ""))
                toml_rows.append(entry)

    write_toml({table_key: toml_rows}, dest_path)  # Format Factory toml writer
    return len(toml_rows)


__all__ = ["gnumeric_to_toml"]
