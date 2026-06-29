"""PGM installed-workflow module for Format Factory FOSS track."""
from __future__ import annotations

from pathlib import Path

from .pgm_parser import parse_pgm


def pgm_installed_workflow(source: "str | Path") -> dict:
    """PGM installed-workflow proof: load source and return format metadata.

    Args:
        source: Path to a .pgm grayscale image file.

    Returns:
        dict with keys: format, loaded, width, height, pixel_count.
    """
    model = parse_pgm(str(Path(source).resolve()))
    return {
        "format": "pgm",
        "loaded": model.get("ok", False),
        "width": model.get("width", 0),
        "height": model.get("height", 0),
        "pixel_count": model.get("pixel_count", 0),
    }
