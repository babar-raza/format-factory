"""GnumericWorkbook — production facade for gnm:Workbook.

Spec authority: gnm:Workbook
Fact ref: FACT-GNUMERIC-001
Canonical spec class: src/python/gnumeric/spec/workbook/workbook.py::Workbook
"""
from __future__ import annotations
from typing import ClassVar

from ..spec.workbook.workbook import Workbook as _SpecWorkbook
from ..spec.workbook.sheet import Sheet as _Sheet


class GnumericWorkbook(_SpecWorkbook):
    """Production facade for gnm:Workbook (Gnumeric spreadsheet root element)."""

    spec_qname: ClassVar[str] = "gnumeric:workbook"
    spec_fact_ref: ClassVar[str] = "FACT-GNUMERIC-001"
    namespace_uri: ClassVar[str] = "http://www.gnumeric.org/v10.dtd"

    @classmethod
    def from_file(cls, path: str) -> "GnumericWorkbook":
        """Parse a Gnumeric file and return a GnumericWorkbook facade."""
        from ..gnumeric_codec import load
        return cls(load(path))

    def sheet_objects(self) -> list[_Sheet]:
        """Return all sheets as Sheet objects."""
        return [_Sheet(s) for s in self._data.get("sheets", [])]
