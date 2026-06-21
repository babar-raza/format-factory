"""Tests for ODS analytics deepening (R290P): fill_rate, avg_cell_value_length, row_width_variance."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods.ods_parser import ods_fill_rate, ods_avg_cell_value_length, ods_row_width_variance

SAMPLES = _REPO / "samples" / "by-format" / "ods" / "valid"


def test_fill_rate_returns_float():
    result = ods_fill_rate(SAMPLES / "minimal-spreadsheet.ods")
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0


def test_fill_rate_single_cell():
    result = ods_fill_rate(SAMPLES / "single-cell.ods")
    assert isinstance(result, float)


def test_avg_cell_value_length_returns_float():
    result = ods_avg_cell_value_length(SAMPLES / "minimal-spreadsheet.ods")
    assert isinstance(result, float)
    assert result >= 0.0


def test_avg_cell_value_length_numeric():
    result = ods_avg_cell_value_length(SAMPLES / "numeric-row.ods")
    assert isinstance(result, float)


def test_row_width_variance_returns_float():
    result = ods_row_width_variance(SAMPLES / "minimal-spreadsheet.ods")
    assert isinstance(result, float)
    assert result >= 0.0


def test_row_width_variance_single_cell():
    result = ods_row_width_variance(SAMPLES / "single-cell.ods")
    assert isinstance(result, float)
