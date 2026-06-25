"""FodsDateStyle — Compat facade for the FODS number:date-style element.

Spec authority: number:date-style (FACT-FODS-010, ODF 1.3 §16.27)
Canonical spec class: src/python/fods/spec/number/date_style.py::DateStyle
Qname registry: shared/qname-registry/fods.yaml (facade_names: [FodsDateStyle])

TC-SP-002 (2026-06-25): facade created to satisfy Gate 11 P-ARCH-001 spec parity.
"""
from __future__ import annotations

from src.python.fods.spec.number.date_style import DateStyle as _SpecDateStyle


class FodsDateStyle(_SpecDateStyle):
    """ARCHITECTURE MARKER — spec_qname attribution for number:date-style (Gate 11 P-ARCH-001).

    Date formatting style for cells with date values.
    Use fods production code for behavioral implementation.
    This class exists to satisfy Gate 11 P-ARCH-001 spec_qname traceability only.
    It inherits the canonical spec class but adds no behavioral implementation.
    TC-SP-002 disposition: PATH B (architecture marker, 2026-06-25).
    """

    spec_qname = "number:date-style"
    spec_fact_ref = "FACT-FODS-010"
    namespace_uri = "urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0"
