"""
tests/python/gnumeric/test_r302_gnumeric_iter_sheets.py

Sprint: ff-sprint-s302-gnumeric-sheet-iterator-20260626
Authority: Gnumeric XML format — gnm:Sheet element

Tests for gnumeric_iter_sheets() in gnumeric_sheet_iterator.py.
"""
from __future__ import annotations

from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_MINIMAL = _REPO / "samples" / "by-format" / "gnumeric" / "minimal-spreadsheet.gnumeric"
_MULTI = _REPO / "samples" / "by-format" / "gnumeric" / "multi-cell-basic.gnumeric"


class TestGnumericIterSheetsImport:
    def test_importable_from_gnumeric_sheet_iterator(self):
        from gnumeric.gnumeric_sheet_iterator import gnumeric_iter_sheets
        assert callable(gnumeric_iter_sheets)

    def test_importable_from_package(self):
        import gnumeric
        assert hasattr(gnumeric, "gnumeric_iter_sheets")


class TestGnumericIterSheetsOutput:
    def test_returns_iterator(self):
        from gnumeric.gnumeric_sheet_iterator import gnumeric_iter_sheets
        result = gnumeric_iter_sheets(str(_MINIMAL))
        assert hasattr(result, "__iter__") and hasattr(result, "__next__")

    def test_minimal_yields_sheets(self):
        from gnumeric.gnumeric_sheet_iterator import gnumeric_iter_sheets
        sheets = list(gnumeric_iter_sheets(str(_MINIMAL)))
        assert len(sheets) >= 1

    def test_sheet_type_is_spec_sheet(self):
        from gnumeric.gnumeric_sheet_iterator import gnumeric_iter_sheets
        from gnumeric.spec.workbook.sheet import Sheet
        sheets = list(gnumeric_iter_sheets(str(_MINIMAL)))
        assert all(isinstance(s, Sheet) for s in sheets)

    def test_sheet_has_spec_qname(self):
        from gnumeric.gnumeric_sheet_iterator import gnumeric_iter_sheets
        sheets = list(gnumeric_iter_sheets(str(_MINIMAL)))
        assert all(hasattr(s, "spec_qname") for s in sheets)

    def test_sheet_qname_value(self):
        from gnumeric.gnumeric_sheet_iterator import gnumeric_iter_sheets
        sheets = list(gnumeric_iter_sheets(str(_MINIMAL)))
        assert all(s.spec_qname == "gnumeric:sheet" for s in sheets)

    def test_sheet_has_name(self):
        from gnumeric.gnumeric_sheet_iterator import gnumeric_iter_sheets
        sheets = list(gnumeric_iter_sheets(str(_MINIMAL)))
        for s in sheets:
            assert isinstance(s.name, str)

    def test_sheet_has_cell_count(self):
        from gnumeric.gnumeric_sheet_iterator import gnumeric_iter_sheets
        sheets = list(gnumeric_iter_sheets(str(_MINIMAL)))
        for s in sheets:
            assert isinstance(s.cell_count, int) and s.cell_count >= 0

    def test_consistent(self):
        from gnumeric.gnumeric_sheet_iterator import gnumeric_iter_sheets
        r1 = [s.name for s in gnumeric_iter_sheets(str(_MINIMAL))]
        r2 = [s.name for s in gnumeric_iter_sheets(str(_MINIMAL))]
        assert r1 == r2
