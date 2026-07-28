"""
tsv_field_iterator.py — Spec-shaped field iteration for TSV documents.

Authority: IANA text/tab-separated-values — field value.
Spec QName: tsv:field (urn:iana:media-type:text:tab-separated-values)
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterator

from .tsv_parser import parse_tsv_strict
from .spec.record.field import Field


def tsv_iter_fields(source: "str | Path") -> Iterator[Field]:
    """Yield spec-shaped Field objects for every field in a TSV document.

    Yields all fields from all rows (including header row if present) in order.

    Args:
        source: Path to a .tsv Tab-Separated Values file.

    Yields:
        Field instances (spec class: tsv:field, SAL-TSV-00002).
    """
    doc = parse_tsv_strict(str(Path(source).resolve()))
    headers = doc.get("headers", [])
    if headers:
        for h in headers:
            yield Field(str(h))
    for row in doc.get("rows", []):
        for value in row:
            yield Field(str(value))
