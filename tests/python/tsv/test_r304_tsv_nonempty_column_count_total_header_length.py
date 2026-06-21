"""Tests for tsv_nonempty_column_count and tsv_total_header_length (Sprint 94, R304)."""
import sys
from pathlib import Path

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import tsv_nonempty_column_count, tsv_total_header_length

TSV = _REPO / "samples" / "by-format" / "tsv"


def test_nonempty_column_count_minimal():
    assert tsv_nonempty_column_count(TSV / "minimal-2x2.tsv") == 2


def test_nonempty_column_count_multi():
    assert tsv_nonempty_column_count(TSV / "multi-column.tsv") == 4


def test_nonempty_column_count_single():
    assert tsv_nonempty_column_count(TSV / "single-cell.tsv") == 1


def test_nonempty_column_count_returns_int():
    assert isinstance(tsv_nonempty_column_count(TSV / "minimal-2x2.tsv"), int)


def test_nonempty_column_count_positive():
    assert tsv_nonempty_column_count(TSV / "minimal-2x2.tsv") > 0


def test_total_header_length_minimal():
    assert tsv_total_header_length(TSV / "minimal-2x2.tsv") == 7


def test_total_header_length_multi():
    assert tsv_total_header_length(TSV / "multi-column.tsv") == 15


def test_total_header_length_single():
    assert tsv_total_header_length(TSV / "single-cell.tsv") == 5


def test_total_header_length_returns_int():
    assert isinstance(tsv_total_header_length(TSV / "minimal-2x2.tsv"), int)


def test_total_header_length_nonnegative():
    assert tsv_total_header_length(TSV / "single-cell.tsv") >= 0
