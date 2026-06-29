"""FODT installed-workflow module for Format Factory FOSS track."""
from __future__ import annotations

from pathlib import Path

from .parser import parse_fodt


def fodt_installed_workflow(source: "str | Path") -> dict:
    """FODT installed-workflow proof: load source and return format metadata.

    Args:
        source: Path to a .fodt flat-XML ODT file.

    Returns:
        dict with keys: format, loaded, block_count, table_count.
    """
    model = parse_fodt(str(Path(source).resolve()))
    return {
        "format": "fodt",
        "loaded": True,
        "block_count": len(model.get("blocks", [])),
        "table_count": len(model.get("tables", [])),
    }
