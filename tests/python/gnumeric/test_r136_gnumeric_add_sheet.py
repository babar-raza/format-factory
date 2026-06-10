"""Tests for add_sheet() — Gnumeric sheet addition.

Sprint: FORMAT-FACTORY-AUTONOMY-ACCELERATION-SPRINT-4-001
TC-PRODUCT-GNUMERIC-ADD-SHEET
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from gnumeric.gnumeric_codec import create_gnumeric, add_sheet


class TestAddSheet:
    def test_sheet_count_increases(self):
        model = create_gnumeric([{"name": "Sheet1"}])
        result = add_sheet(model, "Sheet2")
        assert result["sheet_count"] == 2

    def test_new_sheet_name(self):
        model = create_gnumeric([{"name": "Sheet1"}])
        result = add_sheet(model, "NewSheet")
        names = [s["name"] for s in result["sheets"]]
        assert "NewSheet" in names

    def test_original_sheet_preserved(self):
        model = create_gnumeric([{"name": "Sheet1"}])
        result = add_sheet(model, "Sheet2")
        names = [s["name"] for s in result["sheets"]]
        assert "Sheet1" in names

    def test_does_not_mutate_original(self):
        model = create_gnumeric([{"name": "Sheet1"}])
        add_sheet(model, "Sheet2")
        assert model["sheet_count"] == 1

    def test_auto_name_when_empty(self):
        model = create_gnumeric([{"name": "Sheet1"}])
        result = add_sheet(model, "")
        names = [s["name"] for s in result["sheets"]]
        assert any(n.startswith("Sheet") for n in names)

    def test_new_sheet_is_empty(self):
        model = create_gnumeric([])
        result = add_sheet(model, "Empty")
        sheet = result["sheets"][0]
        assert sheet["cell_count"] == 0
        assert sheet["cell_values"] == []

    def test_add_to_empty_workbook(self):
        model = create_gnumeric([])
        result = add_sheet(model, "First")
        assert result["sheet_count"] == 1

    def test_insert_at_beginning(self):
        model = create_gnumeric([{"name": "B"}, {"name": "C"}])
        result = add_sheet(model, "A", insert_at=0)
        assert result["sheets"][0]["name"] == "A"

    def test_insert_at_middle(self):
        model = create_gnumeric([{"name": "A"}, {"name": "C"}])
        result = add_sheet(model, "B", insert_at=1)
        assert result["sheets"][1]["name"] == "B"

    def test_type_error_on_non_dict(self):
        with pytest.raises(TypeError):
            add_sheet("not a dict", "Sheet1")

    def test_is_gnumeric_flag_preserved(self):
        model = create_gnumeric([])
        result = add_sheet(model, "S")
        assert result.get("is_gnumeric") is True
