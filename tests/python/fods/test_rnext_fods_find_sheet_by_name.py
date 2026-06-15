"""
test_rnext_fods_find_sheet_by_name.py -- Dedicated test coverage for find_sheet_by_name.

Gap: GAP-FODS-FOSS-FIND_SHEET_B-001 (missing_test_coverage)
"""
from __future__ import annotations
import sys
from pathlib import Path
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fods.neutral_model import find_sheet_by_name


def _wb(sheets=None):
    return {"sheets": sheets or []}

def _sheet(name="Sheet1", rows=None):
    return {"name": name, "rows": rows or []}


class TestFindSheetByName:
    def test_finds_existing_sheet(self):
        wb = _wb([_sheet("Alpha"), _sheet("Beta")])
        result = find_sheet_by_name(wb, "Beta")
        assert result is not None
        assert result["name"] == "Beta"

    def test_returns_none_for_missing(self):
        wb = _wb([_sheet("Alpha")])
        assert find_sheet_by_name(wb, "Missing") is None

    def test_empty_workbook_returns_none(self):
        assert find_sheet_by_name(_wb(), "Any") is None

    def test_case_sensitive(self):
        wb = _wb([_sheet("Sheet1")])
        assert find_sheet_by_name(wb, "sheet1") is None
        assert find_sheet_by_name(wb, "Sheet1") is not None

    def test_first_match_returned(self):
        wb = _wb([_sheet("Dup", []), _sheet("Dup", [{"cells": []}])])
        result = find_sheet_by_name(wb, "Dup")
        assert result is not None
        assert result["rows"] == []

    def test_returns_full_sheet_dict(self):
        wb = _wb([_sheet("Data", [{"cells": [{"value": "x"}]}])])
        result = find_sheet_by_name(wb, "Data")
        assert "rows" in result
        assert len(result["rows"]) == 1

    def test_empty_name(self):
        wb = _wb([_sheet("")])
        result = find_sheet_by_name(wb, "")
        assert result is not None
