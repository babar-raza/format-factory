"""SYLK installed-workflow module for Format Factory FOSS track."""
from __future__ import annotations

from pathlib import Path

from .sylk_parser import parse_sylk, get_row_count, get_column_count, get_cell_count


def sylk_installed_workflow(source: "str | bytes | Path") -> dict:
    """SYLK installed-workflow proof: load source and return format metadata.

    Args:
        source: Path to a .slk file or bytes content.

    Returns:
        dict with keys: format, loaded, row_count, column_count, cell_count.
    """
    import tempfile
    import os

    if isinstance(source, (bytes, bytearray)):
        with tempfile.NamedTemporaryFile(suffix=".slk", delete=False, mode="wb") as tmp:
            tmp.write(source)
            tmp_path = tmp.name
        try:
            model = parse_sylk(tmp_path)
            rows = get_row_count(tmp_path)
            cols = get_column_count(tmp_path)
            cells = get_cell_count(tmp_path)
        finally:
            os.unlink(tmp_path)
    else:
        model = parse_sylk(str(source))
        rows = get_row_count(str(source))
        cols = get_column_count(str(source))
        cells = get_cell_count(str(source))

    return {
        "format": "sylk",
        "loaded": True,
        "row_count": rows,
        "column_count": cols,
        "cell_count": cells,
    }
