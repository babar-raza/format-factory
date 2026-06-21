"""Tests for FODS Sprint 42 gap closure.

Closes:
  GAP-FODS-FOSS-FODS_EMPTY_R-001  (Fods Empty Row Count)
  GAP-FODS-FOSS-FODS_DISTINC-001  (Fods Distinct Value Count)
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fods import fods_distinct_value_count, fods_empty_row_count, parse_fods_strict

_DIR = _REPO / "samples" / "by-format" / "fods"


@pytest.fixture
def minimal_wb():
    return parse_fods_strict(str(_DIR / "minimal-spreadsheet.fods"))


@pytest.fixture
def formula_wb():
    return parse_fods_strict(str(_DIR / "formula-basic.fods"))


@pytest.fixture
def multi_wb():
    return parse_fods_strict(str(_DIR / "multi-sheet-basic.fods"))


class TestFodsEmptyRowCount:
    def test_return_type(self, minimal_wb):
        assert isinstance(fods_empty_row_count(minimal_wb), int)

    def test_zero_for_minimal(self, minimal_wb):
        assert fods_empty_row_count(minimal_wb) == 0

    def test_zero_for_formula(self, formula_wb):
        assert fods_empty_row_count(formula_wb) == 0

    def test_nonnegative(self, minimal_wb):
        assert fods_empty_row_count(minimal_wb) >= 0

    def test_consistent_across_calls(self, minimal_wb):
        assert fods_empty_row_count(minimal_wb) == fods_empty_row_count(minimal_wb)


class TestFodsDistinctValueCount:
    def test_return_type(self, minimal_wb):
        assert isinstance(fods_distinct_value_count(minimal_wb), int)

    def test_exact_1_for_minimal(self, minimal_wb):
        assert fods_distinct_value_count(minimal_wb) == 1

    def test_exact_4_for_formula(self, formula_wb):
        assert fods_distinct_value_count(formula_wb) == 4

    def test_exact_4_for_multi(self, multi_wb):
        assert fods_distinct_value_count(multi_wb) == 4

    def test_positive(self, minimal_wb):
        assert fods_distinct_value_count(minimal_wb) > 0

    def test_consistent_across_calls(self, minimal_wb):
        assert fods_distinct_value_count(minimal_wb) == fods_distinct_value_count(minimal_wb)
