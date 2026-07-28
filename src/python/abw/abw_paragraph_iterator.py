"""
abw_paragraph_iterator.py — Spec-shaped paragraph iteration for ABW documents.

Authority: AbiWord AWML 1.0.
Spec QName: abiword:p (http://www.abisource.com/awml/)
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterator

from .abw_codec import load
from .spec.document.paragraph import Paragraph


def abw_iter_paragraphs(source: "str | bytes | Path") -> Iterator[Paragraph]:
    """Yield spec-shaped Paragraph objects for every paragraph in an ABW document.

    Args:
        source: Path to a .abw AbiWord document file.

    Yields:
        Paragraph instances (spec class: abiword:p, SAL-ABW-00003).
    """
    model = load(source)
    for text in model.get("paragraphs", []):
        yield Paragraph(str(text))
