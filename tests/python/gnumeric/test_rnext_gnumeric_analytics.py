"""Product deepening tests for Gnumeric analytics functions.

Tests gnumeric_sheet_summary, gnumeric_numeric_cell_count,
gnumeric_string_cell_count, gnumeric_column_count_file,
gnumeric_row_count_file, gnumeric_cell_count_file.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.gnumeric import (
    load,
    gnumeric_sheet_summary,
    gnumeric_numeric_cell_count,
    gnumeric_string_cell_count,
    gnumeric_column_count_file,
    gnumeric_row_count_file,
    gnumeric_cell_count_file,
)

SAMPLES = _REPO / "samples" / "by-format" / "gnumeric"
MINIMAL = SAMPLES / "minimal-spreadsheet.gnumeric"
MULTI = SAMPLES / "multi-cell-basic.gnumeric"
EMPTY = SAMPLES / "empty-sheet.gnumeric"


@pytest.fixture
def minimal_model():
    return load(str(MINIMAL))


@pytest.fixture
def multi_model():
    return load(str(MULTI))


@pytest.fixture
def empty_model():
    return load(str(EMPTY))


class TestGnumericSheetSummary:
    def test_summary_has_required_keys(self, minimal_model):
        summary = gnumeric_sheet_summary(minimal_model, 0)
        assert "row_count" in summary
        assert "col_count" in summary
        assert "nonempty_cells" in summary

    def test_summary_values_nonnegative(self, minimal_model):
        summary = gnumeric_sheet_summary(minimal_model, 0)
        assert summary["row_count"] >= 0
        assert summary["col_count"] >= 0
        assert summary["nonempty_cells"] >= 0

    def test_empty_sheet_summary(self, empty_model):
        summary = gnumeric_sheet_summary(empty_model, 0)
        assert summary["nonempty_cells"] == 0


class TestGnumericNumericCellCount:
    def test_numeric_count_nonnegative(self, minimal_model):
        count = gnumeric_numeric_cell_count(minimal_model, 0)
        assert isinstance(count, int)
        assert count >= 0

    def test_empty_sheet_zero_numeric(self, empty_model):
        count = gnumeric_numeric_cell_count(empty_model, 0)
        assert count == 0


class TestGnumericStringCellCount:
    def test_string_count_nonnegative(self, minimal_model):
        count = gnumeric_string_cell_count(minimal_model, 0)
        assert isinstance(count, int)
        assert count >= 0

    def test_empty_sheet_zero_strings(self, empty_model):
        count = gnumeric_string_cell_count(empty_model, 0)
        assert count == 0


class TestGnumericFileApis:
    def test_column_count_file(self):
        count = gnumeric_column_count_file(str(MINIMAL))
        assert isinstance(count, int)
        assert count >= 1

    def test_row_count_file(self):
        count = gnumeric_row_count_file(str(MINIMAL))
        assert isinstance(count, int)
        assert count >= 1

    def test_cell_count_file(self):
        count = gnumeric_cell_count_file(str(MINIMAL))
        assert isinstance(count, int)
        assert count >= 1

    def test_multi_cell_counts_consistent(self):
        cell_count = gnumeric_cell_count_file(str(MULTI))
        row_count = gnumeric_row_count_file(str(MULTI))
        col_count = gnumeric_column_count_file(str(MULTI))
        assert cell_count >= 1
        assert row_count >= 1
        assert col_count >= 1
        # Cells can't exceed theoretical grid
        assert cell_count <= row_count * col_count

    def test_empty_sheet_file_apis(self):
        assert gnumeric_cell_count_file(str(EMPTY)) == 0
        assert gnumeric_row_count_file(str(EMPTY)) == 0
        assert gnumeric_column_count_file(str(EMPTY)) == 0
