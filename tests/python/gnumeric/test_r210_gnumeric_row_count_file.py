"""
Tests for gnumeric_row_count_file — sprint product-deepening-rnext79.

Sprint: FORMAT-FACTORY-ABW-ZST-DEEPENING-001
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
GNUMERIC_SAMPLES = REPO / "samples" / "by-format" / "gnumeric"

sys.path.insert(0, str(REPO / "src" / "python"))

from gnumeric.gnumeric_codec import gnumeric_row_count_file


def test_import():
    assert callable(gnumeric_row_count_file)


def test_empty_sheet_has_zero_rows():
    result = gnumeric_row_count_file(GNUMERIC_SAMPLES / "empty-sheet.gnumeric")
    assert result == 0


def test_minimal_spreadsheet_has_one_row():
    result = gnumeric_row_count_file(GNUMERIC_SAMPLES / "minimal-spreadsheet.gnumeric")
    assert result == 1


def test_multi_cell_basic_has_two_rows():
    result = gnumeric_row_count_file(GNUMERIC_SAMPLES / "multi-cell-basic.gnumeric")
    assert result == 2


def test_returns_int():
    result = gnumeric_row_count_file(GNUMERIC_SAMPLES / "empty-sheet.gnumeric")
    assert isinstance(result, int)


def test_result_nonnegative():
    result = gnumeric_row_count_file(GNUMERIC_SAMPLES / "minimal-spreadsheet.gnumeric")
    assert result >= 0
