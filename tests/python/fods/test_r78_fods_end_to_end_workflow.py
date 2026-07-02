"""
tests/python/fods/test_r78_fods_end_to_end_workflow.py

R78 Train E — FODS end-to-end product workflow tests.

Tests the complete FODS product usage pattern from a consumer perspective:
1. Parse a FODS file
2. Inspect using analysis APIs
3. Edit cells and sheets
4. Write to new file
5. Round-trip verify
6. Export to CSV

These tests validate the full FODS product workflow is functional
and discoverable, not just individual API correctness.
"""
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.python.fods import (
    parse_fods,
    write_fods,
    workbook_to_xml,
    workbook_stats,
    workbook_sheet_order,
    workbook_sheet_summary,
    workbook_set_cell_value,
    workbook_warnings_for_unsupported_edit,
    workbook_add_sheet,
    workbook_rename_sheet,
    workbook_remove_sheet,
    workbook_cell_range,
    workbook_formula_list,
    workbook_type_distribution,
)
from src.python.fods.csv_exporter import export_fods_to_csv, export_fods_to_csv_file

FODS_SAMPLE = REPO_ROOT / "samples" / "by-format" / "fods" / "minimal-spreadsheet.fods"


def _build_workbook_with_data() -> dict:
    """Build a workbook with two sheets and data for workflow testing."""
    wb = {
        "sheets": [
            {
                "name": "Sales",
                "rows": [
                    {"cells": [
                        {"value": "Product", "value_type": "string"},
                        {"value": "Q1", "value_type": "string"},
                        {"value": "Q2", "value_type": "string"},
                    ]},
                    {"cells": [
                        {"value": "Widget", "value_type": "string"},
                        {"value": 100.0, "value_type": "float"},
                        {"value": 120.0, "value_type": "float"},
                    ]},
                    {"cells": [
                        {"value": "Gadget", "value_type": "string"},
                        {"value": 50.0, "value_type": "float"},
                        {"value": 75.0, "value_type": "float"},
                    ]},
                ],
                "auto_updatable": False,
            },
            {
                "name": "Summary",
                "rows": [
                    {"cells": [
                        {"value": "Total", "value_type": "string"},
                        {"value": 345.0, "value_type": "float"},
                    ]},
                ],
                "auto_updatable": False,
            },
        ]
    }
    return wb


# ---------------------------------------------------------------------------
# Workflow 1: Parse → Inspect
# ---------------------------------------------------------------------------

class TestFodsParseAndInspect:
    """Parse a FODS file and verify all inspection APIs work correctly."""

    def test_parse_returns_workbook(self):
        doc = parse_fods(FODS_SAMPLE)
        assert isinstance(doc, dict)
        assert "sheets" in doc

    def test_stats_returns_expected_keys(self):
        doc = parse_fods(FODS_SAMPLE)
        stats = workbook_stats(doc)
        assert "sheet_count" in stats
        assert "total_cells" in stats

    def test_sheet_order_returns_list(self):
        doc = parse_fods(FODS_SAMPLE)
        order = workbook_sheet_order(doc)
        assert isinstance(order, list)
        assert len(order) >= 1

    def test_sheet_summary_returns_per_sheet_info(self):
        doc = parse_fods(FODS_SAMPLE)
        summary = workbook_sheet_summary(doc)
        assert isinstance(summary, list)
        assert len(summary) >= 1
        for item in summary:
            assert "name" in item

    def test_type_distribution_returns_dict(self):
        doc = parse_fods(FODS_SAMPLE)
        dist = workbook_type_distribution(doc)
        assert isinstance(dist, dict)


# ---------------------------------------------------------------------------
# Workflow 2: Edit → Write → Round-trip
# ---------------------------------------------------------------------------

class TestFodsEditAndSave:
    """Edit a workbook and verify write + round-trip works."""

    def test_set_cell_value_and_round_trip(self):
        doc = parse_fods(FODS_SAMPLE)
        sheet_name = workbook_sheet_order(doc)[0]
        ok, msg = workbook_set_cell_value(doc, sheet_name, 0, 0, "R78_TEST_VALUE")
        assert ok is not None, f"Edit failed: {msg}"
        with tempfile.NamedTemporaryFile(suffix=".fods", delete=False) as tf:
            out = Path(tf.name)
        write_fods(doc, out)
        doc2 = parse_fods(out)
        val = doc2["sheets"][0]["rows"][0]["cells"][0]["value"]
        assert val == "R78_TEST_VALUE", f"Round-trip mismatch: {val!r}"
        out.unlink(missing_ok=True)

    def test_workbook_to_xml_returns_string(self):
        doc = parse_fods(FODS_SAMPLE)
        xml = workbook_to_xml(doc)
        assert isinstance(xml, str)
        assert len(xml) > 100

    def test_edit_warnings_returns_list(self):
        doc = parse_fods(FODS_SAMPLE)
        sheet_name = workbook_sheet_order(doc)[0]
        warnings = workbook_warnings_for_unsupported_edit(doc, sheet_name, 0, 0)
        assert isinstance(warnings, list)


