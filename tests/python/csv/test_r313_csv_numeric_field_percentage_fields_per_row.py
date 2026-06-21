"""Tests for csv_numeric_field_percentage and csv_fields_per_row (Sprint 103, R313)."""
import sys
from pathlib import Path

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import csv_numeric_field_percentage, csv_fields_per_row

CSV = _REPO / "samples" / "by-format" / "csv"


def test_numeric_pct_minimal():
    assert abs(csv_numeric_field_percentage(CSV / "minimal-2x2.csv") - 50.0) < 0.1


def test_numeric_pct_quoted():
    assert abs(csv_numeric_field_percentage(CSV / "quoted-fields.csv") - 33.33) < 0.1


def test_numeric_pct_single():
    assert abs(csv_numeric_field_percentage(CSV / "single-cell.csv") - 100.0) < 0.1


def test_numeric_pct_returns_float():
    assert isinstance(csv_numeric_field_percentage(CSV / "minimal-2x2.csv"), float)


def test_numeric_pct_bounded():
    pct = csv_numeric_field_percentage(CSV / "minimal-2x2.csv")
    assert 0.0 <= pct <= 100.0


def test_fields_per_row_minimal():
    assert abs(csv_fields_per_row(CSV / "minimal-2x2.csv") - 2.0) < 0.01


def test_fields_per_row_quoted():
    assert abs(csv_fields_per_row(CSV / "quoted-fields.csv") - 3.0) < 0.01


def test_fields_per_row_single():
    assert abs(csv_fields_per_row(CSV / "single-cell.csv") - 1.0) < 0.01


def test_fields_per_row_returns_float():
    assert isinstance(csv_fields_per_row(CSV / "minimal-2x2.csv"), float)


def test_fields_per_row_positive():
    assert csv_fields_per_row(CSV / "quoted-fields.csv") > 0.0
