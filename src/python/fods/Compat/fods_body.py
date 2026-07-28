"""FodsBody — Compat facade for the FODS office:body element.

Spec authority: office:body (SAL-FODS-00002, ODF 1.3 §3.3)
Canonical spec class: src/python/fods/spec/office/body.py::Body
Qname registry: shared/qname-registry/fods.yaml (facade_names: [FodsBody])

TC-SP-002 (2026-06-25): facade created to satisfy Gate 11 P-ARCH-001 spec parity.
"""
from __future__ import annotations
from typing import ClassVar

from src.python.fods.spec.office.body import Body as _SpecBody


class FodsBody(_SpecBody):
    """ARCHITECTURE MARKER — spec_qname attribution for office:body (Gate 11 P-ARCH-001).

    Use fods production code for behavioral implementation.
    This class exists to satisfy Gate 11 P-ARCH-001 spec_qname traceability only.
    It inherits the canonical spec class but adds no behavioral implementation.
    TC-SP-002 disposition: PATH B (architecture marker, 2026-06-25).
    """

    spec_qname: ClassVar[str] = "office:body"
    spec_fact_ref: ClassVar[str] = "SAL-FODS-00002"
    namespace_uri: ClassVar[str] = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
