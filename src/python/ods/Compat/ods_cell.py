"""OdsCell — production facade for table:table-cell (ODS cell).

Spec authority: table:table-cell
Fact ref: FACT-ODS-EX-0479
Canonical spec class: src/python/ods/spec/table/table_cell.py::TableCell
"""
from __future__ import annotations

from ..spec.table.table_cell import TableCell as _SpecTableCell


class OdsCell(_SpecTableCell):
    """Production facade for table:table-cell (ODF Spreadsheet cell element)."""

    spec_qname = "table:table-cell"
    spec_fact_ref = "FACT-ODS-EX-0479"
    namespace_uri = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
