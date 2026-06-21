"""Tests for csv_nonempty_column_count and csv_avg_string_field_length (Sprint 95, R305)."""
import sys
from pathlib import Path

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import csv_nonempty_column_count, csv_avg_string_field_length

CSV = _REPO / "samples" / "by-format" / "csv"


def test_nonempty_column_count_minimal():
    assert csv_nonempty_column_count(CSV / "minimal-2x2.csv") == 2


def test_nonempty_column_count_quoted():
    assert csv_nonempty_column_count(CSV / "quoted-fields.csv") == 3


def test_nonempty_column_count_single():
    assert csv_nonempty_column_count(CSV / "single-cell.csv") == 1


def test_nonempty_column_count_returns_int():
    assert isinstance(csv_nonempty_column_count(CSV / "minimal-2x2.csv"), int)


def test_nonempty_column_count_positive():
    assert csv_nonempty_column_count(CSV / "minimal-2x2.csv") > 0


def test_avg_string_field_length_minimal():
    assert abs(csv_avg_string_field_length(CSV / "minimal-2x2.csv") - 4.0) < 0.01


def test_avg_string_field_length_quoted():
    assert abs(csv_avg_string_field_length(CSV / "quoted-fields.csv") - 13.0) < 0.01


def test_avg_string_field_length_single():
    assert abs(csv_avg_string_field_length(CSV / "single-cell.csv") - 0.0) < 0.01


def test_avg_string_field_length_returns_float():
    assert isinstance(csv_avg_string_field_length(CSV / "minimal-2x2.csv"), float)


def test_avg_string_field_length_nonnegative():
    assert csv_avg_string_field_length(CSV / "single-cell.csv") >= 0.0
