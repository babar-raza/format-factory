"""Tests for CSV analytics deepening (R290M): avg_field_text_length, column_uniformity, max_field_count_per_row."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import csv_avg_field_text_length, csv_column_uniformity, csv_max_field_count_per_row

SAMPLES = _REPO / "samples" / "by-format" / "csv"


def test_avg_field_text_length_returns_float():
    result = csv_avg_field_text_length(SAMPLES / "minimal-2x2.csv")
    assert isinstance(result, float)
    assert result >= 0.0


def test_avg_field_text_length_single_cell():
    result = csv_avg_field_text_length(SAMPLES / "single-cell.csv")
    assert isinstance(result, float)


def test_column_uniformity_returns_float():
    result = csv_column_uniformity(SAMPLES / "minimal-2x2.csv")
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0


def test_column_uniformity_single():
    result = csv_column_uniformity(SAMPLES / "single-cell.csv")
    assert result == 1.0  # all rows same field count


def test_max_field_count_per_row_returns_int():
    result = csv_max_field_count_per_row(SAMPLES / "minimal-2x2.csv")
    assert isinstance(result, int)
    assert result >= 1


def test_max_field_count_per_row_quoted():
    result = csv_max_field_count_per_row(SAMPLES / "quoted-fields.csv")
    assert isinstance(result, int)
