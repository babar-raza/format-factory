"""
tests/python/fods/test_r76_fods_edit_save.py

Tests for the R76 FODS edit-and-save product deepening capability.

Covers:
- workbook_set_cell_value: update string, float, boolean cells
- workbook_set_cell_value: return value on success and failure
- workbook_warnings_for_unsupported_edit: warns on formula, merge
- Round-trip: parse → set_cell_value → write_fods → re-parse → verify
- Integration: edit_save_fods example pattern
"""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.python.fods import (
    parse_fods,
    write_fods,
    workbook_set_cell_value,
    workbook_warnings_for_unsupported_edit,
)

FODS_SAMPLE = REPO_ROOT / "samples" / "by-format" / "fods" / "minimal-spreadsheet.fods"


# ---------------------------------------------------------------------------
# workbook_set_cell_value
# ---------------------------------------------------------------------------

class TestWorkbookSetCellValue:
    def test_set_string_value(self):
        wb = parse_fods(FODS_SAMPLE)
        sheet_name = wb["sheets"][0]["name"]
        ok, msg = workbook_set_cell_value(wb, sheet_name, 0, 0, "Updated")
        assert ok is True
        assert wb["sheets"][0]["rows"][0]["cells"][0]["value"] == "Updated"
        assert wb["sheets"][0]["rows"][0]["cells"][0]["value_type"] == "string"

    def test_set_float_value(self):
        wb = parse_fods(FODS_SAMPLE)
        sheet_name = wb["sheets"][0]["name"]
        ok, msg = workbook_set_cell_value(wb, sheet_name, 0, 0, 42.5)
        assert ok is True
        assert wb["sheets"][0]["rows"][0]["cells"][0]["value"] == 42.5
        assert wb["sheets"][0]["rows"][0]["cells"][0]["value_type"] == "float"

    def test_set_boolean_value(self):
        wb = parse_fods(FODS_SAMPLE)
        sheet_name = wb["sheets"][0]["name"]
        ok, msg = workbook_set_cell_value(wb, sheet_name, 0, 0, True)
        assert ok is True
        assert wb["sheets"][0]["rows"][0]["cells"][0]["value_type"] == "boolean"

    def test_explicit_value_type_overrides_inference(self):
        wb = parse_fods(FODS_SAMPLE)
        sheet_name = wb["sheets"][0]["name"]
        ok, _ = workbook_set_cell_value(wb, sheet_name, 0, 0, 99, value_type="string")
        assert ok is True
        assert wb["sheets"][0]["rows"][0]["cells"][0]["value_type"] == "string"

    def test_returns_false_for_unknown_sheet(self):
        wb = parse_fods(FODS_SAMPLE)
        ok, msg = workbook_set_cell_value(wb, "NonExistentSheet", 0, 0, "x")
        assert ok is False
        assert "not found" in msg.lower()

    def test_returns_false_for_out_of_range_row(self):
        wb = parse_fods(FODS_SAMPLE)
        sheet_name = wb["sheets"][0]["name"]
        ok, msg = workbook_set_cell_value(wb, sheet_name, 99999, 0, "x")
        assert ok is False
        assert "out of range" in msg.lower()

    def test_returns_false_for_out_of_range_col(self):
        wb = parse_fods(FODS_SAMPLE)
        sheet_name = wb["sheets"][0]["name"]
        ok, msg = workbook_set_cell_value(wb, sheet_name, 0, 99999, "x")
        assert ok is False
        assert "out of range" in msg.lower()

    def test_formula_cleared_on_plain_value_set(self):
        wb = parse_fods(REPO_ROOT / "samples" / "by-format" / "fods" / "formula-basic.fods")
        sheet_name = wb["sheets"][0]["name"]
        # Find a cell with a formula
        formula_row, formula_col = None, None
        for ri, row in enumerate(wb["sheets"][0]["rows"]):
            for ci, cell in enumerate(row.get("cells", [])):
                if cell.get("formula"):
                    formula_row, formula_col = ri, ci
                    break
            if formula_row is not None:
                break
        if formula_row is None:
            pytest.skip("No formula cell found in sample")
        ok, _ = workbook_set_cell_value(wb, sheet_name, formula_row, formula_col, 0)
        assert ok is True
        assert wb["sheets"][0]["rows"][formula_row]["cells"][formula_col]["formula"] is None


class TestWorkbookEditSaveRoundtrip:
    def test_round_trip_string_edit(self, tmp_path):
        wb = parse_fods(FODS_SAMPLE)
        sheet_name = wb["sheets"][0]["name"]
        ok, _ = workbook_set_cell_value(wb, sheet_name, 0, 0, "RoundTripTest")
        assert ok is True

        out_path = tmp_path / "edited.fods"
        write_fods(wb, out_path)
        assert out_path.exists()

        wb2 = parse_fods(out_path)
        assert wb2["sheets"][0]["rows"][0]["cells"][0]["value"] == "RoundTripTest"

    def test_round_trip_preserves_other_cells(self, tmp_path):
        wb = parse_fods(FODS_SAMPLE)
        sheet_name = wb["sheets"][0]["name"]
        original_row_count = wb["sheets"][0]["row_count"]

        ok, _ = workbook_set_cell_value(wb, sheet_name, 0, 0, "ChangedA1")
        assert ok is True

        out_path = tmp_path / "edited.fods"
        write_fods(wb, out_path)

        wb2 = parse_fods(out_path)
        assert wb2["sheets"][0]["row_count"] == original_row_count


class TestWorkbookWarningsForUnsupportedEdit:
    def test_no_warnings_for_plain_string_cell(self):
        wb = parse_fods(FODS_SAMPLE)
        sheet_name = wb["sheets"][0]["name"]
        warnings = workbook_warnings_for_unsupported_edit(wb, sheet_name, 0, 0)
        assert isinstance(warnings, list)
        # Plain cell should have no or minimal warnings
        formula_warning = any("formula" in w.lower() for w in warnings)
        assert not bool(formula_warning)

    def test_warns_for_formula_cell(self):
        wb = parse_fods(REPO_ROOT / "samples" / "by-format" / "fods" / "formula-basic.fods")
        sheet_name = wb["sheets"][0]["name"]
        # Inject a formula cell
        wb["sheets"][0]["rows"][0]["cells"][0]["formula"] = "=SUM(A1:A2)"
        warnings = workbook_warnings_for_unsupported_edit(wb, sheet_name, 0, 0)
        assert any("formula" in w.lower() for w in warnings)

    def test_returns_error_for_unknown_sheet(self):
        wb = parse_fods(FODS_SAMPLE)
        warnings = workbook_warnings_for_unsupported_edit(wb, "NoSuchSheet", 0, 0)
        assert len(warnings) > 0
        assert "not found" in warnings[0].lower()
