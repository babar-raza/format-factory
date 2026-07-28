"""
toml_key_iterator.py — Spec-shaped key iteration for TOML documents.

Authority: TOML v1.0.0 specification.
Spec QName: toml:key (urn:format:toml:1.0)
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterator

from .toml_codec import load_toml
from .spec.table.key import Key


def toml_iter_keys(source: "str | Path") -> Iterator[Key]:
    """Yield spec-shaped Key objects for every top-level key in a TOML file.

    Args:
        source: Path to a .toml file.

    Yields:
        Key instances (spec class: toml:key, SAL-TOML-00002).
    """
    data = load_toml(str(Path(source).resolve()))
    for name, value in data.items():
        yield Key(name=name, value=value)
