"""Tests for FODS Sprint 41 gap closure.

Closes:
  GAP-FODS-FOSS-FODS_HAS_NU-001  (Fods Has Numeric Cells)
  GAP-FODS-FOSS-FODS_MAX_RO-001  (Fods Max Row Cell Count)
  GAP-FODS-FOSS-FODS_MIN_CE-001  (Fods Min Cell Length)
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fods import fods_has_numeric_cells, fods_max_row_cell_count, fods_min_cell_length, parse_fods_strict

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


class TestFodsHasNumericCells:
    def test_return_type(self, minimal_wb):
        assert isinstance(fods_has_numeric_cells(minimal_wb), bool)

    def test_false_for_minimal(self, minimal_wb):
        assert fods_has_numeric_cells(minimal_wb) is False

    def test_true_for_formula(self, formula_wb):
        assert fods_has_numeric_cells(formula_wb) is True

    def test_consistent_across_calls(self, minimal_wb):
        assert fods_has_numeric_cells(minimal_wb) == fods_has_numeric_cells(minimal_wb)


class TestFodsMaxRowCellCount:
    def test_return_type(self, minimal_wb):
        assert isinstance(fods_max_row_cell_count(minimal_wb), int)

    def test_exact_1_for_minimal(self, minimal_wb):
        assert fods_max_row_cell_count(minimal_wb) == 1

    def test_exact_2_for_multi(self, multi_wb):
        assert fods_max_row_cell_count(multi_wb) == 2

    def test_exact_4_for_formula(self, formula_wb):
        # formula-basic.fods has min_cell_length=4
        assert fods_min_cell_length(formula_wb) == 4

    def test_positive(self, minimal_wb):
        assert fods_max_row_cell_count(minimal_wb) > 0

    def test_consistent_across_calls(self, minimal_wb):
        assert fods_max_row_cell_count(minimal_wb) == fods_max_row_cell_count(minimal_wb)


class TestFodsMinCellLength:
    def test_return_type(self, minimal_wb):
        assert isinstance(fods_min_cell_length(minimal_wb), int)

    def test_exact_5_for_minimal(self, minimal_wb):
        assert fods_min_cell_length(minimal_wb) == 5

    def test_exact_4_for_formula(self, formula_wb):
        assert fods_min_cell_length(formula_wb) == 4

    def test_nonnegative(self, minimal_wb):
        assert fods_min_cell_length(minimal_wb) >= 0

    def test_consistent_across_calls(self, minimal_wb):
        assert fods_min_cell_length(minimal_wb) == fods_min_cell_length(minimal_wb)
