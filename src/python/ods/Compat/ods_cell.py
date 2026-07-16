"""OdsCell — production facade for table:table-cell (ODS cell).

Spec authority: table:table-cell
Fact ref: SAL-ODS-00474
Canonical spec class: src/python/ods/spec/table/table_cell.py::TableCell
"""
from __future__ import annotations
from typing import ClassVar

from ..spec.table.table_cell import TableCell as _SpecTableCell


class OdsCell(_SpecTableCell):
    """Production facade for table:table-cell (ODF Spreadsheet cell element)."""

    spec_qname: ClassVar[str] = "table:table-cell"
    spec_fact_ref: ClassVar[str] = "SAL-ODS-00474"
    namespace_uri: ClassVar[str] = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
