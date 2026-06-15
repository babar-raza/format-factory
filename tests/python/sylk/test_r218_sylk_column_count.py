"""Tests for sylk_column_count().

Sprint: product-deepening-rnext88
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.sylk.sylk_parser import sylk_column_count

SYLK_SAMPLES = _REPO / "samples" / "by-format" / "sylk" / "valid"


class TestSylkColumnCount:
    def test_import(self):
        assert callable(sylk_column_count)

    def test_minimal_2x2_has_two_columns(self):
        assert sylk_column_count(SYLK_SAMPLES / "minimal-2x2.slk") == 2

    def test_single_cell_has_one_column(self):
        assert sylk_column_count(SYLK_SAMPLES / "single-cell.slk") == 1

    def test_numeric_row_has_three_columns(self):
        assert sylk_column_count(SYLK_SAMPLES / "numeric-row.slk") == 3

    def test_returns_int(self):
        result = sylk_column_count(SYLK_SAMPLES / "minimal-2x2.slk")
        assert isinstance(result, int)

    def test_positive(self):
        for sample in SYLK_SAMPLES.iterdir():
            if sample.suffix == ".slk":
                assert sylk_column_count(sample) >= 1
