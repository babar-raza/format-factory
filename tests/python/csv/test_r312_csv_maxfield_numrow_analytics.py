"""
Tests for Sprint r312: csv_max_row_field_count, csv_has_only_numeric_row.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import csv_max_row_field_count, csv_has_only_numeric_row

_CSV = _REPO / "samples" / "by-format" / "csv"


# --- csv_max_row_field_count ---

def test_csv_max_row_field_count_minimal_two():
    assert csv_max_row_field_count(_CSV / "minimal-2x2.csv") == 2


def test_csv_max_row_field_count_quoted_three():
    assert csv_max_row_field_count(_CSV / "quoted-fields.csv") == 3


def test_csv_max_row_field_count_single_cell_one():
    assert csv_max_row_field_count(_CSV / "single-cell.csv") == 1


def test_csv_max_row_field_count_returns_int_minimal():
    assert isinstance(csv_max_row_field_count(_CSV / "minimal-2x2.csv"), int)


def test_csv_max_row_field_count_returns_int_quoted():
    assert isinstance(csv_max_row_field_count(_CSV / "quoted-fields.csv"), int)


def test_csv_max_row_field_count_all_three_distinct():
    results = [
        csv_max_row_field_count(_CSV / "minimal-2x2.csv"),
        csv_max_row_field_count(_CSV / "quoted-fields.csv"),
        csv_max_row_field_count(_CSV / "single-cell.csv"),
    ]
    assert results == [2, 3, 1]


# --- csv_has_only_numeric_row ---

def test_csv_has_only_numeric_row_minimal_false():
    # rows have mixed (name, number) — no all-numeric row
    assert csv_has_only_numeric_row(_CSV / "minimal-2x2.csv") is False


def test_csv_has_only_numeric_row_quoted_false():
    # all rows have string fields — no all-numeric row
    assert csv_has_only_numeric_row(_CSV / "quoted-fields.csv") is False


def test_csv_has_only_numeric_row_single_cell_true():
    # single field '42' is numeric
    assert csv_has_only_numeric_row(_CSV / "single-cell.csv") is True


def test_csv_has_only_numeric_row_returns_bool_minimal():
    assert isinstance(csv_has_only_numeric_row(_CSV / "minimal-2x2.csv"), bool)


def test_csv_has_only_numeric_row_returns_bool_single():
    assert isinstance(csv_has_only_numeric_row(_CSV / "single-cell.csv"), bool)


def test_csv_has_only_numeric_row_all_three():
    results = [
        csv_has_only_numeric_row(_CSV / "minimal-2x2.csv"),
        csv_has_only_numeric_row(_CSV / "quoted-fields.csv"),
        csv_has_only_numeric_row(_CSV / "single-cell.csv"),
    ]
    assert results == [False, False, True]
