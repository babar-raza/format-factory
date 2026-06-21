"""Tests for CSV Sprint 67 gap closure.

Closes:
  GAP-CSV-FOSS-CSV_FIELD_LE-001   (Csv Field Length Variance)
"""
import pytest
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import csv_field_length_variance

_DIR = _REPO / "samples" / "by-format" / "csv"
_MINIMAL = str(_DIR / "minimal-2x2.csv")
_QUOTED = str(_DIR / "quoted-fields.csv")
_SINGLE = str(_DIR / "single-cell.csv")


class TestCsvFieldLengthVariance:
    def test_return_type(self):
        assert isinstance(csv_field_length_variance(_MINIMAL), (int, float))

    def test_exact_1_5_for_minimal(self):
        assert csv_field_length_variance(_MINIMAL) == pytest.approx(1.5)

    def test_approx_38_14_for_quoted(self):
        assert csv_field_length_variance(_QUOTED) == pytest.approx(38.139, rel=1e-2)

    def test_zero_for_single(self):
        assert csv_field_length_variance(_SINGLE) == 0.0

    def test_nonnegative(self):
        assert csv_field_length_variance(_MINIMAL) >= 0.0

    def test_consistent_across_calls(self):
        assert csv_field_length_variance(_MINIMAL) == csv_field_length_variance(_MINIMAL)
