"""Behavioral tests for GNUMERIC spec/Compat layer (TC-PH-004)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from src.python.gnumeric.Compat import GnumericWorkbook, GnumericSheet
from src.python.gnumeric.spec.workbook.workbook import Workbook as SpecWorkbook
from src.python.gnumeric.spec.workbook.sheet import Sheet as SpecSheet


_SAMPLE_WORKBOOK = {
    "sheet_count": 2,
    "cell_count": 10,
    "sheets": [
        {"name": "Sheet1", "cell_count": 6, "cell_values": {"A1": "Hello", "B1": 42}},
        {"name": "Sheet2", "cell_count": 4, "cell_values": {}},
    ],
}
_SAMPLE_SHEET = {"name": "Sheet1", "cell_count": 6, "cell_values": {"A1": "Hello", "B1": 42}}


class TestGnumericWorkbookMetadata:
    def test_spec_qname(self):
        assert GnumericWorkbook.spec_qname == "gnm:Workbook"

    def test_spec_fact_ref(self):
        assert GnumericWorkbook.spec_fact_ref == "FACT-GNUMERIC-001"

    def test_namespace_uri_present(self):
        assert GnumericWorkbook.namespace_uri


class TestGnumericWorkbookBehavior:
    def test_instantiation(self):
        wb = GnumericWorkbook(_SAMPLE_WORKBOOK)
        assert wb is not None

    def test_sheet_count(self):
        wb = GnumericWorkbook(_SAMPLE_WORKBOOK)
        assert wb.sheet_count == 2

    def test_cell_count(self):
        wb = GnumericWorkbook(_SAMPLE_WORKBOOK)
        assert wb.cell_count == 10

    def test_to_dict(self):
        wb = GnumericWorkbook(_SAMPLE_WORKBOOK)
        d = wb.to_dict()
        assert isinstance(d, dict)

    def test_repr_nonempty(self):
        wb = GnumericWorkbook(_SAMPLE_WORKBOOK)
        assert repr(wb)

    def test_inherits_spec_class(self):
        wb = GnumericWorkbook(_SAMPLE_WORKBOOK)
        assert isinstance(wb, SpecWorkbook)


class TestGnumericSheetBehavior:
    def test_instantiation(self):
        s = GnumericSheet(_SAMPLE_SHEET)
        assert s is not None

    def test_spec_qname(self):
        assert GnumericSheet.spec_qname == "gnm:Sheet"

    def test_name_property(self):
        s = GnumericSheet(_SAMPLE_SHEET)
        assert s.name == "Sheet1"

    def test_cell_count(self):
        s = GnumericSheet(_SAMPLE_SHEET)
        assert s.cell_count == 6

    def test_inherits_spec_class(self):
        s = GnumericSheet(_SAMPLE_SHEET)
        assert isinstance(s, SpecSheet)

    def test_repr_nonempty(self):
        s = GnumericSheet(_SAMPLE_SHEET)
        assert repr(s)
