"""
Tests for tsv_row_count — sprint product-deepening-rnext77.

Sprint: FORMAT-FACTORY-ABW-ZST-DEEPENING-001
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
TSV_SAMPLES = REPO / "samples" / "by-format" / "tsv"

sys.path.insert(0, str(REPO / "src" / "python"))

from tsv.tsv_parser import tsv_row_count


def test_import():
    assert callable(tsv_row_count)


def test_minimal_2x2_has_two_rows():
    result = tsv_row_count(TSV_SAMPLES / "minimal-2x2.tsv")
    assert result == 2


def test_single_cell_has_one_row():
    result = tsv_row_count(TSV_SAMPLES / "single-cell.tsv")
    assert result == 1


def test_multi_column_has_two_rows():
    result = tsv_row_count(TSV_SAMPLES / "multi-column.tsv")
    assert result == 2


def test_returns_int():
    result = tsv_row_count(TSV_SAMPLES / "minimal-2x2.tsv")
    assert isinstance(result, int)


def test_result_nonnegative():
    result = tsv_row_count(TSV_SAMPLES / "single-cell.tsv")
    assert result >= 0
