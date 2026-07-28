"""
sylk_to_tsv.py — Dogfood export: SYLK → TSV using Format Factory libraries.

Reads a SYLK (Symbolic Link) spreadsheet using Format Factory's SYLK parser
and writes each data row as a TSV row using Format Factory's TSV writer.

SYLK uses 1-based (row, col) cell coordinates. The first row is optionally
used as column headers; otherwise no header row is written.

Sprint: SYLK-TO-TSV-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-SYLK-TO-TSV-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from sylk.sylk_parser import parse_sylk_strict  # Format Factory source reader
from tsv.tsv_parser import write_tsv  # Format Factory target writer


def sylk_to_tsv(
    sylk_path: str | Path,
    dest_path: str | Path,
    *,
    use_first_row_as_headers: bool = True,
    include_row_index: bool = False,
) -> int:
    """Convert a SYLK file to TSV, one row per data row.

    SYLK cells use 1-based (row, col) coordinates. When use_first_row_as_headers
    is True, row 1 values become the TSV header row.

    Args:
        sylk_path: Path to the source .slk file.
        dest_path: Path for the output .tsv file (parent dirs created).
        use_first_row_as_headers: When True, row 1 values become the TSV header.
        include_row_index: When True, prepends a row_index column (1-based SYLK row).

    Returns:
        Number of data rows written (not counting the header).
    """
    sylk_path = Path(sylk_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_sylk_strict(sylk_path)  # Format Factory sylk reader

    if not doc.cells:
        write_tsv([], dest_path)
        return 0

    max_row = max(c.row for c in doc.cells)
    max_col = max(c.col for c in doc.cells)

    # Build grid indexed by (row, col) — 1-based
    grid = {(cell.row, cell.col): ("" if cell.value is None else str(cell.value)) for cell in doc.cells}

    all_rows = {
        row_idx: [grid.get((row_idx, col_idx), "") for col_idx in range(1, max_col + 1)]
        for row_idx in range(1, max_row + 1)
    }

    if use_first_row_as_headers and all_rows:
        headers = all_rows[1]
        data_row_indices = sorted(k for k in all_rows if k > 1)
    else:
        headers = None
        data_row_indices = sorted(all_rows.keys())

    rows: list[list[str]] = []
    for row_idx in data_row_indices:
        row: list[str] = []
        if include_row_index:
            row.append(str(row_idx))
        row.extend(all_rows[row_idx])
        rows.append(row)

    write_tsv(rows, dest_path, headers=headers)  # Format Factory tsv writer
    return len(rows)


__all__ = ["sylk_to_tsv"]
