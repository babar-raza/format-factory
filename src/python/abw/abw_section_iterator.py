"""
abw_section_iterator.py — Spec-shaped section iteration for ABW documents.

Authority: AbiWord AWML 1.0 — section block element.
Spec QName: abiword:section (http://www.abisource.com/awml/)
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterator

from .abw_codec import load
from .spec.document.section import Section


def abw_iter_sections(source: "str | Path") -> Iterator[Section]:
    """Yield spec-shaped Section objects for every section in an ABW document.

    The ABW neutral model stores a flat paragraph list with a section_count.
    All paragraphs are grouped into one Section per the document's section count.

    Args:
        source: Path to a .abw AbiWord document file.

    Yields:
        Section instances (spec class: abiword:section, FACT-ABW-002).
    """
    model = load(str(Path(source).resolve()))
    paragraphs = model.get("paragraphs", [])
    section_count = model.get("section_count", 1) or 1
    # Distribute paragraphs evenly across sections
    chunk_size = max(1, (len(paragraphs) + section_count - 1) // section_count)
    for i in range(section_count):
        section_paras = paragraphs[i * chunk_size:(i + 1) * chunk_size]
        yield Section(section_paras, index=i)
