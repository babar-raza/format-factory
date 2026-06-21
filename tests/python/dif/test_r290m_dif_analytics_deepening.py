"""Tests for DIF analytics deepening (R290M): avg_cell_text_length, column_type_variety, numeric_column_count."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif.dif_parser import dif_avg_cell_text_length, dif_column_type_variety, dif_numeric_column_count

SAMPLES = _REPO / "samples" / "by-format" / "dif" / "valid"


def test_avg_cell_text_length_returns_float():
    result = dif_avg_cell_text_length(SAMPLES / "minimal-2x2.dif")
    assert isinstance(result, float)
    assert result >= 0.0


def test_avg_cell_text_length_single_cell():
    result = dif_avg_cell_text_length(SAMPLES / "single-cell.dif")
    assert isinstance(result, float)


def test_column_type_variety_returns_int():
    result = dif_column_type_variety(SAMPLES / "minimal-2x2.dif")
    assert isinstance(result, int)
    assert result >= 1


def test_column_type_variety_numeric():
    result = dif_column_type_variety(SAMPLES / "numeric-row.dif")
    assert isinstance(result, int)


def test_numeric_column_count_returns_int():
    result = dif_numeric_column_count(SAMPLES / "numeric-row.dif")
    assert isinstance(result, int)
    assert result >= 0


def test_numeric_column_count_mixed():
    result = dif_numeric_column_count(SAMPLES / "minimal-2x2.dif")
    assert isinstance(result, int)
