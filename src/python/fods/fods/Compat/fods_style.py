"""FodsStyle — Compat facade for the FODS style:style element.

Spec authority: style:style (FACT-FODS-009, ODF 1.3 §14.1.4)
Canonical spec class: src/python/fods/spec/style/style.py::Style
Qname registry: shared/qname-registry/fods.yaml (facade_names: [FodsStyle])

TC-SP-002 (2026-06-25): facade created to satisfy Gate 11 P-ARCH-001 spec parity.
"""
from __future__ import annotations

from src.python.fods.spec.style.style import Style as _SpecStyle


class FodsStyle(_SpecStyle):
    """ARCHITECTURE MARKER — spec_qname attribution for style:style (Gate 11 P-ARCH-001).

    Named style definition (cell style, column style, row style).
    Use fods production code for behavioral implementation.
    This class exists to satisfy Gate 11 P-ARCH-001 spec_qname traceability only.
    It inherits the canonical spec class but adds no behavioral implementation.
    TC-SP-002 disposition: PATH B (architecture marker, 2026-06-25).
    """

    spec_qname = "style:style"
    spec_fact_ref = "FACT-FODS-009"
    namespace_uri = "urn:oasis:names:tc:opendocument:xmlns:style:1.0"
