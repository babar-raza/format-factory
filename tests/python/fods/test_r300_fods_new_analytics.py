"""
Sprint 36 — 5 new FODS analytics functions.
Tests: fods_nonempty_cell_count, fods_nonempty_cell_ratio,
       fods_string_to_numeric_ratio, fods_avg_row_count,
       fods_total_col_count
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods import (
    parse_fods,
    fods_nonempty_cell_count,
    fods_nonempty_cell_ratio,
    fods_string_to_numeric_ratio,
    fods_avg_row_count,
    fods_total_col_count,
)

_SAMPLES = _REPO / "samples" / "by-format" / "fods"
MINIMAL = str(_SAMPLES / "minimal-spreadsheet.fods")
NUMERIC = str(_SAMPLES / "typed-values-basic.fods")
MULTI = str(_SAMPLES / "multi-sheet-basic.fods")
FORMULA = str(_SAMPLES / "formula-basic.fods")


def _load(path):
    return parse_fods(path)


# --- fods_nonempty_cell_count ---

def test_nonempty_cell_count_minimal_is_int():
    assert isinstance(fods_nonempty_cell_count(_load(MINIMAL)), int)


def test_nonempty_cell_count_minimal_nonnegative():
    assert fods_nonempty_cell_count(_load(MINIMAL)) >= 0


def test_nonempty_cell_count_numeric_positive():
    assert fods_nonempty_cell_count(_load(NUMERIC)) > 0


def test_nonempty_cell_count_multi_is_int():
    assert isinstance(fods_nonempty_cell_count(_load(MULTI)), int)


# --- fods_nonempty_cell_ratio ---

def test_nonempty_cell_ratio_minimal_is_float():
    assert isinstance(fods_nonempty_cell_ratio(_load(MINIMAL)), float)


def test_nonempty_cell_ratio_minimal_in_range():
    result = fods_nonempty_cell_ratio(_load(MINIMAL))
    assert 0.0 <= result <= 1.0


def test_nonempty_cell_ratio_numeric_positive():
    assert fods_nonempty_cell_ratio(_load(NUMERIC)) > 0.0


def test_nonempty_cell_ratio_multi_in_range():
    result = fods_nonempty_cell_ratio(_load(MULTI))
    assert 0.0 <= result <= 1.0


# --- fods_string_to_numeric_ratio ---

def test_string_to_numeric_ratio_minimal_is_float():
    assert isinstance(fods_string_to_numeric_ratio(_load(MINIMAL)), float)


def test_string_to_numeric_ratio_minimal_nonnegative():
    assert fods_string_to_numeric_ratio(_load(MINIMAL)) >= 0.0


def test_string_to_numeric_ratio_numeric_file():
    result = fods_string_to_numeric_ratio(_load(NUMERIC))
    assert isinstance(result, float)


def test_string_to_numeric_ratio_multi_is_float():
    assert isinstance(fods_string_to_numeric_ratio(_load(MULTI)), float)


# --- fods_avg_row_count ---

def test_avg_row_count_minimal_is_float():
    assert isinstance(fods_avg_row_count(_load(MINIMAL)), float)


def test_avg_row_count_minimal_positive():
    assert fods_avg_row_count(_load(MINIMAL)) > 0.0


def test_avg_row_count_numeric_positive():
    assert fods_avg_row_count(_load(NUMERIC)) > 0.0


def test_avg_row_count_multi_positive():
    assert fods_avg_row_count(_load(MULTI)) > 0.0


# --- fods_total_col_count ---

def test_total_col_count_minimal_is_int():
    assert isinstance(fods_total_col_count(_load(MINIMAL)), int)


def test_total_col_count_minimal_nonnegative():
    assert fods_total_col_count(_load(MINIMAL)) >= 0


def test_total_col_count_multi_positive():
    assert fods_total_col_count(_load(MULTI)) > 0


def test_nonempty_cell_count_formula_positive():
    assert fods_nonempty_cell_count(_load(FORMULA)) > 0
