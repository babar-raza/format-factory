"""Tests for csv_avg_field_length and csv_string_field_percentage (Sprint 112, R322)."""
import sys
from pathlib import Path

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import csv_avg_field_length, csv_string_field_percentage

CSV = _REPO / "samples" / "by-format" / "csv"


def test_avg_len_minimal():
    assert abs(csv_avg_field_length(CSV / "minimal-2x2.csv") - 3.0) < 0.1


def test_avg_len_single():
    assert abs(csv_avg_field_length(CSV / "single-cell.csv") - 2.0) < 0.1


def test_avg_len_quoted():
    val = csv_avg_field_length(CSV / "quoted-fields.csv")
    assert val > 0, f"expected positive, got {val}"


def test_avg_len_returns_float():
    assert isinstance(csv_avg_field_length(CSV / "minimal-2x2.csv"), float)


def test_avg_len_positive():
    assert csv_avg_field_length(CSV / "minimal-2x2.csv") > 0.0


def test_string_pct_minimal():
    assert abs(csv_string_field_percentage(CSV / "minimal-2x2.csv") - 50.0) < 0.1


def test_string_pct_single():
    assert abs(csv_string_field_percentage(CSV / "single-cell.csv") - 0.0) < 0.1


def test_string_pct_quoted():
    val = csv_string_field_percentage(CSV / "quoted-fields.csv")
    assert val >= 0.0


def test_string_pct_returns_float():
    assert isinstance(csv_string_field_percentage(CSV / "minimal-2x2.csv"), float)


def test_string_pct_nonnegative():
    assert csv_string_field_percentage(CSV / "minimal-2x2.csv") >= 0.0
