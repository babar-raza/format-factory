"""
r319 DIF analytics: dif_max_numeric_int_value, dif_col_count_exceeds_numeric_count.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.dif.dif_parser import dif_max_numeric_int_value, dif_col_count_exceeds_numeric_count

_DIF = _REPO / "samples" / "by-format" / "dif" / "valid"


# --- dif_max_numeric_int_value ---

def test_max_numeric_int_minimal_2x2():
    assert dif_max_numeric_int_value(_DIF / "minimal-2x2.dif") == 99

def test_max_numeric_int_numeric_row():
    assert dif_max_numeric_int_value(_DIF / "numeric-row.dif") == 3

def test_max_numeric_int_single_cell():
    assert dif_max_numeric_int_value(_DIF / "single-cell.dif") == 42

def test_max_numeric_int_returns_int_type():
    result = dif_max_numeric_int_value(_DIF / "minimal-2x2.dif")
    assert isinstance(result, int)

def test_max_numeric_int_minimal_not_zero():
    assert dif_max_numeric_int_value(_DIF / "minimal-2x2.dif") != 0

def test_max_numeric_int_single_greater_than_row():
    assert dif_max_numeric_int_value(_DIF / "single-cell.dif") > dif_max_numeric_int_value(_DIF / "numeric-row.dif")


# --- dif_col_count_exceeds_numeric_count ---

def test_col_exceeds_numeric_minimal_2x2_true():
    assert dif_col_count_exceeds_numeric_count(_DIF / "minimal-2x2.dif") is True

def test_col_exceeds_numeric_numeric_row_false():
    assert dif_col_count_exceeds_numeric_count(_DIF / "numeric-row.dif") is False

def test_col_exceeds_numeric_single_cell_false():
    assert dif_col_count_exceeds_numeric_count(_DIF / "single-cell.dif") is False

def test_col_exceeds_numeric_returns_bool():
    result = dif_col_count_exceeds_numeric_count(_DIF / "minimal-2x2.dif")
    assert isinstance(result, bool)

def test_col_exceeds_numeric_numeric_row_is_bool():
    result = dif_col_count_exceeds_numeric_count(_DIF / "numeric-row.dif")
    assert isinstance(result, bool)

def test_col_exceeds_numeric_only_minimal_true():
    results = [
        dif_col_count_exceeds_numeric_count(_DIF / "minimal-2x2.dif"),
        dif_col_count_exceeds_numeric_count(_DIF / "numeric-row.dif"),
        dif_col_count_exceeds_numeric_count(_DIF / "single-cell.dif"),
    ]
    assert results.count(True) == 1
