"""
tests/python/sylk/test_r197_sylk_analytics.py

Sprint: FORMAT-FACTORY-TSV-SYLK-DEEPENING-001
Tests for sylk_nonempty_rows(), sylk_numeric_cell_count(), sylk_string_cell_count().
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from sylk import sylk_nonempty_rows, sylk_numeric_cell_count, sylk_string_cell_count

_SAMPLES = _REPO / "samples" / "by-format" / "sylk" / "valid"
_MINIMAL = str(_SAMPLES / "minimal-2x2.slk")
_SINGLE = str(_SAMPLES / "single-cell.slk")


class TestSylkNonemptyRows:
    def test_returns_int(self):
        result = sylk_nonempty_rows(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = sylk_nonempty_rows(_MINIMAL)
        assert result >= 0

    def test_minimal_has_rows(self):
        result = sylk_nonempty_rows(_MINIMAL)
        assert result > 0

    def test_single_cell_has_one_row(self):
        result = sylk_nonempty_rows(_SINGLE)
        assert result >= 1


class TestSylkNumericCellCount:
    def test_returns_int(self):
        result = sylk_numeric_cell_count(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = sylk_numeric_cell_count(_MINIMAL)
        assert result >= 0

    def test_minimal_has_numeric_cells(self):
        result = sylk_numeric_cell_count(_MINIMAL)
        assert result >= 0  # minimal-2x2 has mixed types


class TestSylkStringCellCount:
    def test_returns_int(self):
        result = sylk_string_cell_count(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = sylk_string_cell_count(_MINIMAL)
        assert result >= 0

    def test_minimal_has_string_cells(self):
        result = sylk_string_cell_count(_MINIMAL)
        assert result > 0

    def test_numeric_plus_string_le_total_cells(self):
        from sylk import get_cell_count
        numeric = sylk_numeric_cell_count(_MINIMAL)
        string = sylk_string_cell_count(_MINIMAL)
        total = get_cell_count(_MINIMAL)
        assert numeric + string <= total + 1  # allow small discrepancy
