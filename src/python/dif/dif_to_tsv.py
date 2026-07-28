"""
dif_to_tsv.py — Dogfood export: DIF → TSV using Format Factory libraries.

Reads a DIF (Data Interchange Format) file using Format Factory's DIF parser
and writes each row as a TSV row using Format Factory's TSV writer.

Each DIF data row becomes one TSV row. Column keys are always col_0, col_1, ...
since DIF has no native header concept.

Sprint: DIF-TO-TSV-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-DIF-TO-TSV-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from dif.dif_parser import parse_dif_strict  # Format Factory source reader
from tsv.tsv_parser import write_tsv  # Format Factory target writer


def dif_to_tsv(
    dif_path: str | Path,
    dest_path: str | Path,
    *,
    include_row_index: bool = False,
) -> int:
    """Convert a DIF file to TSV, one row per data row.

    Each DIF row becomes one TSV row with tab-delimited cell values.
    No header row is written (DIF has no native headers).

    Args:
        dif_path: Path to the source .dif file.
        dest_path: Path for the output .tsv file (parent dirs created).
        include_row_index: When True, prepends a row_index column (0-based).

    Returns:
        Number of data rows written.
    """
    dif_path = Path(dif_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_dif_strict(dif_path)  # Format Factory dif reader

    rows: list[list[str]] = []
    for row_idx, dif_row in enumerate(doc.rows):
        row: list[str] = []
        if include_row_index:
            row.append(str(row_idx))
        for cell in dif_row:
            row.append("" if cell.value is None else str(cell.value))
        rows.append(row)

    write_tsv(rows, dest_path)  # Format Factory tsv writer (no header for DIF)
    return len(rows)


__all__ = ["dif_to_tsv"]
