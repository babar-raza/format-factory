"""ODT installed-workflow module for Format Factory FOSS track."""
from __future__ import annotations

from pathlib import Path

from .odt_parser import parse_odt


def odt_installed_workflow(source: "str | Path") -> dict:
    """ODT installed-workflow proof: load source and return format metadata.

    Args:
        source: Path to a .odt file.

    Returns:
        dict with keys: format, loaded, paragraph_count, heading_count.
    """
    model = parse_odt(str(source))
    return {
        "format": "odt",
        "loaded": True,
        "paragraph_count": model.get("paragraph_count", 0),
        "heading_count": model.get("heading_count", 0),
    }
