"""
fodt_paragraph_iterator.py — Spec-shaped paragraph iteration for FODT documents.

Authority: ODF 1.3 §5.1.3 — text:p.
Spec QName: text:p (urn:oasis:names:tc:opendocument:xmlns:text:1.0)
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterator

from .parser import parse_fodt
from .spec.text.paragraph import Paragraph


def fodt_iter_paragraphs(source: "str | Path") -> Iterator[Paragraph]:
    """Yield spec-shaped Paragraph objects for every paragraph block in a FODT document.

    Args:
        source: Path to a .fodt Flat OpenDocument Text file.

    Yields:
        Paragraph instances (spec class: text:p, FACT-FODT-003).
    """
    model = parse_fodt(str(Path(source).resolve()))
    for block in model.get("blocks", []):
        if isinstance(block, dict):
            yield Paragraph(block)
