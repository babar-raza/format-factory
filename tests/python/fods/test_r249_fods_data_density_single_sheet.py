"""Tests for fods_data_density and fods_is_single_sheet (Sprint 39).

Closes:
  GAP-FODS-FOSS-FODS_DATA_DE-001 (Fods Data Density)
  GAP-FODS-FOSS-FODS_IS_SING-001 (Fods Is Single Sheet)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fods import parse_fods_strict, fods_data_density, fods_is_single_sheet
from src.python.fods.neutral_model import build_workbook

_FODS_DIR = _REPO / "samples" / "by-format" / "fods"
_MINIMAL = str(_FODS_DIR / "minimal-spreadsheet.fods")   # 1 sheet, 1 cell "Hello"
_MULTI = str(_FODS_DIR / "multi-sheet-basic.fods")        # 2 sheets
_TYPED = str(_FODS_DIR / "typed-values-basic.fods")       # 1 sheet, mixed types
_FORMULA = str(_FODS_DIR / "formula-basic.fods")          # 1 sheet, formula cells


def _make_empty_wb():
    return build_workbook(
        odf_version_attr="1.3",
        mimetype=None,
        sheets=[{"name": "Empty", "index": 0, "rows": []}],
        warnings=[],
        unsupported_features=[],
        parse_errors=[],
    )


class TestFodsDataDensity:
    def test_return_type(self):
        wb = parse_fods_strict(_MINIMAL)
        assert isinstance(fods_data_density(wb), float)

    def test_exact_1_0_for_minimal(self):
        # minimal-spreadsheet.fods: 1 cell, 1 non-empty -> density=1.0
        wb = parse_fods_strict(_MINIMAL)
        assert fods_data_density(wb) == 1.0

    def test_exact_1_0_for_multi_sheet(self):
        # multi-sheet-basic.fods: all cells have data -> density=1.0
        wb = parse_fods_strict(_MULTI)
        assert fods_data_density(wb) == 1.0

    def test_exact_1_0_for_typed_values(self):
        # typed-values-basic.fods: all cells have data -> density=1.0
        wb = parse_fods_strict(_TYPED)
        assert fods_data_density(wb) == 1.0

    def test_range_0_to_1(self):
        wb = parse_fods_strict(_MINIMAL)
        density = fods_data_density(wb)
        assert 0.0 <= density <= 1.0

    def test_zero_for_empty_workbook(self):
        wb = _make_empty_wb()
        # Empty workbook has no cells -> density should be 0.0
        assert fods_data_density(wb) == 0.0

    def test_consistent_across_calls(self):
        wb = parse_fods_strict(_MINIMAL)
        assert fods_data_density(wb) == fods_data_density(wb)


class TestFodsIsSingleSheet:
    def test_return_type(self):
        wb = parse_fods_strict(_MINIMAL)
        assert isinstance(fods_is_single_sheet(wb), bool)

    def test_true_for_minimal(self):
        # minimal-spreadsheet.fods: 1 sheet -> True
        wb = parse_fods_strict(_MINIMAL)
        assert fods_is_single_sheet(wb) is True

    def test_false_for_multi_sheet(self):
        # multi-sheet-basic.fods: 2 sheets -> False
        wb = parse_fods_strict(_MULTI)
        assert fods_is_single_sheet(wb) is False

    def test_true_for_typed_values(self):
        # typed-values-basic.fods: 1 sheet -> True
        wb = parse_fods_strict(_TYPED)
        assert fods_is_single_sheet(wb) is True

    def test_true_for_formula(self):
        # formula-basic.fods: 1 sheet -> True
        wb = parse_fods_strict(_FORMULA)
        assert fods_is_single_sheet(wb) is True

    def test_consistent_across_calls(self):
        wb = parse_fods_strict(_MINIMAL)
        assert fods_is_single_sheet(wb) == fods_is_single_sheet(wb)
