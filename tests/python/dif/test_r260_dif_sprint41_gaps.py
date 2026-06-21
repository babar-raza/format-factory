"""Tests for DIF Sprint 41 gap closure.

Closes:
  GAP-DIF-FOSS-DIF_MAX_COLU-001  (Dif Max Column Sum)
  GAP-DIF-FOSS-DIF_MIN_COLU-001  (Dif Min Column Sum)
  GAP-DIF-FOSS-DIF_DISTINCT-001  (Dif Distinct Numeric Count)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.dif import (
    dif_distinct_numeric_count,
    dif_max_column_sum,
    dif_min_column_sum,
)

_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"
_MINIMAL_2X2 = str(_DIR / "minimal-2x2.dif")
_NUMERIC_ROW = str(_DIR / "numeric-row.dif")
_SINGLE_CELL = str(_DIR / "single-cell.dif")


class TestDifMaxColumnSum:
    def test_return_type(self):
        assert isinstance(dif_max_column_sum(_MINIMAL_2X2), float)

    def test_exact_99_0_for_minimal_2x2(self):
        assert dif_max_column_sum(_MINIMAL_2X2) == 99.0

    def test_exact_3_0_for_numeric_row(self):
        assert dif_max_column_sum(_NUMERIC_ROW) == 3.0

    def test_consistent_across_calls(self):
        assert dif_max_column_sum(_MINIMAL_2X2) == dif_max_column_sum(_MINIMAL_2X2)


class TestDifMinColumnSum:
    def test_return_type(self):
        assert isinstance(dif_min_column_sum(_MINIMAL_2X2), float)

    def test_exact_42_0_for_minimal_2x2(self):
        assert dif_min_column_sum(_MINIMAL_2X2) == 42.0

    def test_nonnegative(self):
        assert dif_min_column_sum(_MINIMAL_2X2) >= 0

    def test_consistent_across_calls(self):
        assert dif_min_column_sum(_MINIMAL_2X2) == dif_min_column_sum(_MINIMAL_2X2)


class TestDifDistinctNumericCount:
    def test_return_type(self):
        assert isinstance(dif_distinct_numeric_count(_MINIMAL_2X2), int)

    def test_exact_2_for_minimal_2x2(self):
        assert dif_distinct_numeric_count(_MINIMAL_2X2) == 2

    def test_exact_3_for_numeric_row(self):
        assert dif_distinct_numeric_count(_NUMERIC_ROW) == 3

    def test_positive(self):
        assert dif_distinct_numeric_count(_MINIMAL_2X2) > 0

    def test_consistent_across_calls(self):
        assert dif_distinct_numeric_count(_MINIMAL_2X2) == dif_distinct_numeric_count(_MINIMAL_2X2)
