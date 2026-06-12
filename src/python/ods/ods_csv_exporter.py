"""
ods_csv_exporter.py — CSV export for ODS documents.

Public API:
  export_ods_to_csv(doc, sheet_index=0) — returns CSV string (RFC 4180)
  export_ods_to_csv_file(doc, output_path, sheet_index=0) — writes CSV to file

First export capability for the ODS format. R33 deepening deliverable.
Implements RFC 4180 CSV output for a single sheet.

License: Apache-2.0
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import Any

from .ods_parser import OdsDocument, OdsCell


MAX_EXPORT_ROWS = 1048576
MAX_EXPORT_COLS = 16384


class OdsCsvExportError(Exception):
    """Raised when CSV export fails."""


def _needs_quoting(value: str) -> bool:
    """Check if a CSV field needs quoting per RFC 4180."""
    return any(c in value for c in (',', '"', '\n', '\r'))


def _quote_field(value: str) -> str:
    """Quote a CSV field per RFC 4180: double-quotes escaped as ""."""
    if _needs_quoting(value):
        escaped = value.replace('"', '""')
        return f'"{escaped}"'
    return value


def _cell_to_text(cell: OdsCell) -> str:
    """Convert an ODS cell to its text representation for CSV export."""
    if cell.value is None:
        return ""
    if isinstance(cell.value, float):
        # Avoid trailing .0 for integer values
        if cell.value == int(cell.value):
            return str(int(cell.value))
        return str(cell.value)
    return str(cell.value)


def _trim_trailing_empty(cells: list[OdsCell]) -> list[OdsCell]:
    """Remove trailing empty cells from a row."""
    end = len(cells)
    while end > 0 and not cells[end - 1].text and not cells[end - 1].value_type:
        end -= 1
    return cells[:end]


def export_ods_to_csv(
    doc: OdsDocument,
    sheet_index: int = 0,
    *,
    include_empty_rows: bool = False,
    line_ending: str = "\r\n",
) -> str:
    """Export a single ODS sheet to RFC 4180 CSV string.

    Args:
        doc: Parsed ODS document.
        sheet_index: Which sheet to export (0-based).
        include_empty_rows: If True, include rows with no data.
        line_ending: Line ending to use (default CRLF per RFC 4180).

    Returns:
        CSV string.

    Raises:
        OdsCsvExportError: If export fails.
    """
    if not doc.sheets:
        raise OdsCsvExportError("Document has no sheets")
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        raise OdsCsvExportError(
            f"Sheet index {sheet_index} out of range (0-{len(doc.sheets) - 1})"
        )

    sheet = doc.sheets[sheet_index]
    if len(sheet.rows) > MAX_EXPORT_ROWS:
        raise OdsCsvExportError(
            f"Sheet has {len(sheet.rows)} rows, exceeds export limit of {MAX_EXPORT_ROWS}"
        )

    buf = io.StringIO()
    for row in sheet.rows:
        trimmed = _trim_trailing_empty(row.cells)
        if not trimmed and not include_empty_rows:
            continue

        if len(trimmed) > MAX_EXPORT_COLS:
            raise OdsCsvExportError(
                f"Row has {len(trimmed)} columns, exceeds limit of {MAX_EXPORT_COLS}"
            )

        fields = [_quote_field(_cell_to_text(cell)) for cell in trimmed]
        buf.write(",".join(fields))
        buf.write(line_ending)

    return buf.getvalue()


def export_ods_to_csv_file(
    doc: OdsDocument,
    output_path: str | Path,
    sheet_index: int = 0,
    *,
    include_empty_rows: bool = False,
    encoding: str = "utf-8",
) -> str:
    """Export a single ODS sheet to a CSV file.

    Args:
        doc: Parsed ODS document.
        output_path: Path to write the CSV file.
        sheet_index: Which sheet to export (0-based).
        include_empty_rows: If True, include rows with no data.
        encoding: File encoding (default UTF-8).

    Returns:
        Absolute path of the written file.

    Raises:
        OdsCsvExportError: If export fails.
    """
    csv_text = export_ods_to_csv(
        doc,
        sheet_index,
        include_empty_rows=include_empty_rows,
    )
    path = Path(output_path)
    path.write_bytes(csv_text.encode(encoding))
    return str(path.resolve())


def get_csv_export_capabilities() -> dict[str, Any]:
    """Return capability declarations for ODS CSV exporter."""
    return {
        "format": "ods",
        "export_target": "csv",
        "rfc": "RFC 4180",
        "features": [
            "single_sheet_export",
            "typed_cell_values",
            "rfc4180_quoting",
            "empty_row_trimming",
            "trailing_cell_trimming",
            "configurable_line_ending",
            "file_output",
        ],
        "limitations": [
            "single_sheet_only",
            "no_formula_evaluation",
            "no_style_preservation",
            "no_merged_cell_handling",
        ],
        "max_rows": MAX_EXPORT_ROWS,
        "max_cols": MAX_EXPORT_COLS,
    }
