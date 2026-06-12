"""
Tests for sylk_empty_cell_count — sprint product-deepening-rnext71.

Sprint: FORMAT-FACTORY-ABW-ZST-DEEPENING-001
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SYLK_SAMPLES = REPO / "samples" / "by-format" / "sylk" / "valid"

sys.path.insert(0, str(REPO / "src" / "python"))

from sylk.sylk_parser import sylk_empty_cell_count


def test_import():
    assert callable(sylk_empty_cell_count)


def test_minimal_2x2_no_empty_cells():
    result = sylk_empty_cell_count(SYLK_SAMPLES / "minimal-2x2.slk")
    assert result == 0


def test_numeric_row_no_empty_cells():
    result = sylk_empty_cell_count(SYLK_SAMPLES / "numeric-row.slk")
    assert result == 0


def test_single_cell_no_empty_cells():
    result = sylk_empty_cell_count(SYLK_SAMPLES / "single-cell.slk")
    assert result == 0


def test_returns_int():
    result = sylk_empty_cell_count(SYLK_SAMPLES / "minimal-2x2.slk")
    assert isinstance(result, int)


def test_result_nonnegative():
    result = sylk_empty_cell_count(SYLK_SAMPLES / "numeric-row.slk")
    assert result >= 0
