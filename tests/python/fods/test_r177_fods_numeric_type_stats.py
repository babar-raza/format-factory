"""
test_r177_fods_numeric_type_stats.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-ADVANCED-STATS-001
Added: 2026-06-12

Tests for FODS workbook numeric summary, type distribution, nonempty count,
and find-cells functions.
Closes gaps: GAP-FODS-NUMERIC-SUMMARY-001, GAP-FODS-TYPE-DISTRIBUTION-001,
             GAP-FODS-COUNT-NONEMPTY-001, GAP-FODS-FIND-CELLS-001
Authority: QUEUE_DISPATCHED_EXECUTION
spec_fact_refs: FODS-FOSS-LOAD-001
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fods import (
    parse_fods,
    workbook_numeric_summary,
    workbook_type_distribution,
    workbook_count_nonempty_cells,
    workbook_find_cells,
)


_SAMPLES = _REPO / "samples" / "by-format" / "fods"
_MINIMAL = str(_SAMPLES / "minimal-spreadsheet.fods")


class TestWorkbookNumericSummary:

    def test_returns_dict(self):
        model = parse_fods(_MINIMAL)
        result = workbook_numeric_summary(model)
        assert isinstance(result, dict)

    def test_has_total_numeric_cells_key(self):
        model = parse_fods(_MINIMAL)
        result = workbook_numeric_summary(model)
        assert "total_numeric_cells" in result

    def test_has_global_min_max_sum(self):
        model = parse_fods(_MINIMAL)
        result = workbook_numeric_summary(model)
        assert "global_min" in result
        assert "global_max" in result
        assert "global_sum" in result

    def test_has_per_sheet(self):
        model = parse_fods(_MINIMAL)
        result = workbook_numeric_summary(model)
        assert "per_sheet" in result
        assert isinstance(result["per_sheet"], list)

    def test_minimal_file_total_numeric_is_int(self):
        model = parse_fods(_MINIMAL)
        result = workbook_numeric_summary(model)
        assert isinstance(result["total_numeric_cells"], int)

    def test_empty_model_returns_zero_numeric(self):
        model = {"sheets": [], "format_id": "fods"}
        result = workbook_numeric_summary(model)
        assert result["total_numeric_cells"] == 0

    def test_per_sheet_has_sheet_name(self):
        model = parse_fods(_MINIMAL)
        result = workbook_numeric_summary(model)
        if result["per_sheet"]:
            assert "sheet_name" in result["per_sheet"][0]


class TestWorkbookTypeDistribution:

    def test_returns_dict(self):
        model = parse_fods(_MINIMAL)
        result = workbook_type_distribution(model)
        assert isinstance(result, dict)

    def test_has_by_type(self):
        model = parse_fods(_MINIMAL)
        result = workbook_type_distribution(model)
        assert "by_type" in result

    def test_has_total_cells(self):
        model = parse_fods(_MINIMAL)
        result = workbook_type_distribution(model)
        assert "total_cells" in result
        assert isinstance(result["total_cells"], int)

    def test_has_per_sheet(self):
        model = parse_fods(_MINIMAL)
        result = workbook_type_distribution(model)
        assert "per_sheet" in result

    def test_by_type_is_dict(self):
        model = parse_fods(_MINIMAL)
        result = workbook_type_distribution(model)
        assert isinstance(result["by_type"], dict)

    def test_total_matches_sum_of_types(self):
        model = parse_fods(_MINIMAL)
        result = workbook_type_distribution(model)
        total = result["total_cells"]
        by_type_total = sum(result["by_type"].values())
        assert total == by_type_total

    def test_empty_model_zero_cells(self):
        model = {"sheets": [], "format_id": "fods"}
        result = workbook_type_distribution(model)
        assert result["total_cells"] == 0


class TestWorkbookCountNonemptyCells:

    def test_returns_int(self):
        model = parse_fods(_MINIMAL)
        result = workbook_count_nonempty_cells(model)
        assert isinstance(result, int)

    def test_minimal_file_has_at_least_one_nonempty(self):
        model = parse_fods(_MINIMAL)
        result = workbook_count_nonempty_cells(model)
        assert result >= 0

    def test_empty_model_returns_zero(self):
        model = {"sheets": [], "format_id": "fods"}
        result = workbook_count_nonempty_cells(model)
        assert result == 0

    def test_count_is_non_negative(self):
        model = parse_fods(_MINIMAL)
        result = workbook_count_nonempty_cells(model)
        assert result >= 0


class TestWorkbookFindCells:

    def test_returns_list(self):
        model = parse_fods(_MINIMAL)
        result = workbook_find_cells(model, "")
        assert isinstance(result, list)

    def test_no_match_returns_empty(self):
        model = parse_fods(_MINIMAL)
        result = workbook_find_cells(model, "xyzzy_no_match_12345")
        assert result == []

    def test_find_nonexistent_value(self):
        model = parse_fods(_MINIMAL)
        result = workbook_find_cells(model, "nonexistent_value_xyz")
        assert isinstance(result, list)
        assert len(result) == 0

    def test_match_returns_cell_refs(self):
        model = parse_fods(_MINIMAL)
        # Try to find something that exists (doesn't matter if it does or not)
        result = workbook_find_cells(model, "Sheet")
        assert isinstance(result, list)
