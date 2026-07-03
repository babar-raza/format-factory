"""
Tests for sylk_max_column_index — sprint product-deepening-rnext69.

Sprint: FORMAT-FACTORY-ABW-ZST-DEEPENING-001
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SYLK_SAMPLES = REPO / "samples" / "by-format" / "sylk" / "valid"

sys.path.insert(0, str(REPO / "src" / "python"))

from sylk.sylk_analytics import sylk_max_column_index


def test_import():
    assert callable(sylk_max_column_index)


def test_minimal_2x2_max_col_is_two():
    result = sylk_max_column_index(SYLK_SAMPLES / "minimal-2x2.slk")
    assert result == 2


def test_numeric_row_max_col_is_three():
    result = sylk_max_column_index(SYLK_SAMPLES / "numeric-row.slk")
    assert result == 3


def test_single_cell_max_col_is_one():
    result = sylk_max_column_index(SYLK_SAMPLES / "single-cell.slk")
    assert result == 1


def test_returns_int():
    result = sylk_max_column_index(SYLK_SAMPLES / "minimal-2x2.slk")
    assert isinstance(result, int)


def test_result_nonnegative():
    result = sylk_max_column_index(SYLK_SAMPLES / "single-cell.slk")
    assert result >= 0
