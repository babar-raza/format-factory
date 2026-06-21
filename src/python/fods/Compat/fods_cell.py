"""FodsCell — Production facade for the FODS table-cell element.

Spec authority: table:table-cell (FACT-FODS-006, ODF 1.3 §9.5)
Canonical spec class: src/python/fods/spec/table/table_cell.py::TableCell
Qname registry: shared/qname-registry/fods.yaml (facade_names: [FodsCell])

TC-MACH-ARCH-004 (2026-06-21): facade created to satisfy Gate 11 P-ARCH-001.
"""
from __future__ import annotations

from src.python.fods.spec.table.table_cell import TableCell as _SpecTableCell


class FodsCell(_SpecTableCell):
    """Production facade for table:table-cell (a single cell in a FODS sheet).

    Delegates to the canonical spec stub via inheritance. Represents a cell
    within table:table-row with office:value-type and office:value attributes.
    """

    spec_qname = "table:table-cell"
    spec_fact_ref = "FACT-FODS-006"
    namespace_uri = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
