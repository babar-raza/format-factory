"""
tests/python/fods/test_r300_fods_iter_sheets.py

Sprint: ff-sprint-s300-fods-sheet-iterator-20260626
Authority: ODF 1.3 §9.1 — table:table

Tests for fods_iter_sheets() in fods_sheet_iterator.py.
"""
from __future__ import annotations

from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_MINIMAL = _REPO / "samples" / "by-format" / "fods" / "minimal-spreadsheet.fods"
_MULTI = _REPO / "samples" / "by-format" / "fods" / "multi-sheet-basic.fods"


class TestFodsIterSheetsImport:
    def test_importable_from_fods_sheet_iterator(self):
        from fods.fods_sheet_iterator import fods_iter_sheets
        assert callable(fods_iter_sheets)

    def test_importable_from_package(self):
        import fods
        assert hasattr(fods, "fods_iter_sheets")


class TestFodsIterSheetsOutput:
    def test_returns_iterator(self):
        from fods.fods_sheet_iterator import fods_iter_sheets
        result = fods_iter_sheets(str(_MINIMAL))
        assert hasattr(result, "__iter__") and hasattr(result, "__next__")

    def test_minimal_yields_sheets(self):
        from fods.fods_sheet_iterator import fods_iter_sheets
        sheets = list(fods_iter_sheets(str(_MINIMAL)))
        assert len(sheets) >= 1

    def test_sheet_type_is_fods_sheet(self):
        from fods.fods_sheet_iterator import fods_iter_sheets
        from fods.models import FodsSheet
        sheets = list(fods_iter_sheets(str(_MINIMAL)))
        assert all(isinstance(s, FodsSheet) for s in sheets)

    def test_sheet_has_spec_qname(self):
        from fods.fods_sheet_iterator import fods_iter_sheets
        sheets = list(fods_iter_sheets(str(_MINIMAL)))
        assert all(hasattr(s, "spec_qname") for s in sheets)

    def test_sheet_qname_value(self):
        from fods.fods_sheet_iterator import fods_iter_sheets
        sheets = list(fods_iter_sheets(str(_MINIMAL)))
        assert all(s.spec_qname == "table:table" for s in sheets)

    def test_sheet_has_name(self):
        from fods.fods_sheet_iterator import fods_iter_sheets
        sheets = list(fods_iter_sheets(str(_MINIMAL)))
        for s in sheets:
            assert isinstance(s.name, str)

    def test_sheet_has_row_count(self):
        from fods.fods_sheet_iterator import fods_iter_sheets
        sheets = list(fods_iter_sheets(str(_MINIMAL)))
        for s in sheets:
            assert isinstance(s.row_count, int) and s.row_count >= 0

    def test_multi_sheet_yields_multiple(self):
        from fods.fods_sheet_iterator import fods_iter_sheets
        sheets = list(fods_iter_sheets(str(_MULTI)))
        assert len(sheets) >= 2

    def test_consistent(self):
        from fods.fods_sheet_iterator import fods_iter_sheets
        r1 = [s.name for s in fods_iter_sheets(str(_MINIMAL))]
        r2 = [s.name for s in fods_iter_sheets(str(_MINIMAL))]
        assert r1 == r2
