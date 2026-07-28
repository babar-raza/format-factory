"""FodtTableRow — Compat facade for the FODT table:table-row element.

Spec authority: table:table-row (SAL-FODT-00007, ODF 1.3 §9.1)
Canonical spec class: src/python/fodt/spec/table/table_row.py::TableRow
Qname registry: shared/qname-registry/fodt.yaml (facade_names: [FodtTableRow])

TC-SP-005 (2026-06-25): facade created to satisfy Gate 11 P-ARCH-001 spec parity.
"""
from __future__ import annotations
from typing import ClassVar

from ..spec.table.table_row import TableRow as _SpecTableRow


class FodtTableRow(_SpecTableRow):
    """ARCHITECTURE MARKER — spec_qname attribution for table:table-row (Gate 11 P-ARCH-001).

    Row within a table:table container.
    TC-SP-005 disposition: PATH B (architecture marker, 2026-06-25).
    """

    spec_qname: ClassVar[str] = "table:table-row"
    spec_fact_ref: ClassVar[str] = "SAL-FODT-00007"
    namespace_uri: ClassVar[str] = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
