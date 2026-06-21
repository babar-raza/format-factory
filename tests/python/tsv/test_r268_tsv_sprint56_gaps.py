"""Tests for TSV Sprint 56 gap closure.

Closes:
  GAP-TSV-FOSS-TSV_FIELD_UN-001  (Tsv Field Uniqueness Ratio)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.tsv import tsv_field_uniqueness_ratio

_DIR = _REPO / "samples" / "by-format" / "tsv"
_MINIMAL = str(_DIR / "minimal-2x2.tsv")
_MULTI = str(_DIR / "multi-column.tsv")
_SINGLE = str(_DIR / "single-cell.tsv")


class TestTsvFieldUniquenessRatio:
    def test_return_type(self):
        assert isinstance(tsv_field_uniqueness_ratio(_MINIMAL), (int, float))

    def test_exact_1_for_minimal(self):
        assert tsv_field_uniqueness_ratio(_MINIMAL) == 1.0

    def test_exact_1_for_multi_column(self):
        assert tsv_field_uniqueness_ratio(_MULTI) == 1.0

    def test_exact_1_for_single_cell(self):
        assert tsv_field_uniqueness_ratio(_SINGLE) == 1.0

    def test_in_range_0_to_1(self):
        assert 0.0 <= tsv_field_uniqueness_ratio(_MINIMAL) <= 1.0

    def test_consistent_across_calls(self):
        assert tsv_field_uniqueness_ratio(_MINIMAL) == tsv_field_uniqueness_ratio(_MINIMAL)
