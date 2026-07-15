"""GnumericSheet — production facade for gnm:Sheet.

Spec authority: gnm:Sheet
Fact ref: FACT-GNUMERIC-002
Canonical spec class: src/python/gnumeric/spec/workbook/sheet.py::Sheet
"""
from __future__ import annotations
from typing import ClassVar

from ..spec.workbook.sheet import Sheet as _SpecSheet


class GnumericSheet(_SpecSheet):
    """Production facade for gnm:Sheet (Gnumeric spreadsheet sheet element)."""

    spec_qname: ClassVar[str] = "gnumeric:sheet"
    spec_fact_ref: ClassVar[str] = "FACT-GNUMERIC-002"
    namespace_uri: ClassVar[str] = "http://www.gnumeric.org/v10.dtd"
