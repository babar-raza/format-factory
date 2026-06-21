"""Tests for FODS gap closure batch 2 (Sprint 40).

Closes:
  GAP-FODS-FOSS-FODS_TOTAL_T-001  (Fods Total Text Length)
  GAP-FODS-FOSS-FODS_COLUMN_-001  (Fods Column Count Variance)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fods import fods_col_count_variance, fods_total_text_length, parse_fods_strict

_DIR = _REPO / "samples" / "by-format" / "fods"
_FORMULA = str(_DIR / "formula-basic.fods")
_MINIMAL = str(_DIR / "minimal-spreadsheet.fods")
_MULTI_SHEET = str(_DIR / "multi-sheet-basic.fods")


class TestFodsTotalTextLength:
    def test_return_type(self):
        wb = parse_fods_strict(_FORMULA)
        assert isinstance(fods_total_text_length(wb), int)

    def test_exact_16_for_formula(self):
        wb = parse_fods_strict(_FORMULA)
        assert fods_total_text_length(wb) == 16

    def test_exact_5_for_minimal(self):
        wb = parse_fods_strict(_MINIMAL)
        assert fods_total_text_length(wb) == 5

    def test_exact_18_for_multi_sheet(self):
        wb = parse_fods_strict(_MULTI_SHEET)
        assert fods_total_text_length(wb) == 18

    def test_nonnegative(self):
        wb = parse_fods_strict(_FORMULA)
        assert fods_total_text_length(wb) >= 0

    def test_consistent_across_calls(self):
        wb = parse_fods_strict(_FORMULA)
        assert fods_total_text_length(wb) == fods_total_text_length(wb)


class TestFodsColCountVariance:
    def test_return_type(self):
        wb = parse_fods_strict(_FORMULA)
        assert isinstance(fods_col_count_variance(wb), float)

    def test_zero_for_single_sheet_formula(self):
        wb = parse_fods_strict(_FORMULA)
        assert fods_col_count_variance(wb) == 0.0

    def test_zero_for_minimal_single_sheet(self):
        wb = parse_fods_strict(_MINIMAL)
        assert fods_col_count_variance(wb) == 0.0

    def test_nonzero_for_multi_sheet(self):
        wb = parse_fods_strict(_MULTI_SHEET)
        assert fods_col_count_variance(wb) == 0.25

    def test_nonnegative(self):
        wb = parse_fods_strict(_FORMULA)
        assert fods_col_count_variance(wb) >= 0.0

    def test_consistent_across_calls(self):
        wb = parse_fods_strict(_MULTI_SHEET)
        assert fods_col_count_variance(wb) == fods_col_count_variance(wb)
