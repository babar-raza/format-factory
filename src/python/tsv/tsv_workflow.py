"""
tsv_workflow.py — TSV installed-workflow proof module.

Provides tsv_installed_workflow() as a named, prefix-consistent proof function
for the Format Factory FOSS track.

Authority: IANA text/tab-separated-values
"""
from __future__ import annotations

from typing import Any

from .tsv_parser import _load_tsv_data


def tsv_installed_workflow(source: "Any") -> dict:
    """TSV installed-workflow proof: parse source and return format metadata.

    Named variant with explicit tsv_ prefix for API naming consistency
    across the Format Factory FOSS track.

    Args:
        source: TSV file path, bytes, or str content.

    Returns:
        dict with keys: format, loaded, row_count, column_count.
    """
    result = _load_tsv_data(source)
    rows = result.get("rows", [])
    headers = result.get("headers") or []
    col_count = len(headers) if headers else (len(rows[0]) if rows else 0)
    return {
        "format": "tsv",
        "loaded": True,
        "row_count": len(rows),
        "column_count": col_count,
    }
