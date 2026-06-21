"""Tests for DIF gap closure batch 3 (Sprint 40).

Closes:
  GAP-DIF-FOSS-DIF_IS_WIDER-001   (Dif Is Wider Than Tall)
  GAP-DIF-FOSS-DIF_MIN_ROW_-001   (Dif Min Row Index)
  GAP-DIF-FOSS-DIF_MAX_ROW_-001   (Dif Max Row Index)
  GAP-DIF-FOSS-DIF_VECTORS_-001   (Dif Vectors Count)
  GAP-DIF-FOSS-DIF_COLUMN_F-001   (Dif Column Fill Ratio)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.dif import (
    dif_column_fill_ratio,
    dif_is_wider_than_tall,
    dif_max_row_index,
    dif_min_row_index,
    dif_vectors_count,
)

_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"
_MINIMAL_2X2 = str(_DIR / "minimal-2x2.dif")
_NUMERIC_ROW = str(_DIR / "numeric-row.dif")
_SINGLE_CELL = str(_DIR / "single-cell.dif")


class TestDifIsWiderThanTall:
    def test_return_type(self):
        assert isinstance(dif_is_wider_than_tall(_MINIMAL_2X2), bool)

    def test_false_for_minimal_2x2(self):
        assert dif_is_wider_than_tall(_MINIMAL_2X2) is False

    def test_true_for_numeric_row(self):
        # numeric-row has more columns than rows
        assert dif_is_wider_than_tall(_NUMERIC_ROW) is True

    def test_consistent_across_calls(self):
        assert dif_is_wider_than_tall(_MINIMAL_2X2) == dif_is_wider_than_tall(_MINIMAL_2X2)


class TestDifMinRowIndex:
    def test_return_type(self):
        assert isinstance(dif_min_row_index(_MINIMAL_2X2), int)

    def test_zero_for_minimal_2x2(self):
        assert dif_min_row_index(_MINIMAL_2X2) == 0

    def test_nonnegative(self):
        assert dif_min_row_index(_MINIMAL_2X2) >= 0

    def test_consistent_across_calls(self):
        assert dif_min_row_index(_MINIMAL_2X2) == dif_min_row_index(_MINIMAL_2X2)


class TestDifMaxRowIndex:
    def test_return_type(self):
        assert isinstance(dif_max_row_index(_MINIMAL_2X2), int)

    def test_zero_for_minimal_2x2(self):
        assert dif_max_row_index(_MINIMAL_2X2) == 0

    def test_nonnegative(self):
        assert dif_max_row_index(_MINIMAL_2X2) >= 0

    def test_consistent_across_calls(self):
        assert dif_max_row_index(_MINIMAL_2X2) == dif_max_row_index(_MINIMAL_2X2)


class TestDifVectorsCount:
    def test_return_type(self):
        assert isinstance(dif_vectors_count(_MINIMAL_2X2), int)

    def test_exact_2_for_minimal_2x2(self):
        assert dif_vectors_count(_MINIMAL_2X2) == 2

    def test_exact_3_for_numeric_row(self):
        assert dif_vectors_count(_NUMERIC_ROW) == 3

    def test_exact_1_for_single_cell(self):
        assert dif_vectors_count(_SINGLE_CELL) == 1

    def test_positive(self):
        assert dif_vectors_count(_MINIMAL_2X2) > 0

    def test_consistent_across_calls(self):
        assert dif_vectors_count(_MINIMAL_2X2) == dif_vectors_count(_MINIMAL_2X2)


class TestDifColumnFillRatio:
    def test_return_type(self):
        assert isinstance(dif_column_fill_ratio(_MINIMAL_2X2), float)

    def test_exact_4_0_for_minimal_2x2(self):
        assert dif_column_fill_ratio(_MINIMAL_2X2) == 4.0

    def test_exact_1_0_for_numeric_row(self):
        assert dif_column_fill_ratio(_NUMERIC_ROW) == 1.0

    def test_positive(self):
        assert dif_column_fill_ratio(_MINIMAL_2X2) > 0

    def test_consistent_across_calls(self):
        assert dif_column_fill_ratio(_MINIMAL_2X2) == dif_column_fill_ratio(_MINIMAL_2X2)
