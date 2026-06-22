"""FodsSheet — Production facade for the FODS table/sheet element.

Spec authority: table:table (FACT-FODS-004, ODF 1.3 §9.1)
Canonical spec class: src/python/fods/spec/table/table.py::Table
Qname registry: shared/qname-registry/fods.yaml (facade_names: [FodsSheet])

TC-MACH-ARCH-004 (2026-06-21): facade created to satisfy Gate 11 P-ARCH-001.
"""
from __future__ import annotations

from src.python.fods.spec.table.table import Table as _SpecTable


class FodsSheet(_SpecTable):
    """ARCHITECTURE MARKER — spec_qname attribution for table:table (Gate 11 P-ARCH-001).

    Use fods.models.FodsSheet for production (full data-handling behavior).
    This class exists to satisfy Gate 11 P-ARCH-001 spec_qname traceability only.
    It inherits the canonical spec class but adds no behavioral implementation.
    TC-ZS-004 disposition: PATH B (document-only architecture marker, 2026-06-22).
    """

    spec_qname = "table:table"
    spec_fact_ref = "FACT-FODS-004"
    namespace_uri = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
