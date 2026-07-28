"""ABW spec Section — canonical implementation of abw:section.

spec_qname: abw:section
spec_fact_ref: SAL-ABW-00002
Spec ref: AbiWord AWML 1.0 — section block element
Facade: AbwSection is not a separate Compat class; sections are accessed
        via Document.section_count and the flat paragraph list.
"""
from __future__ import annotations

from typing import Any, ClassVar

from .paragraph import Paragraph


class Section:
    """Canonical implementation of the abw:section element.

    A section groups paragraphs. The neutral model stores a flat paragraph
    list, so Section wraps a named slice of that list.
    """

    spec_qname: ClassVar[str] = "abiword:section"
    spec_fact_ref: ClassVar[str] = "SAL-ABW-00002"
    namespace_uri: ClassVar[str] = "http://www.abisource.com/awml/"
    local_name: ClassVar[str] = "section"
    facade_names: ClassVar[list] = []

    def __init__(self, paragraphs: list[str], index: int = 0):
        self._paragraphs = list(paragraphs)
        self._index = index

    @property
    def index(self) -> int:
        return self._index

    @property
    def paragraph_count(self) -> int:
        return len(self._paragraphs)

    @property
    def paragraphs(self) -> list[str]:
        return list(self._paragraphs)

    def paragraph_objects(self) -> list[Paragraph]:
        return [Paragraph(text) for text in self._paragraphs]

    def is_empty(self) -> bool:
        return all(not p.strip() for p in self._paragraphs)

    def to_dict(self) -> dict[str, Any]:
        return {"index": self._index, "paragraphs": self._paragraphs}

    def __repr__(self) -> str:
        return f"Section(index={self._index}, paragraph_count={self.paragraph_count})"
