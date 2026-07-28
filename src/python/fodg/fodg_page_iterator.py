"""
fodg_page_iterator.py — Spec-shaped page iteration for FODG documents.

Authority: ODF 1.3 §9.1.4 — draw:page.
Spec QName: draw:page (urn:oasis:names:tc:opendocument:xmlns:drawing:1.0)
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterator

from .fodg_codec import load
from .spec.draw.page import Page


def fodg_iter_pages(source: "str | Path") -> Iterator[Page]:
    """Yield spec-shaped Page objects for every page in a FODG document.

    Args:
        source: Path to a .fodg Flat OpenDocument Drawing file.

    Yields:
        Page instances (spec class: draw:page, SAL-FODG-00414).
    """
    model = load(str(Path(source).resolve()))
    for page_dict in model.get("pages", []):
        yield Page(page_dict)
