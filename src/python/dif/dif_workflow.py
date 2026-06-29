"""DIF installed-workflow module for Format Factory FOSS track."""
from __future__ import annotations

from pathlib import Path

from .dif_parser import parse_dif


def dif_installed_workflow(source: "str | Path") -> dict:
    """DIF installed-workflow proof: load source and return format metadata.

    Args:
        source: Path to a .dif file.

    Returns:
        dict with keys: format, loaded, row_count, column_count.
    """
    model = parse_dif(str(Path(source).resolve()))
    return {
        "format": "dif",
        "loaded": model.get("ok", False),
        "row_count": model.get("tuples", 0),
        "column_count": model.get("vectors", 0),
    }
