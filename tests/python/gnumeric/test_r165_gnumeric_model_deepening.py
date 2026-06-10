"""
test_r165_gnumeric_model_deepening.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT31-001
Added: 2026-06-10

Deepening tests for Gnumeric create_gnumeric, write_gnumeric, load roundtrip,
and export_to_json with model-level edge cases.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric.gnumeric_codec import (
    create_gnumeric,
    write_gnumeric,
    load,
    export_to_json,
    set_cell_value,
)


class TestCreateGnumeric:

    def test_empty_sheets_list(self):
        doc = create_gnumeric([])
        assert isinstance(doc, dict)
        assert doc["sheets"] == []

    def test_single_empty_sheet(self):
        doc = create_gnumeric([{"name": "MySheet"}])
        assert len(doc["sheets"]) == 1
        assert doc["sheets"][0]["name"] == "MySheet"

    def test_multiple_sheets(self):
        doc = create_gnumeric([
            {"name": "Sheet1"},
            {"name": "Sheet2"},
            {"name": "Sheet3"},
        ])
        assert len(doc["sheets"]) == 3
        names = [s["name"] for s in doc["sheets"]]
        assert names == ["Sheet1", "Sheet2", "Sheet3"]

    def test_sheet_with_rows(self):
        doc = create_gnumeric([{
            "name": "Data",
            "rows": [["A", "B"], ["1", "2"]],
        }])
        assert len(doc["sheets"]) == 1
        assert doc["sheets"][0]["name"] == "Data"

    def test_default_sheet_name(self):
        doc = create_gnumeric([{}])
        assert len(doc["sheets"]) == 1
        assert "name" in doc["sheets"][0]


class TestWriteAndLoadRoundtrip:

    def test_basic_roundtrip(self, tmp_path):
        doc = create_gnumeric([{"name": "Test", "rows": [["hello"]]}])
        p = tmp_path / "rt.gnumeric"
        write_gnumeric(doc, str(p))
        loaded = load(str(p))
        assert isinstance(loaded, dict)
        assert "sheets" in loaded
        assert len(loaded["sheets"]) >= 1

    def test_multi_sheet_roundtrip(self, tmp_path):
        doc = create_gnumeric([
            {"name": "A", "rows": [["1"]]},
            {"name": "B", "rows": [["2"]]},
        ])
        p = tmp_path / "multi.gnumeric"
        write_gnumeric(doc, str(p))
        loaded = load(str(p))
        assert len(loaded["sheets"]) == 2

    def test_empty_sheet_roundtrip(self, tmp_path):
        doc = create_gnumeric([{"name": "Empty"}])
        p = tmp_path / "empty.gnumeric"
        write_gnumeric(doc, str(p))
        loaded = load(str(p))
        assert len(loaded["sheets"]) >= 1

    def test_set_cell_roundtrip(self, tmp_path):
        doc = create_gnumeric([{"name": "S1"}])
        doc = set_cell_value(doc, 0, 0, 0, "42")
        p = tmp_path / "cell.gnumeric"
        write_gnumeric(doc, str(p))
        loaded = load(str(p))
        assert loaded["sheets"][0]["cell_count"] >= 1


class TestExportToJsonModel:

    def test_returns_valid_json(self, tmp_path):
        doc = create_gnumeric([{"name": "S1", "rows": [["A", "B"]]}])
        p = tmp_path / "test.gnumeric"
        write_gnumeric(doc, str(p))
        result = export_to_json(str(p))
        parsed = json.loads(result)
        assert isinstance(parsed, list)

    def test_sheet_name_in_json(self, tmp_path):
        doc = create_gnumeric([{"name": "MyData"}])
        p = tmp_path / "test.gnumeric"
        write_gnumeric(doc, str(p))
        parsed = json.loads(export_to_json(str(p)))
        assert parsed[0]["name"] == "MyData"

    def test_multi_sheet_json(self, tmp_path):
        doc = create_gnumeric([
            {"name": "A", "rows": [["1"]]},
            {"name": "B", "rows": [["2"]]},
        ])
        p = tmp_path / "multi.gnumeric"
        write_gnumeric(doc, str(p))
        parsed = json.loads(export_to_json(str(p)))
        assert len(parsed) == 2
        names = [s["name"] for s in parsed]
        assert "A" in names
        assert "B" in names

    def test_json_has_rows(self, tmp_path):
        doc = create_gnumeric([{"name": "S1", "rows": [["x", "y"]]}])
        p = tmp_path / "test.gnumeric"
        write_gnumeric(doc, str(p))
        parsed = json.loads(export_to_json(str(p)))
        assert "rows" in parsed[0]
        assert isinstance(parsed[0]["rows"], list)
