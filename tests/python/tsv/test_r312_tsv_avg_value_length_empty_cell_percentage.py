"""Tests for tsv_avg_value_length and tsv_empty_cell_percentage (Sprint 102, R312)."""
import sys
from pathlib import Path

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import tsv_avg_value_length, tsv_empty_cell_percentage

TSV = _REPO / "samples" / "by-format" / "tsv"


def test_avg_value_length_minimal():
    assert abs(tsv_avg_value_length(TSV / "minimal-2x2.tsv") - 3.0) < 0.001


def test_avg_value_length_multi():
    assert abs(tsv_avg_value_length(TSV / "multi-column.tsv") - 3.375) < 0.001


def test_avg_value_length_single():
    assert abs(tsv_avg_value_length(TSV / "single-cell.tsv") - 2.0) < 0.001


def test_avg_value_length_returns_float():
    assert isinstance(tsv_avg_value_length(TSV / "minimal-2x2.tsv"), float)


def test_avg_value_length_positive():
    assert tsv_avg_value_length(TSV / "multi-column.tsv") > 0.0


def test_empty_cell_percentage_minimal():
    assert abs(tsv_empty_cell_percentage(TSV / "minimal-2x2.tsv") - 0.0) < 0.001


def test_empty_cell_percentage_multi():
    assert abs(tsv_empty_cell_percentage(TSV / "multi-column.tsv") - 0.0) < 0.001


def test_empty_cell_percentage_single():
    assert abs(tsv_empty_cell_percentage(TSV / "single-cell.tsv") - 0.0) < 0.001


def test_empty_cell_percentage_returns_float():
    assert isinstance(tsv_empty_cell_percentage(TSV / "minimal-2x2.tsv"), float)


def test_empty_cell_percentage_bounded():
    p = tsv_empty_cell_percentage(TSV / "minimal-2x2.tsv")
    assert 0.0 <= p <= 100.0
