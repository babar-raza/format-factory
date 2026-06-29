"""FODG installed-workflow module for Format Factory FOSS track."""
from __future__ import annotations

from pathlib import Path

from .fodg_codec import load


def fodg_installed_workflow(source: "str | bytes | Path") -> dict:
    """FODG installed-workflow proof: load source and return format metadata.

    Args:
        source: Path to a .fodg file or bytes content.

    Returns:
        dict with keys: format, loaded, page_count, shape_count.
    """
    model = load(source)
    return {
        "format": "fodg",
        "loaded": True,
        "page_count": model.get("page_count", 0),
        "shape_count": model.get("shapes_total", 0),
    }
