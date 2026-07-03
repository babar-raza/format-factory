"""
Tests for ods_string_cell_count — sprint product-deepening-rnext76.

Sprint: FORMAT-FACTORY-ABW-ZST-DEEPENING-001
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
ODS_SAMPLES = REPO / "samples" / "by-format" / "ods" / "valid"

sys.path.insert(0, str(REPO / "src" / "python"))

from ods.ods_analytics import ods_string_cell_count


def test_import():
    assert callable(ods_string_cell_count)


def test_minimal_spreadsheet_has_three_string_cells():
    result = ods_string_cell_count(ODS_SAMPLES / "minimal-spreadsheet.ods")
    assert result == 3


def test_single_cell_has_one_string_cell():
    result = ods_string_cell_count(ODS_SAMPLES / "single-cell.ods")
    assert result == 1


def test_numeric_row_has_no_string_cells():
    result = ods_string_cell_count(ODS_SAMPLES / "numeric-row.ods")
    assert result == 0


def test_returns_int():
    result = ods_string_cell_count(ODS_SAMPLES / "minimal-spreadsheet.ods")
    assert isinstance(result, int)


def test_result_nonnegative():
    result = ods_string_cell_count(ODS_SAMPLES / "single-cell.ods")
    assert result >= 0
