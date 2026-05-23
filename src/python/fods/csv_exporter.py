"""
csv_exporter.py -- CSV export for FODS workbooks.

Public API:
  export_fods_to_csv(workbook, sheet_index=0) -- returns CSV string (RFC 4180)
  export_fods_to_csv_file(workbook, output_path, sheet_index=0) -- writes CSV to file

Export path for the Python FOSS FODS package. Converts a parsed neutral model workbook
(or a raw dict from parse_fods) to RFC 4180 CSV for a single sheet.

R50 MT6 deliverable: export dogfooding quick wins.

License: Apache-2.0
Package: format-factory-fods v0.1.0
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


MAX_EXPORT_ROWS = 1048576
MAX_EXPORT_COLS = 16384


def _rfc4180_field(value: str) -> str:
    """Quote a CSV field per RFC 4180 if it contains comma, newline, or double-quote."""
    if "," in value or "\n" in value or "\r" in value or '"' in value:
        return '"' + value.replace('"', '""') + '"'
    return value


class FodsCsvExportError(Exception):
    """Raised when FODS CSV export fails."""


def _cell_to_text(cell: dict[str, Any]) -> str:
    """Convert a neutral model cell dict to its text representation for CSV."""
    # Prefer text_content (display value) over raw value
    text = cell.get("text_content", "")
    if text:
        return str(text)
    raw = cell.get("value")
    if raw is None:
        return ""
    if isinstance(raw, float):
        # Avoid trailing .0 for integer float values
        if raw == int(raw) and abs(raw) < 1e15:
            return str(int(raw))
        return str(raw)
    return str(raw)


def export_fods_to_csv(
    workbook: dict[str, Any],
    sheet_index: int = 0,
) -> str:
    """Export a FODS workbook (neutral model dict) to a CSV string.

    Exports a single sheet identified by sheet_index (default: 0, i.e. first sheet).
    Uses RFC 4180 CSV format with CRLF line endings.

    Args:
        workbook: Neutral model dict from parse_fods() or workbook_to_xml().
                  Must have a 'sheets' list key.
        sheet_index: Zero-based index of the sheet to export. Default 0.

    Returns:
        RFC 4180 CSV string with CRLF line endings.

    Raises:
        FodsCsvExportError: If workbook format is invalid or sheet_index is out of range.
    """
    if not isinstance(workbook, dict):
        raise FodsCsvExportError(f"workbook must be a dict, got {type(workbook).__name__}")

    sheets = workbook.get("sheets", [])
    if not isinstance(sheets, list):
        raise FodsCsvExportError("workbook['sheets'] must be a list")

    if not sheets:
        raise FodsCsvExportError("workbook has no sheets")

    if sheet_index < 0 or sheet_index >= len(sheets):
        raise FodsCsvExportError(
            f"sheet_index {sheet_index} out of range (workbook has {len(sheets)} sheet(s))"
        )

    sheet = sheets[sheet_index]
    rows = sheet.get("rows", [])

    if len(rows) > MAX_EXPORT_ROWS:
        raise FodsCsvExportError(
            f"Sheet has {len(rows)} rows, exceeding export limit {MAX_EXPORT_ROWS}"
        )

    lines: list[str] = []
    for row in rows:
        cells = row.get("cells", [])
        if len(cells) > MAX_EXPORT_COLS:
            raise FodsCsvExportError(
                f"Row has {len(cells)} cells, exceeding export limit {MAX_EXPORT_COLS}"
            )
        row_values = [_cell_to_text(c) for c in cells]
        lines.append(",".join(_rfc4180_field(v) for v in row_values))

    return "\r\n".join(lines) + ("\r\n" if lines else "")


def export_fods_to_csv_file(
    workbook: dict[str, Any],
    output_path: str | Path,
    sheet_index: int = 0,
) -> None:
    """Export a FODS workbook sheet to a CSV file.

    Args:
        workbook: Neutral model dict from parse_fods().
        output_path: Destination path for the .csv file.
        sheet_index: Zero-based sheet index to export. Default 0.
    """
    csv_content = export_fods_to_csv(workbook, sheet_index=sheet_index)
    Path(output_path).write_text(csv_content, encoding="utf-8", newline="")
