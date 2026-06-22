"""OdtParagraph — production facade for text:p (ODT).

Spec authority: text:p
Fact ref: FACT-ODT-EX-0094
Canonical spec class: src/python/odt/spec/text/paragraph.py::Paragraph
"""
from __future__ import annotations

from ..spec.text.paragraph import Paragraph as _SpecParagraph


class OdtParagraph(_SpecParagraph):
    """Production facade for text:p (ODF Text Document paragraph element)."""

    spec_qname = "text:p"
    spec_fact_ref = "FACT-ODT-EX-0094"
    namespace_uri = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
