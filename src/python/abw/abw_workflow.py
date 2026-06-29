"""ABW installed-workflow module for Format Factory FOSS track."""
from __future__ import annotations

from pathlib import Path

from .abw_codec import load, get_paragraph_count, get_section_count


def abw_installed_workflow(source: "str | bytes | Path") -> dict:
    """ABW installed-workflow proof: load source and return format metadata.

    Args:
        source: Path to a .abw AbiWord document file.

    Returns:
        dict with keys: format, loaded, paragraph_count, section_count.
    """
    model = load(source)
    return {
        "format": "abw",
        "loaded": True,
        "paragraph_count": len(model.get("paragraphs", [])),
        "section_count": len(model.get("sections", [])),
    }
