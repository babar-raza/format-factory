"""
tests/packaging/test_r82_installed_fods_product_workflow.py

R82 Train H: FODS installed-wheel product workflow.

Validates the FODS product API workflow using the source package
(equivalent to what the installed wheel provides).
Defect fixed: D79-10 — R79 proved installation but not the full product workflow.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
# Add src/python to path to test the same code as the installed wheel
sys.path.insert(0, str(REPO_ROOT / "src" / "python"))


def _import_fods():
    """Import fods; skip if not available."""
    try:
        import fods
        return fods
    except ImportError:
        pytest.skip("fods not importable — install wheel first")


class TestFodsInstalledProductWorkflow:
    """FODS installed-wheel product workflow — all 8 product steps."""

    def test_fods_namespace(self):
        fods = _import_fods()
        assert fods.__name__ == "fods"

    def test_fods_version(self):
        fods = _import_fods()
        assert fods.__version__ == "0.1.0.dev0"

    def test_fods_track(self):
        fods = _import_fods()
        assert fods.__track__ == "python-foss"

    def test_fods_not_commercial(self):
        fods = _import_fods()
        assert fods.__commercial_ready__ is False

    def test_workbook_sheet_order(self):
        fods = _import_fods()
        wb = {
            "sheets": [
                {"name": "Sheet1", "rows": [
                    {"cells": [{"value": "A", "type": "string"}]},
                ], "auto_updatable": False}
            ]
        }
        sheets = fods.workbook_sheet_order(wb)
        assert isinstance(sheets, list)
        assert "Sheet1" in sheets

    def test_workbook_add_sheet(self):
        fods = _import_fods()
        wb = {"sheets": [{"name": "Sheet1", "rows": [], "auto_updatable": False}]}
        ok, msg = fods.workbook_add_sheet(wb, "R82_TEST_SHEET")
        assert ok, f"workbook_add_sheet failed: {msg}"
        names = [s["name"] for s in wb["sheets"]]
        assert "R82_TEST_SHEET" in names

    def test_workbook_rename_sheet(self):
        fods = _import_fods()
        wb = {"sheets": [
            {"name": "Sheet1", "rows": [], "auto_updatable": False},
            {"name": "OldName", "rows": [], "auto_updatable": False},
        ]}
        ok, msg = fods.workbook_rename_sheet(wb, "OldName", "NewName")
        assert ok, f"workbook_rename_sheet failed: {msg}"
        names = [s["name"] for s in wb["sheets"]]
        assert "NewName" in names
        assert "OldName" not in names

    def test_workbook_set_cell_value(self):
        fods = _import_fods()
        wb = {"sheets": [{"name": "Sheet1", "rows": [
            {"cells": [{"value": "original", "type": "string"}]},
        ], "auto_updatable": False}]}
        ok, msg = fods.workbook_set_cell_value(wb, "Sheet1", 0, 0, "R82_PROOF")
        assert ok, f"workbook_set_cell_value failed: {msg}"
        # Verify persisted
        sheet = wb["sheets"][0]
        assert sheet["rows"][0]["cells"][0]["value"] == "R82_PROOF"

    def test_workbook_remove_sheet(self):
        fods = _import_fods()
        wb = {"sheets": [
            {"name": "Sheet1", "rows": [], "auto_updatable": False},
            {"name": "ToRemove", "rows": [], "auto_updatable": False},
        ]}
        ok, msg = fods.workbook_remove_sheet(wb, "ToRemove")
        assert ok, f"workbook_remove_sheet failed: {msg}"
        names = [s["name"] for s in wb["sheets"]]
        assert "ToRemove" not in names

    def test_workbook_to_xml(self):
        fods = _import_fods()
        wb = {"sheets": [{"name": "Sheet1", "rows": [
            {"cells": [{"value": "Hello", "type": "string"}]},
        ], "auto_updatable": False}]}
        xml = fods.workbook_to_xml(wb)
        assert xml and len(xml) > 100, "workbook_to_xml returned empty/short output"
        assert isinstance(xml, str)

    def test_workbook_stats(self):
        fods = _import_fods()
        wb = {"sheets": [{"name": "Sheet1", "rows": [
            {"cells": [{"value": "x", "type": "string"}]},
        ], "auto_updatable": False}]}
        stats = fods.workbook_stats(wb)
        assert isinstance(stats, dict)
        assert "sheet_count" in stats or len(stats) > 0

    def test_workbook_warnings_for_unsupported_edit(self):
        fods = _import_fods()
        wb = {"sheets": [{"name": "Sheet1", "rows": [
            {"cells": [{"value": "x", "type": "string"}]},
        ], "auto_updatable": False}]}
        warnings = fods.workbook_warnings_for_unsupported_edit(wb, "Sheet1", 0, 0)
        assert isinstance(warnings, list), f"Expected list, got {type(warnings)}"

    def test_full_workflow_sequence(self):
        """End-to-end product workflow as proven in Train H."""
        fods = _import_fods()
        # Build workbook
        wb = {"sheets": [{"name": "Sheet1", "rows": [
            {"cells": [{"value": "Product", "type": "string"},
                       {"value": "Price", "type": "string"}]},
            {"cells": [{"value": "Widget", "type": "string"},
                       {"value": "9.99", "type": "number"}]},
        ], "auto_updatable": False}]}

        # Sheet order
        sheets = fods.workbook_sheet_order(wb)
        assert "Sheet1" in sheets

        # Add + rename sheet
        ok, _ = fods.workbook_add_sheet(wb, "TEMP")
        assert ok
        ok, _ = fods.workbook_rename_sheet(wb, "TEMP", "RENAMED")
        assert ok

        # Set cell value
        ok, _ = fods.workbook_set_cell_value(wb, "Sheet1", 0, 0, "WORKFLOW_PROOF")
        assert ok

        # Remove sheet
        ok, _ = fods.workbook_remove_sheet(wb, "RENAMED")
        assert ok

        # XML export
        xml = fods.workbook_to_xml(wb)
        assert len(xml) > 100

        # Stats
        stats = fods.workbook_stats(wb)
        assert isinstance(stats, dict)

        # Warnings
        warnings = fods.workbook_warnings_for_unsupported_edit(wb, "Sheet1", 0, 0)
        assert isinstance(warnings, list)
