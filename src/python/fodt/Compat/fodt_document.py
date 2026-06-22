"""FodtDocument — production facade for office:document (FODT).

Spec authority: office:document
Spec ref: ODF 1.3 §3.1
Fact ref: FACT-FODT-001
Canonical spec class: src/python/fodt/spec/office/document.py::Document
"""
from __future__ import annotations

from typing import Any

from ..spec.office.document import Document as _SpecDocument
from ..spec.text.paragraph import Paragraph as _Paragraph
from ..spec.text.heading import Heading as _Heading


class FodtDocument(_SpecDocument):
    """Production facade for office:document (FODT root element).

    Provides the primary public API for accessing FODT document content.
    Inherits structural metadata from the spec authority class.
    """

    spec_qname = "office:document"
    spec_fact_ref = "FACT-FODT-001"
    namespace_uri = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"

    @classmethod
    def from_file(cls, path: str) -> "FodtDocument":
        """Parse a FODT file and return a FodtDocument facade."""
        from ..parser import parse_fodt
        return cls(parse_fodt(path))

    def paragraphs(self) -> list[_Paragraph]:
        """Return all paragraph blocks as Paragraph objects."""
        return [_Paragraph(b) for b in self._data.get("blocks", [])
                if b.get("type") == "paragraph" or b.get("kind") == "paragraph"]

    def headings(self) -> list[_Heading]:
        """Return all heading blocks as Heading objects."""
        return [_Heading(b) for b in self._data.get("blocks", [])
                if b.get("type") == "heading" or b.get("kind") == "heading"]

    @property
    def list_count(self) -> int:
        return len(self._data.get("lists", []))
