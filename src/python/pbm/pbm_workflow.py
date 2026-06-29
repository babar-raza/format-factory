"""PBM installed-workflow module for Format Factory FOSS track."""
from __future__ import annotations

from pathlib import Path

from .pbm_parser import parse_pbm


def pbm_installed_workflow(source: "str | Path") -> dict:
    """PBM installed-workflow proof: load source and return format metadata.

    Args:
        source: Path to a .pbm bitmap image file.

    Returns:
        dict with keys: format, loaded, width, height, pixel_count.
    """
    model = parse_pbm(str(Path(source).resolve()))
    return {
        "format": "pbm",
        "loaded": model.get("ok", False),
        "width": model.get("width", 0),
        "height": model.get("height", 0),
        "pixel_count": model.get("pixel_count", 0),
    }
