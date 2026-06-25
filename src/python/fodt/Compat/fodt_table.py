"""FodtTable — Compat facade for the FODT table:table element.

Spec authority: table:table (FACT-FODT-007, ODF 1.3 §9.1)
Canonical spec class: src/python/fodt/spec/table/table.py::Table
Qname registry: shared/qname-registry/fodt.yaml (facade_names: [FodtTable])

TC-SP-005 (2026-06-25): facade created to satisfy Gate 11 P-ARCH-001 spec parity.
"""
from __future__ import annotations

from ..spec.table.table import Table as _SpecTable


class FodtTable(_SpecTable):
    """ARCHITECTURE MARKER — spec_qname attribution for table:table (Gate 11 P-ARCH-001).

    Embedded table element within FODT document body.
    TC-SP-005 disposition: PATH B (architecture marker, 2026-06-25).
    """

    spec_qname = "table:table"
    spec_fact_ref = "FACT-FODT-007"
    namespace_uri = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
