"""FodpDocument — production facade for office:document (FODP).

Spec authority: office:document
Fact ref: SAL-FODP-00031
Canonical spec class: src/python/fodp/spec/office/document.py::Document
"""
from __future__ import annotations
from typing import ClassVar

from ..spec.office.document import Document as _SpecDocument
from ..spec.draw.page import Page as _Page


class FodpDocument(_SpecDocument):
    """Production facade for office:document (ODF Presentation root element)."""

    spec_qname: ClassVar[str] = "office:document"
    spec_fact_ref: ClassVar[str] = "SAL-FODP-00031"
    namespace_uri: ClassVar[str] = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"

    @classmethod
    def from_file(cls, path: str) -> "FodpDocument":
        """Parse a FODP file and return a FodpDocument facade."""
        from ..fodp_codec import load
        return cls(load(path))

    def page_objects(self) -> list[_Page]:
        """Return all slides as Page objects."""
        return [_Page(p) for p in self._data.get("pages", [])]
