"""Tests for FODS gap closure batch 4 (Sprint 40).

Closes:
  GAP-FODS-FOSS-FODS_EMPTY_R-001  (Fods Empty Row Ratio)
  GAP-FODS-FOSS-FODS_AVG_ROW-001  (Fods Avg Row Count)
  GAP-FODS-FOSS-FODS_TOTAL_C-001  (Fods Total Col Count)
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fods import (
    fods_avg_row_count,
    fods_empty_row_ratio,
    fods_total_col_count,
    parse_fods_strict,
)

_DIR = _REPO / "samples" / "by-format" / "fods"
_MINIMAL = str(_DIR / "minimal-spreadsheet.fods")
_FORMULA = str(_DIR / "formula-basic.fods")
_MULTI = str(_DIR / "multi-sheet-basic.fods")


@pytest.fixture
def minimal_wb():
    return parse_fods_strict(_MINIMAL)


@pytest.fixture
def formula_wb():
    return parse_fods_strict(_FORMULA)


@pytest.fixture
def multi_wb():
    return parse_fods_strict(_MULTI)


class TestFodsEmptyRowRatio:
    def test_return_type(self, minimal_wb):
        assert isinstance(fods_empty_row_ratio(minimal_wb), float)

    def test_zero_for_minimal(self, minimal_wb):
        # all rows have data -> no empty rows
        assert fods_empty_row_ratio(minimal_wb) == 0.0

    def test_zero_for_formula(self, formula_wb):
        assert fods_empty_row_ratio(formula_wb) == 0.0

    def test_between_0_and_1(self, multi_wb):
        r = fods_empty_row_ratio(multi_wb)
        assert 0.0 <= r <= 1.0

    def test_consistent_across_calls(self, minimal_wb):
        assert fods_empty_row_ratio(minimal_wb) == fods_empty_row_ratio(minimal_wb)


class TestFodsAvgRowCount:
    def test_return_type(self, minimal_wb):
        assert isinstance(fods_avg_row_count(minimal_wb), float)

    def test_exact_1_0_for_minimal(self, minimal_wb):
        assert fods_avg_row_count(minimal_wb) == 1.0

    def test_exact_4_0_for_formula(self, formula_wb):
        assert fods_avg_row_count(formula_wb) == 4.0

    def test_exact_1_5_for_multi(self, multi_wb):
        assert fods_avg_row_count(multi_wb) == 1.5

    def test_positive(self, minimal_wb):
        assert fods_avg_row_count(minimal_wb) > 0

    def test_consistent_across_calls(self, formula_wb):
        assert fods_avg_row_count(formula_wb) == fods_avg_row_count(formula_wb)


class TestFodsTotalColCount:
    def test_return_type(self, minimal_wb):
        assert isinstance(fods_total_col_count(minimal_wb), int)

    def test_exact_1_for_minimal(self, minimal_wb):
        assert fods_total_col_count(minimal_wb) == 1

    def test_exact_3_for_multi(self, multi_wb):
        assert fods_total_col_count(multi_wb) == 3

    def test_positive(self, minimal_wb):
        assert fods_total_col_count(minimal_wb) > 0

    def test_consistent_across_calls(self, multi_wb):
        assert fods_total_col_count(multi_wb) == fods_total_col_count(multi_wb)
