"""
fodp_slide_iterator.py — Spec-shaped slide iteration for FODP presentations.

Authority: ODF 1.3 §9.1.4 — draw:page (presentation slide).
Spec QName: presentation:page
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterator

from .fodp_codec import load
from .spec.draw.page import Page


def fodp_iter_slides(source: "str | Path") -> Iterator[Page]:
    """Yield spec-shaped Page objects for every slide in a FODP presentation.

    Args:
        source: Path to a .fodp Flat OpenDocument Presentation file.

    Yields:
        Page instances (spec class: presentation:page, SAL-FODP-00414).
    """
    model = load(str(Path(source).resolve()))
    for page_dict in model.get("pages", []):
        yield Page(page_dict)
