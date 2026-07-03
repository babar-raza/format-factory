"""
tests/python/sylk/test_r186_sylk_numeric_cell_count.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT54-001
Tests for sylk_numeric_cell_count() — count of numeric cells.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.sylk.sylk_analytics import sylk_numeric_cell_count

SAMPLES = _REPO / "samples" / "by-format" / "sylk" / "valid"


class TestSylkNumericCellCount:
    def test_minimal_2x2_has_one_numeric(self):
        result = sylk_numeric_cell_count(SAMPLES / "minimal-2x2.slk")
        assert result == 1

    def test_numeric_row_has_three_numerics(self):
        result = sylk_numeric_cell_count(SAMPLES / "numeric-row.slk")
        assert result == 3

    def test_single_cell_has_one_numeric(self):
        result = sylk_numeric_cell_count(SAMPLES / "single-cell.slk")
        assert result == 1

    def test_returns_int(self):
        result = sylk_numeric_cell_count(SAMPLES / "single-cell.slk")
        assert isinstance(result, int)

    def test_non_negative(self):
        result = sylk_numeric_cell_count(SAMPLES / "minimal-2x2.slk")
        assert result >= 0

    def test_exported_from_init(self):
        from src.python.sylk import sylk_numeric_cell_count as fn
        result = fn(SAMPLES / "numeric-row.slk")
        assert result == 3
