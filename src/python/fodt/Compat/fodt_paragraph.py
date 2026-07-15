"""FodtParagraph — production facade for text:p (FODT).

Spec authority: text:p
Spec ref: ODF 1.3 §5.1.3
Fact ref: FACT-FODT-003
Canonical spec class: src/python/fodt/spec/text/paragraph.py::Paragraph
"""
from __future__ import annotations
from typing import ClassVar

from ..spec.text.paragraph import Paragraph as _SpecParagraph


class FodtParagraph(_SpecParagraph):
    """Production facade for text:p (FODT paragraph element).

    Inherits all behavioral properties from the canonical spec class.
    Primary public API entry point for paragraph access.
    """

    spec_qname: ClassVar[str] = "text:p"
    spec_fact_ref: ClassVar[str] = "FACT-FODT-003"
    namespace_uri: ClassVar[str] = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
