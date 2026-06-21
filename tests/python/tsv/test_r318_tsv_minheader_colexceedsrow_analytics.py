"""
Tests for Sprint r318: tsv_min_header_length, tsv_column_count_exceeds_row_count.
Uses sample files from samples/by-format/tsv/.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import tsv_min_header_length, tsv_column_count_exceeds_row_count

_TSV = _REPO / "samples" / "by-format" / "tsv"


# --- tsv_min_header_length ---
# minimal-2x2.tsv: headers=['Name','Age'] → min(4,3) = 3
# multi-column.tsv: headers=['id','name','score','pass'] → min(2,4,5,4) = 2
# single-cell.tsv: headers=['value'] → min(5) = 5

def test_tsv_min_header_length_minimal_2x2():
    assert tsv_min_header_length(_TSV / "minimal-2x2.tsv") == 3


def test_tsv_min_header_length_multi_column():
    assert tsv_min_header_length(_TSV / "multi-column.tsv") == 2


def test_tsv_min_header_length_single_cell():
    assert tsv_min_header_length(_TSV / "single-cell.tsv") == 5


def test_tsv_min_header_length_returns_int_minimal():
    assert isinstance(tsv_min_header_length(_TSV / "minimal-2x2.tsv"), int)


def test_tsv_min_header_length_returns_int_multi():
    assert isinstance(tsv_min_header_length(_TSV / "multi-column.tsv"), int)


def test_tsv_min_header_length_all_three_distinct():
    results = [
        tsv_min_header_length(_TSV / "minimal-2x2.tsv"),
        tsv_min_header_length(_TSV / "multi-column.tsv"),
        tsv_min_header_length(_TSV / "single-cell.tsv"),
    ]
    assert results == [3, 2, 5]


# --- tsv_column_count_exceeds_row_count ---
# minimal-2x2.tsv: col=2, row=2 → False
# multi-column.tsv: col=4, row=2 → True
# single-cell.tsv: col=1, row=1 → False

def test_tsv_column_count_exceeds_row_count_minimal_false():
    assert tsv_column_count_exceeds_row_count(_TSV / "minimal-2x2.tsv") is False


def test_tsv_column_count_exceeds_row_count_multi_true():
    assert tsv_column_count_exceeds_row_count(_TSV / "multi-column.tsv") is True


def test_tsv_column_count_exceeds_row_count_single_false():
    assert tsv_column_count_exceeds_row_count(_TSV / "single-cell.tsv") is False


def test_tsv_column_count_exceeds_row_count_returns_bool_minimal():
    assert isinstance(tsv_column_count_exceeds_row_count(_TSV / "minimal-2x2.tsv"), bool)


def test_tsv_column_count_exceeds_row_count_returns_bool_multi():
    assert isinstance(tsv_column_count_exceeds_row_count(_TSV / "multi-column.tsv"), bool)


def test_tsv_column_count_exceeds_row_count_all_three():
    results = [
        tsv_column_count_exceeds_row_count(_TSV / "minimal-2x2.tsv"),
        tsv_column_count_exceeds_row_count(_TSV / "multi-column.tsv"),
        tsv_column_count_exceeds_row_count(_TSV / "single-cell.tsv"),
    ]
    assert results == [False, True, False]
