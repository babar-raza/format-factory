"""
dif_vector_iterator.py — Spec-shaped vector (row) iteration for DIF documents.

Authority: DIF specification — data vector.
Spec QName: dif:vector (urn:format:dif:1.0)
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterator

from .dif_parser import parse_dif
from .spec.table.vector import Vector


def dif_iter_vectors(source: "str | Path") -> Iterator[Vector]:
    """Yield spec-shaped Vector objects for every data row in a DIF document.

    Args:
        source: Path to a .dif Data Interchange Format file.

    Yields:
        Vector instances (spec class: dif:vector, FACT-DIF-002).
    """
    model = parse_dif(str(Path(source).resolve()))
    for row in model.get("rows", []):
        if isinstance(row, list):
            yield Vector(row)
