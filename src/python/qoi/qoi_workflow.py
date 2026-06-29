"""QOI installed-workflow module for Format Factory FOSS track."""
from __future__ import annotations

from pathlib import Path

from .qoi_parser import parse_qoi


def qoi_installed_workflow(source: "str | Path") -> dict:
    """QOI installed-workflow proof: load source and return format metadata.

    Args:
        source: Path to a .qoi image file.

    Returns:
        dict with keys: format, loaded, width, height, channels, pixel_count.
    """
    model = parse_qoi(str(Path(source).resolve()))
    return {
        "format": "qoi",
        "loaded": model.get("ok", False),
        "width": model.get("width", 0),
        "height": model.get("height", 0),
        "channels": model.get("channels", 0),
        "pixel_count": model.get("pixel_count", 0),
    }
