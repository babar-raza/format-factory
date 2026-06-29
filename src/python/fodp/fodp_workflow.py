"""FODP installed-workflow module for Format Factory FOSS track."""
from __future__ import annotations

from pathlib import Path

from .fodp_codec import load


def fodp_installed_workflow(source: "str | Path") -> dict:
    """FODP installed-workflow proof: load source and return format metadata.

    Args:
        source: Path to a .fodp presentation file.

    Returns:
        dict with keys: format, loaded, page_count, slide_count.
    """
    model = load(str(Path(source).resolve()))
    page_count = model.get("page_count", 0)
    return {
        "format": "fodp",
        "loaded": True,
        "page_count": page_count,
        "slide_count": page_count,
    }
