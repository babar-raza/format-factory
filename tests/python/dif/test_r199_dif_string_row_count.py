"""
Tests for dif_string_row_count — sprint product-deepening-rnext68.

Sprint: FORMAT-FACTORY-ABW-ZST-DEEPENING-001
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
DIF_SAMPLES = REPO / "samples" / "by-format" / "dif" / "valid"

sys.path.insert(0, str(REPO / "src" / "python"))

from dif.dif_parser import dif_string_row_count


def test_import():
    assert callable(dif_string_row_count)


def test_minimal_2x2_has_one_string_row():
    result = dif_string_row_count(DIF_SAMPLES / "minimal-2x2.dif")
    assert result == 1


def test_numeric_row_has_no_string_rows():
    result = dif_string_row_count(DIF_SAMPLES / "numeric-row.dif")
    assert result == 0


def test_single_cell_has_no_string_rows():
    result = dif_string_row_count(DIF_SAMPLES / "single-cell.dif")
    assert result == 0


def test_returns_int():
    result = dif_string_row_count(DIF_SAMPLES / "minimal-2x2.dif")
    assert isinstance(result, int)


def test_result_nonnegative():
    result = dif_string_row_count(DIF_SAMPLES / "numeric-row.dif")
    assert result >= 0
