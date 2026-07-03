"""Tests for sylk_numeric_cell_count and sylk_is_square (Sprint 61)."""
import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src" / "python"))

from sylk.sylk_analytics import sylk_numeric_cell_count, sylk_is_square

SYLK = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "sylk" / "valid"


class TestSylkNumericCellCount:
    def test_minimal_2x2(self):
        assert sylk_numeric_cell_count(SYLK / "minimal-2x2.slk") == 1

    def test_numeric_row(self):
        assert sylk_numeric_cell_count(SYLK / "numeric-row.slk") == 3

    def test_single_cell(self):
        assert sylk_numeric_cell_count(SYLK / "single-cell.slk") == 1

    def test_returns_int(self):
        assert isinstance(sylk_numeric_cell_count(SYLK / "minimal-2x2.slk"), int)

    def test_nonnegative(self):
        for f in ["minimal-2x2.slk", "numeric-row.slk", "single-cell.slk"]:
            assert sylk_numeric_cell_count(SYLK / f) >= 0


class TestSylkIsSquare:
    def test_minimal_2x2_is_square(self):
        assert sylk_is_square(SYLK / "minimal-2x2.slk") is True

    def test_numeric_row_not_square(self):
        assert sylk_is_square(SYLK / "numeric-row.slk") is False

    def test_single_cell_is_square(self):
        assert sylk_is_square(SYLK / "single-cell.slk") is True

    def test_returns_bool(self):
        assert isinstance(sylk_is_square(SYLK / "minimal-2x2.slk"), bool)

    def test_false_for_non_square(self):
        assert sylk_is_square(SYLK / "numeric-row.slk") is False
