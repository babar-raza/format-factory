"""
odt_paragraph_iterator.py — Spec-shaped paragraph iteration for ODT documents.

Authority: ODF 1.3 Part 3 §5.1.3 — text:p paragraph.
Spec QName: text:p (urn:oasis:names:tc:opendocument:xmlns:text:1.0)
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterator

from .odt_parser import parse_odt
from .spec.text.paragraph import Paragraph


def odt_iter_paragraphs(source: "str | Path") -> Iterator[Paragraph]:
    """Yield spec-shaped Paragraph objects for every paragraph in an ODT document.

    Args:
        source: Path to a .odt OpenDocument Text file.

    Yields:
        Paragraph instances (spec class: text:p, SAL-ODT-00091).
    """
    model = parse_odt(str(Path(source).resolve()))
    for para_dict in model.get("paragraphs", []):
        if isinstance(para_dict, dict):
            yield Paragraph(para_dict)
        else:
            yield Paragraph({"text": str(para_dict)})
