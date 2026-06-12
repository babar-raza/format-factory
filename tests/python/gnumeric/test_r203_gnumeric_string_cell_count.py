"""
Tests for gnumeric_string_cell_count — sprint product-deepening-rnext72.

Sprint: FORMAT-FACTORY-ABW-ZST-DEEPENING-001
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
GNUMERIC_SAMPLES = REPO / "samples" / "by-format" / "gnumeric"

sys.path.insert(0, str(REPO / "src" / "python"))

from gnumeric.gnumeric_codec import load, gnumeric_string_cell_count


def test_import():
    assert callable(gnumeric_string_cell_count)


def test_empty_sheet_returns_zero():
    model = load(GNUMERIC_SAMPLES / "empty-sheet.gnumeric")
    result = gnumeric_string_cell_count(model, 0)
    assert result == 0


def test_minimal_spreadsheet_returns_one():
    model = load(GNUMERIC_SAMPLES / "minimal-spreadsheet.gnumeric")
    result = gnumeric_string_cell_count(model, 0)
    assert result == 1


def test_multi_cell_returns_three():
    model = load(GNUMERIC_SAMPLES / "multi-cell-basic.gnumeric")
    result = gnumeric_string_cell_count(model, 0)
    assert result == 3


def test_returns_int():
    model = load(GNUMERIC_SAMPLES / "minimal-spreadsheet.gnumeric")
    result = gnumeric_string_cell_count(model, 0)
    assert isinstance(result, int)


def test_result_nonnegative():
    model = load(GNUMERIC_SAMPLES / "multi-cell-basic.gnumeric")
    result = gnumeric_string_cell_count(model, 0)
    assert result >= 0
