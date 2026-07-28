"""FodtTableCell — production facade for table:table-cell (FODT).

Spec authority: table:table-cell
Spec ref: ODF 1.3 §9.5
Fact ref: SAL-FODT-00007
Canonical spec class: src/python/fodt/spec/table/table_cell.py::TableCell
"""
from __future__ import annotations
from typing import ClassVar

from ..spec.table.table_cell import TableCell as _SpecTableCell


class FodtTableCell(_SpecTableCell):
    """Production facade for table:table-cell (FODT table cell element).

    Inherits all behavioral properties from the canonical spec class.
    """

    spec_qname: ClassVar[str] = "table:table-cell"
    spec_fact_ref: ClassVar[str] = "SAL-FODT-00007"
    namespace_uri: ClassVar[str] = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
