"""OdtDocument — production facade for office:document (ODT).

Spec authority: office:document
Fact ref: FACT-ODT-EX-0029
Canonical spec class: src/python/odt/spec/office/document.py::Document
"""
from __future__ import annotations

from ..spec.office.document import Document as _SpecDocument
from ..spec.text.paragraph import Paragraph as _Paragraph
from ..spec.text.heading import Heading as _Heading


class OdtDocument(_SpecDocument):
    """Production facade for office:document (ODF Text Document root element)."""

    spec_qname = "office:document"
    spec_fact_ref = "FACT-ODT-EX-0029"
    namespace_uri = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"

    @classmethod
    def from_file(cls, path: str) -> "OdtDocument":
        """Parse an ODT file and return an OdtDocument facade."""
        from ..odt_parser import parse_odt
        return cls(parse_odt(path))

    def paragraph_objects(self) -> list[_Paragraph]:
        """Return all paragraphs as Paragraph objects."""
        return [_Paragraph(p) for p in self._data.get("paragraphs", [])]

    def heading_objects(self) -> list[_Heading]:
        """Return all headings as Heading objects."""
        return [_Heading(h) for h in self._data.get("headings", [])]
