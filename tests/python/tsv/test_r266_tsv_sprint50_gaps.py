"""Tests for TSV Sprint 50 gap closure.

Closes:
  GAP-TSV-FOSS-TSV_HAS_HEAD-001   (Tsv Has Header Row)
  GAP-TSV-FOSS-TSV_ROW_FIEL-001   (Tsv Row Field Variance)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.tsv import tsv_has_header_row, tsv_row_field_variance

_DIR = _REPO / "samples" / "by-format" / "tsv"
_MINIMAL = str(_DIR / "minimal-2x2.tsv")
_MULTI = str(_DIR / "multi-column.tsv")
_SINGLE = str(_DIR / "single-cell.tsv")
_INVALID = str(_DIR / "invalid-binary-garbage.tsv")


class TestTsvHasHeaderRow:
    def test_return_type(self):
        assert isinstance(tsv_has_header_row(_MINIMAL), bool)

    def test_false_for_minimal(self):
        assert tsv_has_header_row(_MINIMAL) is False

    def test_false_for_multi_column(self):
        assert tsv_has_header_row(_MULTI) is False

    def test_false_for_single_cell(self):
        assert tsv_has_header_row(_SINGLE) is False

    def test_true_for_invalid_binary(self):
        assert tsv_has_header_row(_INVALID) is True

    def test_consistent_across_calls(self):
        assert tsv_has_header_row(_MINIMAL) == tsv_has_header_row(_MINIMAL)


class TestTsvRowFieldVariance:
    def test_return_type(self):
        assert isinstance(tsv_row_field_variance(_MINIMAL), (int, float))

    def test_zero_for_minimal(self):
        assert tsv_row_field_variance(_MINIMAL) == 0.0

    def test_zero_for_multi_column(self):
        assert tsv_row_field_variance(_MULTI) == 0.0

    def test_zero_for_single_cell(self):
        assert tsv_row_field_variance(_SINGLE) == 0.0

    def test_nonnegative(self):
        assert tsv_row_field_variance(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert tsv_row_field_variance(_MINIMAL) == tsv_row_field_variance(_MINIMAL)
