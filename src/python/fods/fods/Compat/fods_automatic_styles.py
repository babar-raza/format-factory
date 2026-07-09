"""FodsAutomaticStyles — Compat facade for the FODS office:automatic-styles element.

Spec authority: office:automatic-styles (FACT-FODS-008, ODF 1.3 §14.1)
Canonical spec class: src/python/fods/spec/office/automatic_styles.py::AutomaticStyles
Qname registry: shared/qname-registry/fods.yaml (facade_names: [FodsAutomaticStyles])

TC-SP-002 (2026-06-25): facade created to satisfy Gate 11 P-ARCH-001 spec parity.
"""
from __future__ import annotations

from src.python.fods.spec.office.automatic_styles import AutomaticStyles as _SpecAutomaticStyles


class FodsAutomaticStyles(_SpecAutomaticStyles):
    """ARCHITECTURE MARKER — spec_qname attribution for office:automatic-styles (Gate 11 P-ARCH-001).

    Container for auto-generated cell/column/row styles derived from the data.
    Use fods production code for behavioral implementation.
    This class exists to satisfy Gate 11 P-ARCH-001 spec_qname traceability only.
    It inherits the canonical spec class but adds no behavioral implementation.
    TC-SP-002 disposition: PATH B (architecture marker, 2026-06-25).
    """

    spec_qname = "office:automatic-styles"
    spec_fact_ref = "FACT-FODS-008"
    namespace_uri = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
