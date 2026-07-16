"""FodgPage — production facade for draw:page (FODG).

Spec authority: draw:page
Fact ref: SAL-FODG-00414
Canonical spec class: src/python/fodg/spec/draw/page.py::Page
"""
from __future__ import annotations
from typing import ClassVar

from ..spec.draw.page import Page as _SpecPage


class FodgPage(_SpecPage):
    """Production facade for draw:page (ODF Drawing page element)."""

    spec_qname: ClassVar[str] = "draw:page"
    spec_fact_ref: ClassVar[str] = "SAL-FODG-00414"
    namespace_uri: ClassVar[str] = "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
