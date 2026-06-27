"""
tests/python/ods/test_r296_ods_iter_sheets.py

Sprint: ff-sprint-s296-ods-sheet-iterator-20260626
Authority: ODF 1.3 Part 4 — Spreadsheet

Tests for ods_iter_sheets() in ods_sheet_iterator.py.
"""
from __future__ import annotations

from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_VALID_DIR = _REPO / "samples" / "by-format" / "ods" / "valid"
_MINIMAL = _VALID_DIR / "minimal-spreadsheet.ods"


class TestOdsIterSheetsImport:
    def test_importable_from_ods_sheet_iterator(self):
        from ods.ods_sheet_iterator import ods_iter_sheets
        assert callable(ods_iter_sheets)

    def test_importable_from_package(self):
        import ods
        assert hasattr(ods, "ods_iter_sheets")


class TestOdsIterSheetsOutput:
    def test_returns_iterator(self):
        from ods.ods_sheet_iterator import ods_iter_sheets
        result = ods_iter_sheets(str(_MINIMAL))
        assert hasattr(result, "__iter__") and hasattr(result, "__next__")

    def test_minimal_yields_sheets(self):
        from ods.ods_sheet_iterator import ods_iter_sheets
        sheets = list(ods_iter_sheets(str(_MINIMAL)))
        assert len(sheets) >= 1

    def test_sheet_type_is_spec_table(self):
        from ods.ods_sheet_iterator import ods_iter_sheets
        from ods.spec.table.table import Table
        sheets = list(ods_iter_sheets(str(_MINIMAL)))
        assert all(isinstance(s, Table) for s in sheets)

    def test_sheet_has_spec_qname(self):
        from ods.ods_sheet_iterator import ods_iter_sheets
        sheets = list(ods_iter_sheets(str(_MINIMAL)))
        assert all(hasattr(s, "spec_qname") for s in sheets)

    def test_sheet_qname_value(self):
        from ods.ods_sheet_iterator import ods_iter_sheets
        sheets = list(ods_iter_sheets(str(_MINIMAL)))
        assert all(s.spec_qname == "table:table" for s in sheets)

    def test_sheet_has_name(self):
        from ods.ods_sheet_iterator import ods_iter_sheets
        sheets = list(ods_iter_sheets(str(_MINIMAL)))
        assert all(isinstance(s.name, str) for s in sheets)

    def test_consistent(self):
        from ods.ods_sheet_iterator import ods_iter_sheets
        r1 = [s.name for s in ods_iter_sheets(str(_MINIMAL))]
        r2 = [s.name for s in ods_iter_sheets(str(_MINIMAL))]
        assert r1 == r2
