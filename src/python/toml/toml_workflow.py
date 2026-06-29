"""TOML installed-workflow module for Format Factory FOSS track."""
from __future__ import annotations

from pathlib import Path

from .toml_codec import load_toml, count_keys, list_sections


def toml_installed_workflow(source: "str | Path") -> dict:
    """TOML installed-workflow proof: load source and return format metadata.

    Args:
        source: Path to a .toml file.

    Returns:
        dict with keys: format, loaded, key_count, section_count.
    """
    data = load_toml(str(Path(source).resolve()))
    return {
        "format": "toml",
        "loaded": True,
        "key_count": count_keys(str(Path(source).resolve())),
        "section_count": len(list_sections(str(Path(source).resolve()))),
    }
