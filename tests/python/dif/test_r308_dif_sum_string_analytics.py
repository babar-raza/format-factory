"""
Sprint r308: Tests for dif_numeric_sum_per_cell and dif_has_string_rows.
12 tests total (6 per function).
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.dif.dif_parser import dif_numeric_sum_per_cell, dif_has_string_rows

_D = _REPO / "samples" / "by-format" / "dif" / "valid"
_MINIMAL = _D / "minimal-2x2.dif"
_NUMERIC = _D / "numeric-row.dif"
_SINGLE = _D / "single-cell.dif"


# --- dif_numeric_sum_per_cell ---

def test_numeric_sum_per_cell_minimal_returns_float():
    assert isinstance(dif_numeric_sum_per_cell(_MINIMAL), float)

def test_numeric_sum_per_cell_minimal_is_17_625():
    # minimal-2x2: numsum=141, 8 cells → 17.625
    assert dif_numeric_sum_per_cell(_MINIMAL) == 17.625

def test_numeric_sum_per_cell_numeric_is_2():
    # numeric-row: sum=6, 3 cells → 2.0
    assert dif_numeric_sum_per_cell(_NUMERIC) == 2.0

def test_numeric_sum_per_cell_single_is_42():
    # single-cell: sum=42, 1 cell → 42.0
    assert dif_numeric_sum_per_cell(_SINGLE) == 42.0

def test_numeric_sum_per_cell_all_distinct():
    vals = [dif_numeric_sum_per_cell(p) for p in [_MINIMAL, _NUMERIC, _SINGLE]]
    assert len(set(vals)) == 3

def test_numeric_sum_per_cell_single_greater_than_numeric():
    assert dif_numeric_sum_per_cell(_SINGLE) > dif_numeric_sum_per_cell(_NUMERIC)


# --- dif_has_string_rows ---

def test_has_string_rows_minimal_returns_bool():
    assert isinstance(dif_has_string_rows(_MINIMAL), bool)

def test_has_string_rows_minimal_is_true():
    # minimal-2x2 has 6 string cells
    assert dif_has_string_rows(_MINIMAL) is True

def test_has_string_rows_numeric_is_false():
    # numeric-row has only numeric cells
    assert dif_has_string_rows(_NUMERIC) is False

def test_has_string_rows_single_is_false():
    # single-cell has only a numeric value
    assert dif_has_string_rows(_SINGLE) is False

def test_has_string_rows_only_minimal_is_true():
    results = [dif_has_string_rows(p) for p in [_MINIMAL, _NUMERIC, _SINGLE]]
    assert results.count(True) == 1
    assert results.count(False) == 2

def test_has_string_rows_consistent_with_sum_per_cell():
    # minimal has strings AND highest per-cell sum of 17.625
    assert dif_has_string_rows(_MINIMAL) is True
    assert dif_numeric_sum_per_cell(_MINIMAL) == 17.625
