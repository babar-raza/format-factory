"""FodpPage — production facade for draw:page (FODP).

Spec authority: draw:page
Fact ref: SAL-FODP-00414
Canonical spec class: src/python/fodp/spec/draw/page.py::Page
"""
from __future__ import annotations
from typing import ClassVar

from ..spec.draw.page import Page as _SpecPage


class FodpPage(_SpecPage):
    """Production facade for draw:page (ODF Presentation slide element)."""

    spec_qname: ClassVar[str] = "presentation:page"
    spec_fact_ref: ClassVar[str] = "SAL-FODP-00414"
    namespace_uri: ClassVar[str] = "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
