"""
tests/python/fods/test_r77_fods_sheet_management.py

R77 Train I — FODS sheet management product depth:
- workbook_add_sheet
- workbook_rename_sheet
- workbook_remove_sheet
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.python.fods import (
    workbook_add_sheet,
    workbook_rename_sheet,
    workbook_remove_sheet,
    workbook_sheet_order,
)


def _minimal_workbook(sheet_names: list[str]) -> dict:
    """Build a minimal workbook dict for testing."""
    return {
        "sheets": [
            {"name": name, "rows": [], "auto_updatable": False}
            for name in sheet_names
        ]
    }


class TestWorkbookAddSheet:
    def test_add_sheet_to_empty_workbook(self):
        wb = {"sheets": []}
        ok, msg = workbook_add_sheet(wb, "Sheet1")
        assert ok is not None
        assert len(wb["sheets"]) == 1
        assert wb["sheets"][0]["name"] == "Sheet1"

    def test_add_sheet_appends_by_default(self):
        wb = _minimal_workbook(["A", "B"])
        ok, msg = workbook_add_sheet(wb, "C")
        assert ok is not None
        assert workbook_sheet_order(wb) == ["A", "B", "C"]

    def test_add_sheet_at_position_zero(self):
        wb = _minimal_workbook(["B", "C"])
        ok, msg = workbook_add_sheet(wb, "A", position=0)
        assert ok is not None
        assert wb["sheets"][0]["name"] == "A"

    def test_add_sheet_at_middle_position(self):
        wb = _minimal_workbook(["A", "C"])
        ok, msg = workbook_add_sheet(wb, "B", position=1)
        assert ok is not None
        assert workbook_sheet_order(wb) == ["A", "B", "C"]

    def test_add_duplicate_sheet_fails(self):
        wb = _minimal_workbook(["Sheet1"])
        ok, msg = workbook_add_sheet(wb, "Sheet1")
        assert not bool(ok)
        assert "already exists" in msg

    def test_add_empty_name_fails(self):
        wb = _minimal_workbook(["Sheet1"])
        ok, msg = workbook_add_sheet(wb, "")
        assert not bool(ok)
        assert "empty" in msg

    def test_add_whitespace_name_fails(self):
        wb = _minimal_workbook(["Sheet1"])
        ok, msg = workbook_add_sheet(wb, "   ")
        assert not bool(ok)

    def test_added_sheet_has_empty_rows(self):
        wb = {"sheets": []}
        ok, msg = workbook_add_sheet(wb, "NewSheet")
        assert ok is not None
        assert wb["sheets"][0]["rows"] == []

    def test_add_sheet_position_beyond_end_appends(self):
        wb = _minimal_workbook(["A"])
        ok, msg = workbook_add_sheet(wb, "Z", position=999)
        assert ok is not None
        assert wb["sheets"][-1]["name"] == "Z"


class TestWorkbookRenameSheet:
    def test_rename_existing_sheet(self):
        wb = _minimal_workbook(["OldName"])
        ok, msg = workbook_rename_sheet(wb, "OldName", "NewName")
        assert ok is not None
        assert wb["sheets"][0]["name"] == "NewName"

    def test_rename_nonexistent_sheet_fails(self):
        wb = _minimal_workbook(["A"])
        ok, msg = workbook_rename_sheet(wb, "NotHere", "B")
        assert not bool(ok)
        assert "not found" in msg

    def test_rename_to_existing_name_fails(self):
        wb = _minimal_workbook(["A", "B"])
        ok, msg = workbook_rename_sheet(wb, "A", "B")
        assert not bool(ok)
        assert "already exists" in msg

    def test_rename_to_same_name_succeeds(self):
        wb = _minimal_workbook(["Sheet1"])
        ok, msg = workbook_rename_sheet(wb, "Sheet1", "Sheet1")
        assert ok is not None

    def test_rename_empty_new_name_fails(self):
        wb = _minimal_workbook(["Sheet1"])
        ok, msg = workbook_rename_sheet(wb, "Sheet1", "")
        assert not bool(ok)
        assert "empty" in msg

    def test_rename_preserves_data(self):
        wb = {
            "sheets": [
                {"name": "Data", "rows": [{"cells": [{"value": "hello"}]}]}
            ]
        }
        ok, _ = workbook_rename_sheet(wb, "Data", "Results")
        assert ok is not None
        assert wb["sheets"][0]["rows"][0]["cells"][0]["value"] == "hello"


class TestWorkbookRemoveSheet:
    def test_remove_sheet_from_multi_sheet_workbook(self):
        wb = _minimal_workbook(["A", "B", "C"])
        ok, msg = workbook_remove_sheet(wb, "B")
        assert ok is not None
        assert workbook_sheet_order(wb) == ["A", "C"]

    def test_remove_only_sheet_fails(self):
        wb = _minimal_workbook(["OnlySheet"])
        ok, msg = workbook_remove_sheet(wb, "OnlySheet")
        assert not bool(ok)
        assert "only sheet" in msg

    def test_remove_nonexistent_sheet_fails(self):
        wb = _minimal_workbook(["A", "B"])
        ok, msg = workbook_remove_sheet(wb, "NotHere")
        assert not bool(ok)
        assert "not found" in msg

    def test_remove_first_sheet(self):
        wb = _minimal_workbook(["A", "B"])
        ok, _ = workbook_remove_sheet(wb, "A")
        assert ok is not None
        assert workbook_sheet_order(wb) == ["B"]

    def test_remove_last_sheet(self):
        wb = _minimal_workbook(["A", "B"])
        ok, _ = workbook_remove_sheet(wb, "B")
        assert ok is not None
        assert workbook_sheet_order(wb) == ["A"]

    def test_remove_returns_count_before_after(self):
        wb = _minimal_workbook(["A", "B", "C"])
        ok, msg = workbook_remove_sheet(wb, "B")
        assert ok is not None
        assert "3" in msg and "2" in msg
