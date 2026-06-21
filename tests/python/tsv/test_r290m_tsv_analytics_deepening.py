"""Tests for TSV analytics deepening (R290M): avg_field_text_length, empty_row_ratio, distinct_value_count."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from tsv.tsv_parser import tsv_avg_field_text_length, tsv_empty_row_ratio, tsv_distinct_value_count

SAMPLES = _REPO / "samples" / "by-format" / "tsv"


def test_avg_field_text_length_returns_float():
    result = tsv_avg_field_text_length(SAMPLES / "minimal-2x2.tsv")
    assert isinstance(result, float)
    assert result >= 0.0


def test_avg_field_text_length_single():
    result = tsv_avg_field_text_length(SAMPLES / "single-cell.tsv")
    assert isinstance(result, float)


def test_empty_row_ratio_returns_float():
    result = tsv_empty_row_ratio(SAMPLES / "minimal-2x2.tsv")
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0


def test_empty_row_ratio_multi():
    result = tsv_empty_row_ratio(SAMPLES / "multi-column.tsv")
    assert isinstance(result, float)


def test_distinct_value_count_returns_int():
    result = tsv_distinct_value_count(SAMPLES / "minimal-2x2.tsv")
    assert isinstance(result, int)
    assert result >= 1


def test_distinct_value_count_multi():
    result = tsv_distinct_value_count(SAMPLES / "multi-column.tsv")
    assert isinstance(result, int)
