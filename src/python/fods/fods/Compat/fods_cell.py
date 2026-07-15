"""FodsCell — Production facade for the FODS table-cell element.

Spec authority: table:table-cell (FACT-FODS-006, ODF 1.3 §9.5)
Canonical spec class: src/python/fods/spec/table/table_cell.py::TableCell
Qname registry: shared/qname-registry/fods.yaml (facade_names: [FodsCell])

TC-MACH-ARCH-004 (2026-06-21): facade created to satisfy Gate 11 P-ARCH-001.
"""
from __future__ import annotations
from typing import ClassVar

from src.python.fods.spec.table.table_cell import TableCell as _SpecTableCell


class FodsCell(_SpecTableCell):
    """ARCHITECTURE MARKER — spec_qname attribution for table:table-cell (Gate 11 P-ARCH-001).

    Use fods.models.FodsCell for production (full data-handling behavior).
    This class exists to satisfy Gate 11 P-ARCH-001 spec_qname traceability only.
    It inherits the canonical spec class but adds no behavioral implementation.
    TC-ZS-004 disposition: PATH B (document-only architecture marker, 2026-06-22).
    """

    spec_qname: ClassVar[str] = "table:table-cell"
    spec_fact_ref: ClassVar[str] = "FACT-FODS-006"
    namespace_uri: ClassVar[str] = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
