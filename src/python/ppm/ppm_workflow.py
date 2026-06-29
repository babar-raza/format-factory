"""PPM installed-workflow module for Format Factory FOSS track."""
from __future__ import annotations

from pathlib import Path

from .ppm_parser import parse_ppm


def ppm_installed_workflow(source: "str | Path") -> dict:
    """PPM installed-workflow proof: load source and return format metadata.

    Args:
        source: Path to a .ppm color image file.

    Returns:
        dict with keys: format, loaded, width, height, pixel_count.
    """
    model = parse_ppm(str(Path(source).resolve()))
    return {
        "format": "ppm",
        "loaded": model.get("ok", False),
        "width": model.get("width", 0),
        "height": model.get("height", 0),
        "pixel_count": model.get("pixel_count", 0),
    }
