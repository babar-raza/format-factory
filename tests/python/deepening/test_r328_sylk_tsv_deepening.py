"""Tests for sylk_string_cell_percentage, sylk_avg_value_length,
tsv_string_field_percentage, tsv_avg_field_value_length (Sprint 118, R328).
"""
import sys
from pathlib import Path

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.sylk.sylk_parser import sylk_string_cell_percentage, sylk_avg_value_length
from src.python.tsv.tsv_parser import tsv_string_field_percentage, tsv_avg_field_value_length

SYLK = _REPO / "samples" / "by-format" / "sylk" / "valid"
TSV = _REPO / "samples" / "by-format" / "tsv"


def test_sylk_str_pct_minimal():
    assert abs(sylk_string_cell_percentage(SYLK / "minimal-2x2.slk") - 75.0) < 0.1


def test_sylk_str_pct_numeric():
    assert abs(sylk_string_cell_percentage(SYLK / "numeric-row.slk") - 0.0) < 0.1


def test_sylk_str_pct_single():
    assert abs(sylk_string_cell_percentage(SYLK / "single-cell.slk") - 0.0) < 0.1


def test_sylk_str_pct_returns_float():
    assert isinstance(sylk_string_cell_percentage(SYLK / "minimal-2x2.slk"), float)


def test_sylk_str_pct_bounded():
    val = sylk_string_cell_percentage(SYLK / "minimal-2x2.slk")
    assert 0.0 <= val <= 100.0


def test_sylk_avg_len_minimal():
    assert abs(sylk_avg_value_length(SYLK / "minimal-2x2.slk") - 4.0) < 0.01


def test_sylk_avg_len_numeric():
    assert abs(sylk_avg_value_length(SYLK / "numeric-row.slk") - 1.0) < 0.01


def test_sylk_avg_len_single():
    assert abs(sylk_avg_value_length(SYLK / "single-cell.slk") - 2.0) < 0.01


def test_sylk_avg_len_returns_float():
    assert isinstance(sylk_avg_value_length(SYLK / "minimal-2x2.slk"), float)


def test_sylk_avg_len_positive():
    assert sylk_avg_value_length(SYLK / "minimal-2x2.slk") > 0.0


def test_tsv_str_pct_minimal():
    assert abs(tsv_string_field_percentage(TSV / "minimal-2x2.tsv") - 50.0) < 0.1


def test_tsv_str_pct_multi():
    assert abs(tsv_string_field_percentage(TSV / "multi-column.tsv") - 50.0) < 0.1


def test_tsv_str_pct_single():
    assert abs(tsv_string_field_percentage(TSV / "single-cell.tsv") - 0.0) < 0.1


def test_tsv_str_pct_returns_float():
    assert isinstance(tsv_string_field_percentage(TSV / "minimal-2x2.tsv"), float)


def test_tsv_str_pct_bounded():
    val = tsv_string_field_percentage(TSV / "minimal-2x2.tsv")
    assert 0.0 <= val <= 100.0


def test_tsv_avg_len_minimal():
    assert abs(tsv_avg_field_value_length(TSV / "minimal-2x2.tsv") - 3.0) < 0.01


def test_tsv_avg_len_multi():
    assert abs(tsv_avg_field_value_length(TSV / "multi-column.tsv") - 3.375) < 0.01


def test_tsv_avg_len_single():
    assert abs(tsv_avg_field_value_length(TSV / "single-cell.tsv") - 2.0) < 0.01


def test_tsv_avg_len_returns_float():
    assert isinstance(tsv_avg_field_value_length(TSV / "minimal-2x2.tsv"), float)


def test_tsv_avg_len_positive():
    assert tsv_avg_field_value_length(TSV / "minimal-2x2.tsv") > 0.0
