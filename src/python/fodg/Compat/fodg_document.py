"""FodgDocument — production facade for office:document (FODG).

Spec authority: office:document
Fact ref: SAL-FODG-00031
Canonical spec class: src/python/fodg/spec/office/document.py::Document
"""
from __future__ import annotations
from typing import ClassVar

from ..spec.office.document import Document as _SpecDocument
from ..spec.draw.page import Page as _Page


class FodgDocument(_SpecDocument):
    """Production facade for office:document (ODF Drawing root element)."""

    spec_qname: ClassVar[str] = "office:document"
    spec_fact_ref: ClassVar[str] = "SAL-FODG-00031"
    namespace_uri: ClassVar[str] = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"

    @classmethod
    def from_file(cls, path: str) -> "FodgDocument":
        """Parse a FODG file and return a FodgDocument facade."""
        from ..fodg_codec import load
        return cls(load(path))

    def page_objects(self) -> list[_Page]:
        """Return all pages as Page objects."""
        return [_Page(p) for p in self._data.get("pages", [])]
