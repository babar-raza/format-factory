"""NDJSON installed-workflow module for Format Factory FOSS track."""
from __future__ import annotations

from pathlib import Path

from .ndjson_codec import load_ndjson


def ndjson_installed_workflow(source: "str | Path") -> dict:
    """NDJSON installed-workflow proof: load source and return format metadata.

    Args:
        source: Path to a .ndjson / .jsonl newline-delimited JSON file.

    Returns:
        dict with keys: format, loaded, record_count.
    """
    records = load_ndjson(str(Path(source).resolve()))
    return {
        "format": "ndjson",
        "loaded": True,
        "record_count": len(records),
    }
