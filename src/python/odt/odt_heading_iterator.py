"""
odt_heading_iterator.py — Spec-shaped heading iteration for ODT documents.

Authority: ODF 1.3 §5.1.2 — text:h.
Spec QName: text:h (urn:oasis:names:tc:opendocument:xmlns:text:1.0)
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterator

from .odt_parser import parse_odt
from .spec.text.heading import Heading


def odt_iter_headings(source: "str | Path") -> Iterator[Heading]:
    """Yield spec-shaped Heading objects for every heading in an ODT document.

    Args:
        source: Path to a .odt OpenDocument Text file.

    Yields:
        Heading instances (spec class: text:h, FACT-ODT-EX-0094).
    """
    model = parse_odt(str(Path(source).resolve()))
    for heading in model.get("headings", []):
        if isinstance(heading, dict):
            yield Heading(heading)
        elif isinstance(heading, str):
            yield Heading({"text": heading, "level": 1})
