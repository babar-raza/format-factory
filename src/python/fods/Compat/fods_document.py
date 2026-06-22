"""FodsDocument — Production facade for the FODS document root element.

Spec authority: office:document (FACT-FODS-001, ODF 1.3 §3.1)
Canonical spec class: src/python/fods/spec/office/document.py::Document
Qname registry: shared/qname-registry/fods.yaml (facade_names: [FodsDocument])

TC-MACH-ARCH-004 (2026-06-21): facade created to satisfy Gate 11 P-ARCH-001.
"""
from __future__ import annotations

from src.python.fods.spec.office.document import Document as _SpecDocument


class FodsDocument(_SpecDocument):
    """ARCHITECTURE MARKER — spec_qname attribution for office:document (Gate 11 P-ARCH-001).

    Use fods.models.FodsDocument for production (full data-handling behavior).
    This class exists to satisfy Gate 11 P-ARCH-001 spec_qname traceability only.
    It inherits the canonical spec class but adds no behavioral implementation.
    TC-ZS-004 disposition: PATH B (document-only architecture marker, 2026-06-22).
    """

    spec_qname = "office:document"
    spec_fact_ref = "FACT-FODS-001"
    namespace_uri = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
