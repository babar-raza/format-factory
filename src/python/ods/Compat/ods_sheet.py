"""OdsSheet — production facade for table:table (ODS sheet).

Spec authority: table:table
Fact ref: SAL-ODS-00127
Canonical spec class: src/python/ods/spec/table/table.py::Table
"""
from __future__ import annotations
from typing import ClassVar

from ..spec.table.table import Table as _SpecTable


class OdsSheet(_SpecTable):
    """Production facade for table:table (ODF Spreadsheet sheet element)."""

    spec_qname: ClassVar[str] = "table:table"
    spec_fact_ref: ClassVar[str] = "SAL-ODS-00127"
    namespace_uri: ClassVar[str] = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
