"""FodsTableRow — Compat facade for the FODS table:table-row element.

Spec authority: table:table-row (SAL-FODS-00005, ODF 1.3 §9.4)
Canonical spec class: src/python/fods/spec/table/table_row.py::TableRow
Qname registry: shared/qname-registry/fods.yaml (facade_names: [FodsTableRow])

TC-SP-002 (2026-06-25): facade created to satisfy Gate 11 P-ARCH-001 spec parity.
"""
from __future__ import annotations
from typing import ClassVar

from src.python.fods.spec.table.table_row import TableRow as _SpecTableRow


class FodsTableRow(_SpecTableRow):
    """ARCHITECTURE MARKER — spec_qname attribution for table:table-row (Gate 11 P-ARCH-001).

    Use fods production code for behavioral implementation.
    This class exists to satisfy Gate 11 P-ARCH-001 spec_qname traceability only.
    It inherits the canonical spec class but adds no behavioral implementation.
    TC-SP-002 disposition: PATH B (architecture marker, 2026-06-25).
    """

    spec_qname: ClassVar[str] = "table:table-row"
    spec_fact_ref: ClassVar[str] = "SAL-FODS-00005"
    namespace_uri: ClassVar[str] = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
