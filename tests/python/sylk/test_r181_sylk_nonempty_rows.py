"""
tests/python/sylk/test_r181_sylk_nonempty_rows.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT49-001
Tests for sylk_nonempty_rows() — count rows with at least one non-empty cell.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.sylk.sylk_parser import sylk_nonempty_rows

SAMPLES = _REPO / "samples" / "by-format" / "sylk" / "valid"


class TestSylkNonemptyRows:
    def test_minimal_2x2_two_nonempty_rows(self):
        result = sylk_nonempty_rows(SAMPLES / "minimal-2x2.slk")
        assert result == 2

    def test_numeric_row_one_nonempty_row(self):
        result = sylk_nonempty_rows(SAMPLES / "numeric-row.slk")
        assert result == 1

    def test_single_cell_one_nonempty_row(self):
        result = sylk_nonempty_rows(SAMPLES / "single-cell.slk")
        assert result == 1

    def test_returns_int(self):
        result = sylk_nonempty_rows(SAMPLES / "single-cell.slk")
        assert isinstance(result, int)

    def test_non_negative(self):
        result = sylk_nonempty_rows(SAMPLES / "single-cell.slk")
        assert result >= 0

    def test_exported_from_init(self):
        from src.python.sylk import sylk_nonempty_rows as fn
        result = fn(SAMPLES / "minimal-2x2.slk")
        assert result == 2
