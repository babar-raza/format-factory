"""Tests for tsv_numeric_field_percentage and tsv_fields_per_row (Sprint 111, R321)."""
import sys
from pathlib import Path

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import tsv_numeric_field_percentage, tsv_fields_per_row

TSV = _REPO / "samples" / "by-format" / "tsv"


def test_numeric_pct_minimal():
    assert abs(tsv_numeric_field_percentage(TSV / "minimal-2x2.tsv") - 50.0) < 0.1


def test_numeric_pct_multi():
    assert abs(tsv_numeric_field_percentage(TSV / "multi-column.tsv") - 50.0) < 0.1


def test_numeric_pct_single():
    assert abs(tsv_numeric_field_percentage(TSV / "single-cell.tsv") - 100.0) < 0.1


def test_numeric_pct_returns_float():
    assert isinstance(tsv_numeric_field_percentage(TSV / "minimal-2x2.tsv"), float)


def test_numeric_pct_bounded():
    pct = tsv_numeric_field_percentage(TSV / "minimal-2x2.tsv")
    assert 0.0 <= pct <= 100.0


def test_fields_per_row_minimal():
    assert abs(tsv_fields_per_row(TSV / "minimal-2x2.tsv") - 2.0) < 0.01


def test_fields_per_row_multi():
    assert abs(tsv_fields_per_row(TSV / "multi-column.tsv") - 4.0) < 0.01


def test_fields_per_row_single():
    assert abs(tsv_fields_per_row(TSV / "single-cell.tsv") - 1.0) < 0.01


def test_fields_per_row_returns_float():
    assert isinstance(tsv_fields_per_row(TSV / "minimal-2x2.tsv"), float)


def test_fields_per_row_positive():
    assert tsv_fields_per_row(TSV / "multi-column.tsv") > 0.0
