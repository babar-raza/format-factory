"""AbwDocument — production facade for abw:abiword.

Spec authority: abw:abiword
Spec ref: AbiWord AWML 1.0 — document root
Fact ref: FACT-ABW-001
Canonical spec class: src/python/abw/spec/document/document.py::Document
"""
from __future__ import annotations

from typing import Any

from ..spec.document.document import Document as _SpecDocument
from ..spec.document.paragraph import Paragraph as _Paragraph


class AbwDocument(_SpecDocument):
    """Production facade for abw:abiword (AbiWord document root element).

    Primary public API for AbiWord document access. Inherits structural
    metadata and core properties from the spec authority class.
    """

    spec_qname = "abw:abiword"
    spec_fact_ref = "FACT-ABW-001"
    namespace_uri = "http://www.abisource.com/awml/"

    @classmethod
    def from_file(cls, path: str) -> "AbwDocument":
        """Parse an ABW file and return an AbwDocument facade."""
        from ..abw_codec import load
        return cls(load(path))

    def paragraphs(self) -> list[_Paragraph]:
        """Return all paragraphs as Paragraph objects."""
        return [_Paragraph(text) for text in self._data.get("paragraphs", [])]

    def non_empty_paragraphs(self) -> list[_Paragraph]:
        """Return only paragraphs with non-whitespace content."""
        return [p for p in self.paragraphs() if not p.is_empty()]

    def word_count(self) -> int:
        """Return total word count across all paragraphs."""
        return sum(p.word_count for p in self.paragraphs())

    def __repr__(self) -> str:
        return (
            f"AbwDocument(sections={self.section_count}, "
            f"paragraphs={self.paragraph_count})"
        )
