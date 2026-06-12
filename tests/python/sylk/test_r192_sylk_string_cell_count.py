"""Tests for sylk_string_cell_count — rnext61 product deepening."""
import pytest
from pathlib import Path

SYLK_DIR = Path("samples/by-format/sylk/valid")


def test_import():
    from src.python.sylk import sylk_string_cell_count
    assert callable(sylk_string_cell_count)


def test_minimal_2x2_returns_three_string_cells():
    from src.python.sylk import sylk_string_cell_count
    result = sylk_string_cell_count(SYLK_DIR / "minimal-2x2.slk")
    assert result == 3


def test_numeric_row_returns_zero():
    from src.python.sylk import sylk_string_cell_count
    result = sylk_string_cell_count(SYLK_DIR / "numeric-row.slk")
    assert result == 0


def test_single_cell_numeric_returns_zero():
    from src.python.sylk import sylk_string_cell_count
    result = sylk_string_cell_count(SYLK_DIR / "single-cell.slk")
    assert result == 0


def test_returns_int():
    from src.python.sylk import sylk_string_cell_count
    result = sylk_string_cell_count(SYLK_DIR / "minimal-2x2.slk")
    assert isinstance(result, int)


def test_result_nonnegative():
    from src.python.sylk import sylk_string_cell_count
    for fname in ["minimal-2x2.slk", "numeric-row.slk", "single-cell.slk"]:
        result = sylk_string_cell_count(SYLK_DIR / fname)
        assert result >= 0
