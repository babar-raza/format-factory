"""
tests/python/gnumeric/test_r120_gnumeric_json_export.py

Sprint: FORMAT-FACTORY-PRODUCT-FIRST-AUTONOMOUS-ACQUISITION-TRAIN-001
TC-GNM-JSON: export_to_json()
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric.gnumeric_codec import (
    create_gnumeric,
    write_gnumeric,
    export_to_json,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_gnumeric_file(sheets: list[dict]) -> Path:
    """Write a temp Gnumeric file and return its path."""
    model = create_gnumeric(sheets)
    with tempfile.NamedTemporaryFile(suffix=".gnumeric", delete=False) as f:
        tmp = Path(f.name)
    write_gnumeric(model, tmp)
    return tmp


def _simple_sheet(name: str, rows: list[list[str]]) -> dict:
    return {"name": name, "rows": rows}


# ---------------------------------------------------------------------------
# Basic structure
# ---------------------------------------------------------------------------

class TestExportToJsonBasic:
    """export_to_json() returns valid JSON."""

    def test_returns_string(self):
        tmp = _make_gnumeric_file([_simple_sheet("S1", [["A", "B"], ["1", "2"]])])
        try:
            result = export_to_json(tmp)
            assert isinstance(result, str)
        finally:
            tmp.unlink()

    def test_valid_json(self):
        tmp = _make_gnumeric_file([_simple_sheet("Sheet1", [["X"]])])
        try:
            result = export_to_json(tmp)
            parsed = json.loads(result)
            assert parsed is not None
        finally:
            tmp.unlink()

    def test_top_level_is_list(self):
        tmp = _make_gnumeric_file([_simple_sheet("S1", [["A"]])])
        try:
            result = json.loads(export_to_json(tmp))
            assert isinstance(result, list)
        finally:
            tmp.unlink()

    def test_one_entry_per_sheet(self):
        tmp = _make_gnumeric_file([
            _simple_sheet("Sheet1", [["A"]]),
            _simple_sheet("Sheet2", [["B"]]),
        ])
        try:
            result = json.loads(export_to_json(tmp))
            assert len(result) == 2
        finally:
            tmp.unlink()

    def test_sheet_has_name_field(self):
        tmp = _make_gnumeric_file([_simple_sheet("MySheet", [["A"]])])
        try:
            result = json.loads(export_to_json(tmp))
            assert result[0]["name"] == "MySheet"
        finally:
            tmp.unlink()

    def test_sheet_has_rows_field(self):
        tmp = _make_gnumeric_file([_simple_sheet("S1", [["A", "B"]])])
        try:
            result = json.loads(export_to_json(tmp))
            assert "rows" in result[0]
            assert isinstance(result[0]["rows"], list)
        finally:
            tmp.unlink()

    def test_rows_contain_lists_of_strings(self):
        tmp = _make_gnumeric_file([_simple_sheet("S1", [["A", "B"], ["1", "2"]])])
        try:
            result = json.loads(export_to_json(tmp))
            for row in result[0]["rows"]:
                assert isinstance(row, list)
                for cell in row:
                    assert isinstance(cell, str)
        finally:
            tmp.unlink()


# ---------------------------------------------------------------------------
# Data accuracy
# ---------------------------------------------------------------------------

class TestExportToJsonData:
    """Verify cell values and structure are correctly exported."""

    def test_single_cell_value(self):
        tmp = _make_gnumeric_file([_simple_sheet("S1", [["Hello"]])])
        try:
            result = json.loads(export_to_json(tmp))
            assert result[0]["rows"][0][0] == "Hello"
        finally:
            tmp.unlink()

    def test_grid_values_preserved(self):
        tmp = _make_gnumeric_file([_simple_sheet("Data", [
            ["Name", "Age"],
            ["Alice", "30"],
            ["Bob", "25"],
        ])])
        try:
            result = json.loads(export_to_json(tmp))
            rows = result[0]["rows"]
            assert rows[0][0] == "Name"
            assert rows[0][1] == "Age"
            assert rows[1][0] == "Alice"
            assert rows[2][0] == "Bob"
        finally:
            tmp.unlink()

    def test_empty_sheet_has_empty_rows(self):
        tmp = _make_gnumeric_file([_simple_sheet("Empty", [])])
        try:
            result = json.loads(export_to_json(tmp))
            assert result[0]["rows"] == []
        finally:
            tmp.unlink()

    def test_multi_sheet_name_order(self):
        tmp = _make_gnumeric_file([
            _simple_sheet("First", [["A"]]),
            _simple_sheet("Second", [["B"]]),
        ])
        try:
            result = json.loads(export_to_json(tmp))
            assert result[0]["name"] == "First"
            assert result[1]["name"] == "Second"
        finally:
            tmp.unlink()

    def test_numeric_strings_preserved_as_strings(self):
        tmp = _make_gnumeric_file([_simple_sheet("S1", [["42", "3.14"]])])
        try:
            result = json.loads(export_to_json(tmp))
            row = result[0]["rows"][0]
            assert row[0] == "42"
            assert row[1] == "3.14"
        finally:
            tmp.unlink()


# ---------------------------------------------------------------------------
# Roundtrip
# ---------------------------------------------------------------------------

class TestExportToJsonRoundtrip:
    """create → write → export_to_json roundtrip."""

    def test_full_roundtrip(self):
        sheets = [{"name": "Report", "rows": [["Q1", "Q2", "Q3"], ["100", "200", "300"]]}]
        model = create_gnumeric(sheets)
        tmp = Path(tempfile.mktemp(suffix=".gnumeric"))
        try:
            write_gnumeric(model, tmp)
            result = json.loads(export_to_json(tmp))
            assert result[0]["name"] == "Report"
            row0 = result[0]["rows"][0]
            assert "Q1" in row0
            assert "Q2" in row0
            assert "Q3" in row0
        finally:
            if tmp.exists():
                tmp.unlink()

    def test_json_serializable_output(self):
        """Output must be serializable (no non-JSON types)."""
        tmp = _make_gnumeric_file([_simple_sheet("S1", [["A", "B"]])])
        try:
            raw = export_to_json(tmp)
            re_parsed = json.loads(raw)
            re_dumped = json.dumps(re_parsed)
            assert len(re_dumped) > 0
        finally:
            tmp.unlink()

    def test_accepts_bytes_input(self):
        tmp = _make_gnumeric_file([_simple_sheet("S1", [["Cell"]])])
        try:
            raw_bytes = tmp.read_bytes()
            result = json.loads(export_to_json(raw_bytes))
            assert result[0]["rows"][0][0] == "Cell"
        finally:
            tmp.unlink()
