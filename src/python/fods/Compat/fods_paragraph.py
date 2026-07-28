"""FodsParagraph — Compat facade for the FODS text:p element.

Spec authority: text:p (SAL-FODS-00007, ODF 1.3 §5.1)
Canonical spec class: src/python/fods/spec/text/paragraph.py::Paragraph
Qname registry: shared/qname-registry/fods.yaml (facade_names: [FodsParagraph])

TC-SP-002 (2026-06-25): facade created to satisfy Gate 11 P-ARCH-001 spec parity.
"""
from __future__ import annotations
from typing import ClassVar

from src.python.fods.spec.text.paragraph import Paragraph as _SpecParagraph


class FodsParagraph(_SpecParagraph):
    """ARCHITECTURE MARKER — spec_qname attribution for text:p (Gate 11 P-ARCH-001).

    Text paragraph element within table cell content.
    Use fods production code for behavioral implementation.
    This class exists to satisfy Gate 11 P-ARCH-001 spec_qname traceability only.
    It inherits the canonical spec class but adds no behavioral implementation.
    TC-SP-002 disposition: PATH B (architecture marker, 2026-06-25).
    """

    spec_qname: ClassVar[str] = "text:p"
    spec_fact_ref: ClassVar[str] = "SAL-FODS-00007"
    namespace_uri: ClassVar[str] = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
