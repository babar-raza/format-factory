"""
test_r165_ods_accessor_deepening.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT30-001
Added: 2026-06-10

Deepening tests for ODS count_sheets, get_all_values, get_cell_count, ods_to_csv.
These functions had minimal (1-2 test) coverage.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods.ods_parser import (
    count_sheets,
    get_all_values,
    get_cell_count,
    ods_to_csv,
    OdsError,
)

_SAMPLES = _REPO / "samples" / "by-format" / "ods" / "valid"


# ── count_sheets deepening ──────────────────────────────────────────────

class TestCountSheetsDeepening:

    def test_returns_positive(self):
        count = count_sheets(_SAMPLES / "minimal-spreadsheet.ods")
        assert count > 0

    def test_consistency_across_files(self):
        for name in ("minimal-spreadsheet.ods", "single-cell.ods", "numeric-row.ods"):
            count = count_sheets(_SAMPLES / name)
            assert isinstance(count, int)
            assert count >= 1

    def test_nonexistent_raises(self):
        with pytest.raises((OdsError, FileNotFoundError)):
            count_sheets(_SAMPLES / "ghost.ods")


# ── get_all_values deepening ────────────────────────────────────────────

class TestGetAllValuesDeepening:

    def test_single_cell(self):
        vals = get_all_values(_SAMPLES / "single-cell.ods")
        assert isinstance(vals, list)
        assert len(vals) >= 1

    def test_numeric_row(self):
        vals = get_all_values(_SAMPLES / "numeric-row.ods")
        assert isinstance(vals, list)
        assert len(vals) >= 1

    def test_out_of_range_sheet_index(self):
        vals = get_all_values(_SAMPLES / "single-cell.ods", sheet_index=999)
        assert vals == []

    def test_negative_sheet_index(self):
        vals = get_all_values(_SAMPLES / "single-cell.ods", sheet_index=-1)
        assert vals == []

    def test_nonexistent_raises(self):
        with pytest.raises((OdsError, FileNotFoundError)):
            get_all_values(_SAMPLES / "ghost.ods")


# ── get_cell_count deepening ────────────────────────────────────────────

class TestGetCellCountDeepening:

    def test_single_cell(self):
        count = get_cell_count(_SAMPLES / "single-cell.ods")
        assert isinstance(count, int)
        assert count >= 1

    def test_numeric_row(self):
        count = get_cell_count(_SAMPLES / "numeric-row.ods")
        assert count >= 1

    def test_out_of_range_sheet_index(self):
        count = get_cell_count(_SAMPLES / "single-cell.ods", sheet_index=999)
        assert count == 0

    def test_nonexistent_raises(self):
        with pytest.raises((OdsError, FileNotFoundError)):
            get_cell_count(_SAMPLES / "ghost.ods")


# ── ods_to_csv deepening ────────────────────────────────────────────────

class TestOdsToCsvDeepening:

    def test_returns_string(self):
        csv_str = ods_to_csv(_SAMPLES / "single-cell.ods")
        assert isinstance(csv_str, str)

    def test_nonempty(self):
        csv_str = ods_to_csv(_SAMPLES / "single-cell.ods")
        assert len(csv_str) > 0

    def test_numeric_row(self):
        csv_str = ods_to_csv(_SAMPLES / "numeric-row.ods")
        assert len(csv_str) > 0

    def test_out_of_range_returns_empty(self):
        csv_str = ods_to_csv(_SAMPLES / "single-cell.ods", sheet_index=999)
        assert csv_str == ""

    def test_nonexistent_raises(self):
        with pytest.raises((OdsError, FileNotFoundError)):
            ods_to_csv(_SAMPLES / "ghost.ods")
