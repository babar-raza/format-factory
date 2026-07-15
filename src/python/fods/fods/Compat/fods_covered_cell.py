"""FodsCoveredCell — Compat facade for the FODS table:covered-table-cell element.

Spec authority: table:covered-table-cell (FACT-FODS-023, ODF 1.3 §9.5.2)
Canonical spec class: src/python/fods/spec/table/covered_table_cell.py::CoveredTableCell
Qname registry: shared/qname-registry/fods.yaml (facade_names: [FodsCoveredCell])

TC-SP-002 (2026-06-25): facade created to satisfy Gate 11 P-ARCH-001 spec parity.
"""
from __future__ import annotations
from typing import ClassVar

from src.python.fods.spec.table.covered_table_cell import CoveredTableCell as _SpecCoveredTableCell


class FodsCoveredCell(_SpecCoveredTableCell):
    """ARCHITECTURE MARKER — spec_qname attribution for table:covered-table-cell (Gate 11 P-ARCH-001).

    Marker element for cells covered by a spanning table:table-cell element.
    Use fods production code for behavioral implementation.
    This class exists to satisfy Gate 11 P-ARCH-001 spec_qname traceability only.
    It inherits the canonical spec class but adds no behavioral implementation.
    TC-SP-002 disposition: PATH B (architecture marker, 2026-06-25).
    """

    spec_qname: ClassVar[str] = "table:covered-table-cell"
    spec_fact_ref: ClassVar[str] = "FACT-FODS-023"
    namespace_uri: ClassVar[str] = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
