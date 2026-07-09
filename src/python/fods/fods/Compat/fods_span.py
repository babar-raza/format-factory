"""FodsSpan — Compat facade for the FODS text:span element.

Spec authority: text:span (FACT-FODS-007, ODF 1.3 §5.1)
Canonical spec class: src/python/fods/spec/text/span.py::Span
Qname registry: shared/qname-registry/fods.yaml (facade_names: [FodsSpan])

TC-SP-002 (2026-06-25): facade created to satisfy Gate 11 P-ARCH-001 spec parity.
"""
from __future__ import annotations

from src.python.fods.spec.text.span import Span as _SpecSpan


class FodsSpan(_SpecSpan):
    """ARCHITECTURE MARKER — spec_qname attribution for text:span (Gate 11 P-ARCH-001).

    Inline text span with style attribution within text:p elements.
    Use fods production code for behavioral implementation.
    This class exists to satisfy Gate 11 P-ARCH-001 spec_qname traceability only.
    It inherits the canonical spec class but adds no behavioral implementation.
    TC-SP-002 disposition: PATH B (architecture marker, 2026-06-25).
    """

    spec_qname = "text:span"
    spec_fact_ref = "FACT-FODS-007"
    namespace_uri = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
