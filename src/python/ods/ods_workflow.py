"""ODS installed-workflow module for Format Factory FOSS track."""
from __future__ import annotations

from pathlib import Path

from .ods_parser import parse_ods


def ods_installed_workflow(source: "str | Path") -> dict:
    """ODS installed-workflow proof: load source and return format metadata.

    Args:
        source: Path to a .ods spreadsheet file.

    Returns:
        dict with keys: format, loaded, sheet_count, row_count.
    """
    model = parse_ods(str(Path(source).resolve()))
    sheets = model.get("sheets", [])
    total_rows = sum(s.get("row_count", 0) for s in sheets)
    return {
        "format": "ods",
        "loaded": model.get("ok", False),
        "sheet_count": model.get("sheet_count", len(sheets)),
        "row_count": total_rows,
    }
