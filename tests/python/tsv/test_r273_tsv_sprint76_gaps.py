"""Tests for TSV Sprint 76 gap closure.

Closes:
  GAP-TSV-FOSS-TSV_FIELD_CO-001   (Tsv Field Count Variance)
  GAP-TSV-FOSS-TSV_MIN_HEAD-001   (Tsv Min Header Length)
"""
import pytest
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import tsv_field_count_variance, tsv_min_header_length

_DIR = _REPO / "samples" / "by-format" / "tsv"
_MINIMAL = str(_DIR / "minimal-2x2.tsv")
_MULTI = str(_DIR / "multi-column.tsv")
_SINGLE = str(_DIR / "single-cell.tsv")


class TestTsvFieldCountVariance:
    def test_return_type(self):
        assert isinstance(tsv_field_count_variance(_MINIMAL), (int, float))

    def test_zero_for_minimal(self):
        assert tsv_field_count_variance(_MINIMAL) == pytest.approx(0.0)

    def test_zero_for_multi(self):
        assert tsv_field_count_variance(_MULTI) == pytest.approx(0.0)

    def test_zero_for_single(self):
        assert tsv_field_count_variance(_SINGLE) == pytest.approx(0.0)

    def test_nonnegative(self):
        assert tsv_field_count_variance(_MINIMAL) >= 0.0

    def test_consistent_across_calls(self):
        assert tsv_field_count_variance(_MINIMAL) == tsv_field_count_variance(_MINIMAL)


class TestTsvMinHeaderLength:
    def test_return_type(self):
        assert isinstance(tsv_min_header_length(_MINIMAL), (int, float))

    def test_exact_3_for_minimal(self):
        assert tsv_min_header_length(_MINIMAL) == 3

    def test_exact_2_for_multi(self):
        assert tsv_min_header_length(_MULTI) == 2

    def test_exact_5_for_single(self):
        assert tsv_min_header_length(_SINGLE) == 5

    def test_positive(self):
        assert tsv_min_header_length(_MINIMAL) > 0

    def test_consistent_across_calls(self):
        assert tsv_min_header_length(_MINIMAL) == tsv_min_header_length(_MINIMAL)
