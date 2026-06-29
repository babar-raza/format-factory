"""XCF installed-workflow module for Format Factory FOSS track."""
from __future__ import annotations

from pathlib import Path

from .xcf_parser import parse_xcf


def xcf_installed_workflow(source: "str | Path") -> dict:
    """XCF installed-workflow proof: load source and return format metadata.

    Args:
        source: Path to a .xcf GIMP image file.

    Returns:
        dict with keys: format, loaded, width, height, layer_count.
    """
    model = parse_xcf(str(Path(source).resolve()))
    return {
        "format": "xcf",
        "loaded": model.get("ok", False),
        "width": model.get("width", 0),
        "height": model.get("height", 0),
        "layer_count": model.get("num_layers", 0),
    }
