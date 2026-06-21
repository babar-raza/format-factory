"""
Tests for Sprint r312: tsv_max_row_field_count, tsv_has_only_numeric_row.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import tsv_max_row_field_count, tsv_has_only_numeric_row

_TSV = _REPO / "samples" / "by-format" / "tsv"


# --- tsv_max_row_field_count ---

def test_tsv_max_row_field_count_minimal_two():
    assert tsv_max_row_field_count(_TSV / "minimal-2x2.tsv") == 2


def test_tsv_max_row_field_count_multi_column_four():
    assert tsv_max_row_field_count(_TSV / "multi-column.tsv") == 4


def test_tsv_max_row_field_count_single_cell_one():
    assert tsv_max_row_field_count(_TSV / "single-cell.tsv") == 1


def test_tsv_max_row_field_count_returns_int_minimal():
    assert isinstance(tsv_max_row_field_count(_TSV / "minimal-2x2.tsv"), int)


def test_tsv_max_row_field_count_returns_int_multi():
    assert isinstance(tsv_max_row_field_count(_TSV / "multi-column.tsv"), int)


def test_tsv_max_row_field_count_all_three_distinct():
    results = [
        tsv_max_row_field_count(_TSV / "minimal-2x2.tsv"),
        tsv_max_row_field_count(_TSV / "multi-column.tsv"),
        tsv_max_row_field_count(_TSV / "single-cell.tsv"),
    ]
    assert results == [2, 4, 1]


# --- tsv_has_only_numeric_row ---

def test_tsv_has_only_numeric_row_minimal_false():
    # rows have mixed (name, number) — no all-numeric row
    assert tsv_has_only_numeric_row(_TSV / "minimal-2x2.tsv") is False


def test_tsv_has_only_numeric_row_multi_column_false():
    # rows contain alphabetic fields — no all-numeric row
    assert tsv_has_only_numeric_row(_TSV / "multi-column.tsv") is False


def test_tsv_has_only_numeric_row_single_cell_true():
    # single field '42' is numeric
    assert tsv_has_only_numeric_row(_TSV / "single-cell.tsv") is True


def test_tsv_has_only_numeric_row_returns_bool_minimal():
    assert isinstance(tsv_has_only_numeric_row(_TSV / "minimal-2x2.tsv"), bool)


def test_tsv_has_only_numeric_row_returns_bool_single():
    assert isinstance(tsv_has_only_numeric_row(_TSV / "single-cell.tsv"), bool)


def test_tsv_has_only_numeric_row_all_three():
    results = [
        tsv_has_only_numeric_row(_TSV / "minimal-2x2.tsv"),
        tsv_has_only_numeric_row(_TSV / "multi-column.tsv"),
        tsv_has_only_numeric_row(_TSV / "single-cell.tsv"),
    ]
    assert results == [False, False, True]
