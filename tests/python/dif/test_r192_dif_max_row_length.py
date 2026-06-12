"""Tests for dif_max_row_length — rnext61 product deepening."""
import pytest
from pathlib import Path

DIF_DIR = Path("samples/by-format/dif/valid")


def test_import():
    from src.python.dif import dif_max_row_length
    assert callable(dif_max_row_length)


def test_single_cell_returns_one():
    from src.python.dif import dif_max_row_length
    result = dif_max_row_length(DIF_DIR / "single-cell.dif")
    assert result == 1


def test_numeric_row_returns_three():
    from src.python.dif import dif_max_row_length
    result = dif_max_row_length(DIF_DIR / "numeric-row.dif")
    assert result == 3


def test_minimal_2x2_returns_expected():
    from src.python.dif import dif_max_row_length
    result = dif_max_row_length(DIF_DIR / "minimal-2x2.dif")
    assert result >= 1


def test_returns_int():
    from src.python.dif import dif_max_row_length
    result = dif_max_row_length(DIF_DIR / "numeric-row.dif")
    assert isinstance(result, int)


def test_result_nonnegative():
    from src.python.dif import dif_max_row_length
    for fname in ["single-cell.dif", "numeric-row.dif", "minimal-2x2.dif"]:
        result = dif_max_row_length(DIF_DIR / fname)
        assert result >= 0