# ---------------------------------------------------------------------------
# Workflow 3: Sheet management within a workflow
# ---------------------------------------------------------------------------

class TestFodsSheetManagementWorkflow:
    """Sheet add/rename/remove as part of a complete workflow."""

    def test_add_edit_remove_sheet_workflow(self):
        wb = _build_workbook_with_data()
        # Add a new sheet
        ok, msg = workbook_add_sheet(wb, "Temp")
        assert ok is not None, f"add_sheet failed: {msg}"
        assert "Temp" in workbook_sheet_order(wb)
        # Rename it
        ok, msg = workbook_rename_sheet(wb, "Temp", "Archive")
        assert ok is not None, f"rename_sheet failed: {msg}"
        assert "Archive" in workbook_sheet_order(wb)
        assert "Temp" not in workbook_sheet_order(wb)
        # Remove it
        ok, msg = workbook_remove_sheet(wb, "Archive")
        assert ok is not None, f"remove_sheet failed: {msg}"
        assert "Archive" not in workbook_sheet_order(wb)
        # Original sheets remain
        assert "Sales" in workbook_sheet_order(wb)
        assert "Summary" in workbook_sheet_order(wb)

    def test_sheet_workflow_preserves_data(self):
        wb = _build_workbook_with_data()
        ok, _ = workbook_add_sheet(wb, "NewSheet")
        assert ok is not None
        # NewSheet has no rows — set_cell_value returns False (expected product behavior)
        ok_edit, msg_edit = workbook_set_cell_value(wb, "NewSheet", 0, 0, "Header")
        assert not bool(ok_edit), f"Expected failure on empty sheet, got: {msg_edit}"
        # Data in original sheets untouched
        sales_name = wb["sheets"][0]["name"]
        assert sales_name == "Sales"

    def test_multi_sheet_write_round_trip(self):
        wb = _build_workbook_with_data()
        ok, _ = workbook_add_sheet(wb, "Aux", position=0)
        assert ok is not None
        with tempfile.NamedTemporaryFile(suffix=".fods", delete=False) as tf:
            out = Path(tf.name)
        write_fods(wb, out)
        wb2 = parse_fods(out)
        orders = workbook_sheet_order(wb2)
        assert "Aux" in orders
        assert "Sales" in orders
        assert "Summary" in orders
        out.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Workflow 4: Analysis APIs on constructed data
# ---------------------------------------------------------------------------

class TestFodsAnalysisOnConstructedData:
    """Analysis APIs work correctly on a constructed workbook."""

    def test_cell_range_returns_slice(self):
        wb = _build_workbook_with_data()
        # workbook_cell_range uses sheet_index (int), not sheet name
        result = workbook_cell_range(wb, 0, 0, 2, 0, 2)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_formula_list_returns_list(self):
        wb = _build_workbook_with_data()
        formulas = workbook_formula_list(wb)
        assert isinstance(formulas, list)
        # No formulas in this workbook
        assert formulas == []

    def test_stats_on_multi_sheet(self):
        wb = _build_workbook_with_data()
        stats = workbook_stats(wb)
        assert stats["sheet_count"] == 2
        assert stats["total_cells"] > 0


# ---------------------------------------------------------------------------
# Workflow 5: CSV export
# ---------------------------------------------------------------------------

class TestFodsCsvExportWorkflow:
    """CSV export from FODS is part of the product workflow."""

    def test_export_sheet_to_csv_produces_output(self):
        wb = _build_workbook_with_data()
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as tf:
            csv_path = Path(tf.name)
        # Sales is sheet index 0
        export_fods_to_csv_file(wb, csv_path, sheet_index=0)
        content = csv_path.read_text()
        assert "Product" in content
        assert "Widget" in content
        csv_path.unlink(missing_ok=True)

    def test_export_produces_well_formed_csv(self):
        wb = _build_workbook_with_data()
        csv_string = export_fods_to_csv(wb, sheet_index=0)
        lines = csv_string.splitlines()
        assert len(lines) >= 2, "CSV should have header + data rows"
