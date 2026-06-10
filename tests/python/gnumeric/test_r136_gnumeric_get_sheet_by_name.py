"""Tests for get_sheet_by_name() — Gnumeric sheet lookup by name.

Sprint: FORMAT-FACTORY-AUTONOMY-ACCELERATION-SPRINT-4-001
TC-PRODUCT-GNUMERIC-GET-SHEET-BY-NAME
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from gnumeric.gnumeric_codec import create_gnumeric, get_sheet_by_name


class TestGetSheetByName:
    def test_returns_correct_sheet(self):
        model = create_gnumeric([{"name": "Alpha"}, {"name": "Beta"}])
        sheet = get_sheet_by_name(model, "Beta")
        assert sheet is not None
        assert sheet["name"] == "Beta"

    def test_returns_first_matching_sheet(self):
        model = create_gnumeric([{"name": "Alpha"}, {"name": "Beta"}])
        sheet = get_sheet_by_name(model, "Alpha")
        assert sheet is not None
        assert sheet["name"] == "Alpha"

    def test_returns_none_when_not_found(self):
        model = create_gnumeric([{"name": "Sheet1"}])
        sheet = get_sheet_by_name(model, "Nonexistent")
        assert sheet is None

    def test_empty_workbook_returns_none(self):
        model = create_gnumeric([])
        assert get_sheet_by_name(model, "Sheet1") is None

    def test_case_sensitive_match(self):
        model = create_gnumeric([{"name": "Data"}])
        assert get_sheet_by_name(model, "data") is None
        assert get_sheet_by_name(model, "DATA") is None
        assert get_sheet_by_name(model, "Data") is not None

    def test_sheet_contains_cell_data(self):
        model = create_gnumeric([{"name": "Vals", "rows": [["x", "y"]]}])
        sheet = get_sheet_by_name(model, "Vals")
        assert sheet is not None
        assert "x" in sheet["cell_values"]

    def test_type_error_on_non_dict_model(self):
        with pytest.raises(TypeError):
            get_sheet_by_name("not a dict", "Sheet1")

    def test_type_error_on_non_string_name(self):
        model = create_gnumeric([{"name": "Sheet1"}])
        with pytest.raises(TypeError):
            get_sheet_by_name(model, 0)

    def test_multiple_sheets_finds_last(self):
        model = create_gnumeric([
            {"name": "A"}, {"name": "B"}, {"name": "C"}
        ])
        sheet = get_sheet_by_name(model, "C")
        assert sheet is not None
        assert sheet["name"] == "C"

    def test_returns_dict(self):
        model = create_gnumeric([{"name": "S1"}])
        result = get_sheet_by_name(model, "S1")
        assert isinstance(result, dict)
