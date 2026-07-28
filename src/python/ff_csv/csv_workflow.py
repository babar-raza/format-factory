"""
csv_workflow.py — CSV installed-workflow proof module.

Provides csv_installed_workflow() as a named, prefix-consistent proof function
for the Format Factory FOSS track.

Authority: RFC 4180 (IETF) — Common Format and MIME Type for CSV Files
"""
from __future__ import annotations

import tempfile
import os
from typing import Any

from .csv_parser import parse_csv


def csv_installed_workflow(source: "Any") -> dict:
    """CSV installed-workflow proof: parse source and return format metadata.

    Named variant with explicit csv_ prefix for API naming consistency
    across the Format Factory FOSS track.

    Args:
        source: CSV file path, bytes, or str content.

    Returns:
        dict with keys: format, loaded, row_count, column_count.
    """
    if isinstance(source, (bytes, bytearray)):
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="wb") as tmp:
            tmp.write(source)
            tmp_path = tmp.name
        try:
            result = parse_csv(tmp_path)
        finally:
            os.unlink(tmp_path)
    else:
        result = parse_csv(source)
    rows = result.get("rows", [])
    headers = result.get("headers") or []
    col_count = len(headers) if headers else (len(rows[0]) if rows else 0)
    return {
        "format": "csv",
        "loaded": True,
        "row_count": len(rows),
        "column_count": col_count,
    }
