"""FODS installed-workflow module for Format Factory FOSS track."""
from __future__ import annotations

from pathlib import Path

from .parser import parse_fods


def fods_installed_workflow(source: "str | Path") -> dict:
    """FODS installed-workflow proof: load source and return format metadata.

    Args:
        source: Path to a .fods flat-XML ODS file.

    Returns:
        dict with keys: format, loaded, sheet_count.
    """
    model = parse_fods(str(Path(source).resolve()))
    return {
        "format": "fods",
        "loaded": True,
        "sheet_count": model.get("sheet_count", 0),
    }
