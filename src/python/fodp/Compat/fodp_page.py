"""FodpPage — production facade for draw:page (FODP).

Spec authority: draw:page
Fact ref: FACT-FODP-EX-0417
Canonical spec class: src/python/fodp/spec/draw/page.py::Page
"""
from __future__ import annotations

from ..spec.draw.page import Page as _SpecPage


class FodpPage(_SpecPage):
    """Production facade for draw:page (ODF Presentation slide element)."""

    spec_qname = "presentation:page"
    spec_fact_ref = "FACT-FODP-EX-0417"
    namespace_uri = "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
