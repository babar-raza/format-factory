"""
toml_table_iterator.py — Spec-shaped table iteration for TOML documents.

Authority: TOML v1.0.0 — Tables.
Spec QName: toml:table (urn:format:toml:1.0)
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterator

from .toml_codec import load_toml
from .spec.table.table import Table


def toml_iter_tables(source: "str | Path") -> Iterator[Table]:
    """Yield spec-shaped Table objects for every top-level table in a TOML document.

    Only dict-valued top-level keys (tables/sections) are yielded.

    Args:
        source: Path to a .toml TOML file.

    Yields:
        Table instances (spec class: toml:table, SAL-TOML-00001).
    """
    data = load_toml(str(Path(source).resolve()))
    content = data.get("data", data)
    if isinstance(content, dict):
        for value in content.values():
            if isinstance(value, dict):
                yield Table(value)
