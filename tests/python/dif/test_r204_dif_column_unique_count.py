"""
Tests for dif_column_unique_count — sprint product-deepening-rnext73.

Sprint: FORMAT-FACTORY-ABW-ZST-DEEPENING-001
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
DIF_SAMPLES = REPO / "samples" / "by-format" / "dif" / "valid"

sys.path.insert(0, str(REPO / "src" / "python"))

from dif.dif_parser import dif_column_unique_count


def test_import():
    assert callable(dif_column_unique_count)


def test_minimal_2x2_col0_one_unique():
    result = dif_column_unique_count(DIF_SAMPLES / "minimal-2x2.dif", 0)
    assert result == 1


def test_numeric_row_col0_one_unique():
    result = dif_column_unique_count(DIF_SAMPLES / "numeric-row.dif", 0)
    assert result == 1


def test_single_cell_col0_one_unique():
    result = dif_column_unique_count(DIF_SAMPLES / "single-cell.dif", 0)
    assert result == 1


def test_returns_int():
    result = dif_column_unique_count(DIF_SAMPLES / "minimal-2x2.dif", 0)
    assert isinstance(result, int)


def test_out_of_range_col_returns_zero():
    result = dif_column_unique_count(DIF_SAMPLES / "single-cell.dif", 99)
    assert result == 0
