"""Tests for fods_all_sheets_have_data and fods_max_string_length (Sprint 37)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fods import parse_fods_strict, fods_all_sheets_have_data, fods_max_string_length
from src.python.fods.neutral_model import build_workbook

_FODS_DIR = _REPO / "samples" / "by-format" / "fods"
_MINIMAL = str(_FODS_DIR / "minimal-spreadsheet.fods")     # 1 sheet, "Hello"(5)
_MULTI = str(_FODS_DIR / "multi-sheet-basic.fods")          # 2 sheets, max string "Summary Data"(13)
_FORMULA = str(_FODS_DIR / "formula-basic.fods")            # 1 sheet, no string cells


def _make_empty_wb():
    """Build a workbook with one sheet but no cells."""
    return build_workbook(
        odf_version_attr="1.3",
        mimetype=None,
        sheets=[{"name": "Empty", "index": 0, "rows": []}],
        warnings=[],
        unsupported_features=[],
        parse_errors=[],
    )


class TestFodsAllSheetsHaveData:
    def test_return_type(self):
        wb = parse_fods_strict(_MINIMAL)
        assert isinstance(fods_all_sheets_have_data(wb), bool)

    def test_true_for_minimal(self):
        # minimal-spreadsheet.fods has 1 sheet with 1 cell
        wb = parse_fods_strict(_MINIMAL)
        assert fods_all_sheets_have_data(wb) is True

    def test_true_for_multi_sheet(self):
        # multi-sheet-basic.fods: both sheets have data
        wb = parse_fods_strict(_MULTI)
        assert fods_all_sheets_have_data(wb) is True

    def test_false_for_empty_workbook(self):
        wb = _make_empty_wb()
        assert fods_all_sheets_have_data(wb) is False

    def test_true_for_formula_file(self):
        # formula-basic.fods has cells (numeric)
        wb = parse_fods_strict(_FORMULA)
        assert fods_all_sheets_have_data(wb) is True

    def test_consistent_across_calls(self):
        wb = parse_fods_strict(_MINIMAL)
        assert fods_all_sheets_have_data(wb) == fods_all_sheets_have_data(wb)


class TestFodsMaxStringLength:
    def test_return_type(self):
        wb = parse_fods_strict(_MINIMAL)
        assert isinstance(fods_max_string_length(wb), int)

    def test_exact_5_for_minimal(self):
        # minimal-spreadsheet.fods: string cell "Hello" -> len=5
        wb = parse_fods_strict(_MINIMAL)
        assert fods_max_string_length(wb) == 5

    def test_exact_13_for_multi_sheet(self):
        # multi-sheet-basic.fods: longest string is "Summary Data" (13 chars) or "Data" etc
        wb = parse_fods_strict(_MULTI)
        assert fods_max_string_length(wb) == 13

    def test_zero_for_formula_file(self):
        # formula-basic.fods: no string cells -> 0
        wb = parse_fods_strict(_FORMULA)
        assert fods_max_string_length(wb) == 0

    def test_zero_for_empty_workbook(self):
        wb = _make_empty_wb()
        assert fods_max_string_length(wb) == 0

    def test_nonnegative(self):
        wb = parse_fods_strict(_MINIMAL)
        assert fods_max_string_length(wb) >= 0

    def test_consistent_across_calls(self):
        wb = parse_fods_strict(_MINIMAL)
        assert fods_max_string_length(wb) == fods_max_string_length(wb)
