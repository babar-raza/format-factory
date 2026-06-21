"""Tests for CSV Sprint 76 gap closure.

Closes:
  GAP-CSV-FOSS-CSV_HEADER_F-001   (Csv Header Field Count)
  GAP-CSV-FOSS-CSV_FIELD_TE-001   (Csv Field Text Mean Length)
"""
import pytest
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import csv_header_field_count, csv_field_text_mean_length

_DIR = _REPO / "samples" / "by-format" / "csv"
_MINIMAL = str(_DIR / "minimal-2x2.csv")
_QUOTED = str(_DIR / "quoted-fields.csv")
_SINGLE = str(_DIR / "single-cell.csv")


class TestCsvHeaderFieldCount:
    def test_return_type(self):
        assert isinstance(csv_header_field_count(_MINIMAL), int)

    def test_exact_2_for_minimal(self):
        assert csv_header_field_count(_MINIMAL) == 2

    def test_exact_3_for_quoted(self):
        assert csv_header_field_count(_QUOTED) == 3

    def test_exact_1_for_single(self):
        assert csv_header_field_count(_SINGLE) == 1

    def test_nonnegative(self):
        assert csv_header_field_count(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert csv_header_field_count(_MINIMAL) == csv_header_field_count(_MINIMAL)


class TestCsvFieldTextMeanLength:
    def test_return_type(self):
        assert isinstance(csv_field_text_mean_length(_MINIMAL), (int, float))

    def test_exact_3_0_for_minimal(self):
        assert csv_field_text_mean_length(_MINIMAL) == pytest.approx(3.0)

    def test_exact_10_167_for_quoted(self):
        assert csv_field_text_mean_length(_QUOTED) == pytest.approx(10.167, rel=1e-2)

    def test_exact_2_0_for_single(self):
        assert csv_field_text_mean_length(_SINGLE) == pytest.approx(2.0)

    def test_nonnegative(self):
        assert csv_field_text_mean_length(_MINIMAL) >= 0.0

    def test_consistent_across_calls(self):
        assert csv_field_text_mean_length(_MINIMAL) == csv_field_text_mean_length(_MINIMAL)
