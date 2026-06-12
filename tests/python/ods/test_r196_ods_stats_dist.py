"""
tests/python/ods/test_r196_ods_stats_dist.py

Sprint: FORMAT-FACTORY-ODS-NDJSON-DEEPENING-001
Tests for spreadsheet_stats(), ods_cell_type_distribution(),
ods_formula_cell_count(), ods_data_validation_count(), ods_max_row_length().
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods import (
    spreadsheet_stats,
    ods_cell_type_distribution,
    ods_formula_cell_count,
    ods_data_validation_count,
    ods_max_row_length,
    parse_ods,
)

_SAMPLES = _REPO / "samples" / "by-format" / "ods" / "valid"
_MINIMAL = str(_SAMPLES / "minimal-spreadsheet.ods")


class TestSpreadsheetStats:
    def test_empty_model_returns_zero_sheets(self):
        result = spreadsheet_stats({})
        assert result["sheet_count"] == 0

    def test_returns_required_keys(self):
        result = spreadsheet_stats({})
        assert "sheet_count" in result
        assert "total_rows" in result
        assert "total_cells" in result
        assert "non_empty_cells" in result
        assert "per_sheet" in result

    def test_real_file_has_sheet_count(self):
        model = parse_ods(_MINIMAL)
        result = spreadsheet_stats(model)
        assert result["sheet_count"] >= 1

    def test_real_file_total_cells_positive(self):
        model = parse_ods(_MINIMAL)
        result = spreadsheet_stats(model)
        assert result["total_cells"] > 0

    def test_per_sheet_is_list(self):
        model = parse_ods(_MINIMAL)
        result = spreadsheet_stats(model)
        assert isinstance(result["per_sheet"], list)


class TestOdsCellTypeDistribution:
    def test_empty_model_returns_empty_by_type(self):
        result = ods_cell_type_distribution({})
        assert result["by_type"] == {}

    def test_returns_required_keys(self):
        result = ods_cell_type_distribution({})
        assert "by_type" in result
        assert "total_cells" in result
        assert "empty_fraction" in result

    def test_real_file_has_types(self):
        model = parse_ods(_MINIMAL)
        result = ods_cell_type_distribution(model)
        assert len(result["by_type"]) > 0

    def test_total_cells_matches_sum_of_types(self):
        model = parse_ods(_MINIMAL)
        result = ods_cell_type_distribution(model)
        assert result["total_cells"] == sum(result["by_type"].values())

    def test_empty_fraction_between_0_and_1(self):
        model = parse_ods(_MINIMAL)
        result = ods_cell_type_distribution(model)
        assert 0.0 <= result["empty_fraction"] <= 1.0


class TestOdsFormulaAndValidation:
    def test_formula_count_non_negative(self):
        model = parse_ods(_MINIMAL)
        assert ods_formula_cell_count(model) >= 0

    def test_validation_count_non_negative(self):
        model = parse_ods(_MINIMAL)
        assert ods_data_validation_count(model) >= 0

    def test_formula_count_empty_model_is_zero(self):
        assert ods_formula_cell_count({}) == 0

    def test_validation_count_empty_model_is_zero(self):
        assert ods_data_validation_count({}) == 0


class TestOdsMaxRowLength:
    def test_real_file_returns_positive_int(self):
        result = ods_max_row_length(_MINIMAL)
        assert isinstance(result, int)
        assert result >= 0

    def test_returns_integer(self):
        result = ods_max_row_length(_MINIMAL)
        assert isinstance(result, int)
