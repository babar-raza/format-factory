"""FodgPage — production facade for draw:page (FODG).

Spec authority: draw:page
Fact ref: FACT-FODG-EX-0417
Canonical spec class: src/python/fodg/spec/draw/page.py::Page
"""
from __future__ import annotations

from ..spec.draw.page import Page as _SpecPage


class FodgPage(_SpecPage):
    """Production facade for draw:page (ODF Drawing page element)."""

    spec_qname = "draw:page"
    spec_fact_ref = "FACT-FODG-EX-0417"
    namespace_uri = "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
