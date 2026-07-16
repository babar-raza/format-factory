"""OdtParagraph — production facade for text:p (ODT).

Spec authority: text:p
Fact ref: SAL-ODT-00091
Canonical spec class: src/python/odt/spec/text/paragraph.py::Paragraph
"""
from __future__ import annotations
from typing import ClassVar

from ..spec.text.paragraph import Paragraph as _SpecParagraph


class OdtParagraph(_SpecParagraph):
    """Production facade for text:p (ODF Text Document paragraph element)."""

    spec_qname: ClassVar[str] = "text:p"
    spec_fact_ref: ClassVar[str] = "SAL-ODT-00091"
    namespace_uri: ClassVar[str] = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
