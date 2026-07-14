"""
fods_to_tsv.py

Dogfood export: FODS → TSV

Converts a Flat OpenDocument Spreadsheet (.fods) file to TSV using:
  - Format Factory fods library (parse_fods) as the source reader
  - Format Factory tsv library (write_tsv) as the target writer

The first row of the selected sheet is treated as headers (if present).
Each subsequent row becomes one TSV row.

Sprint: autonomous-loop-20260621-230000-ed51041f
Authority: TASK-012 — Advance one dogfood export path
Ledger entry: R90-FODS-TO-TSV-DOGFOOD-001
"""
from __future__ import annotations

from pathlib import Path

try:
    from .parser import parse_fods  # relative — works in wheel
except ImportError:
    from fods.parser import parse_fods  # absolute — works when loaded directly


def fods_to_tsv(
    fods_path: str | Path,
    dest_path: str | Path,
    *,
    sheet_index: int = 0,
    first_row_as_headers: bool = True,
) -> tuple[int, list[str]]:
    """
    Convert a FODS spreadsheet to TSV using Format Factory writers.

    Parameters
    ----------
    fods_path:
        Path to the source .fods file.
    dest_path:
        Path to write the target .tsv file.
    sheet_index:
        0-based index of the sheet to export (default: 0).
    first_row_as_headers:
        If True, the first row is used as TSV column headers.

    Returns
    -------
    tuple[int, list[str]]
        (row_count_written, headers) — rows written (excluding header row)
        and the header list (empty if first_row_as_headers=False).
    """
    from tsv.tsv_parser import write_tsv  # lazy import — tsv may not be installed in isolated envs

    fods_path = Path(fods_path)
    dest_path = Path(dest_path)

    doc = parse_fods(str(fods_path))  # Format Factory fods reader
    sheets = doc.get("sheets", [])
    if not sheets:
        write_tsv([], dest_path)
        return 0, []

    sheet = sheets[min(sheet_index, len(sheets) - 1)]
    rows = sheet.get("rows", [])

    def _row_values(row: dict) -> list[str]:
        cells = row.get("cells", [])
        return [str(c.get("value", "") or "") for c in cells]

    if not rows:
        write_tsv([], dest_path)
        return 0, []

    all_rows = [_row_values(r) for r in rows]

    headers: list[str] = []
    data_rows: list[list[str]] = all_rows

    if first_row_as_headers and all_rows:
        headers = all_rows[0]
        data_rows = all_rows[1:]

    write_tsv(data_rows, dest_path, headers=headers if headers else None)  # FF tsv writer
    return len(data_rows), headers


__all__ = ["fods_to_tsv"]
