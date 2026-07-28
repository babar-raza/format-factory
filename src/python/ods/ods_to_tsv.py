"""
ods_to_tsv.py — Dogfood export: ODS → TSV using Format Factory libraries.

Reads an ODS spreadsheet using Format Factory's ODS parser and writes
each data row as a TSV row using Format Factory's TSV writer.

The first row is optionally used as column headers.

Sprint: ODS-TO-TSV-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-ODS-TO-TSV-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from ods.ods_parser import parse_ods_strict  # Format Factory source reader
from tsv.tsv_parser import write_tsv  # Format Factory target writer


def _cell_to_str(cell) -> str:
    """Convert ODS cell to string."""
    if cell.text:
        return cell.text
    if cell.value is not None:
        return str(cell.value)
    return ""


def ods_to_tsv(
    ods_path: str | Path,
    dest_path: str | Path,
    *,
    sheet_index: int = 0,
    use_first_row_as_headers: bool = True,
    include_row_index: bool = False,
) -> int:
    """Convert one ODS sheet to TSV, one row per data row.

    Args:
        ods_path: Path to the source .ods file.
        dest_path: Path for the output .tsv file (parent dirs created).
        sheet_index: Zero-based index of the sheet to export (default 0).
        use_first_row_as_headers: When True, row 0 values become the TSV header.
        include_row_index: When True, adds a row_index column (0-based).

    Returns:
        Number of data rows written (not counting the header).
    """
    ods_path = Path(ods_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_ods_strict(ods_path)  # Format Factory ods reader
    if not doc.sheets or sheet_index >= len(doc.sheets):
        write_tsv([], dest_path)
        return 0

    sheet = doc.sheets[sheet_index]
    all_rows = sheet.rows
    if not all_rows:
        write_tsv([], dest_path)
        return 0

    if use_first_row_as_headers and len(all_rows) > 0:
        headers = [_cell_to_str(c) for c in all_rows[0].cells] or None
        data_rows = all_rows[1:]
    else:
        headers = None
        data_rows = all_rows

    rows: list[list[str]] = []
    for row_idx, row in enumerate(data_rows):
        row_data = [_cell_to_str(c) for c in row.cells]
        if include_row_index:
            row_data.insert(0, str(row_idx))
        rows.append(row_data)

    write_tsv(rows, dest_path, headers=headers)  # Format Factory tsv writer
    return len(rows)


__all__ = ["ods_to_tsv"]
