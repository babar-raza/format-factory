"""GnumericSheet — production facade for gnm:Sheet.

Spec authority: gnm:Sheet
Fact ref: FACT-GNUMERIC-002
Canonical spec class: src/python/gnumeric/spec/workbook/sheet.py::Sheet
"""
from __future__ import annotations

from ..spec.workbook.sheet import Sheet as _SpecSheet


class GnumericSheet(_SpecSheet):
    """Production facade for gnm:Sheet (Gnumeric spreadsheet sheet element)."""

    spec_qname = "gnm:Sheet"
    spec_fact_ref = "FACT-GNUMERIC-002"
    namespace_uri = "http://www.gnumeric.org/v10.dtd"
