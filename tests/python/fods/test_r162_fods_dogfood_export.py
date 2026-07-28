"""
test_r162_fods_dogfood_export.py — Dogfood export: use FODS library to build a test results spreadsheet.

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT24-001
Added: 2026-06-10

Demonstrates practical usage of format-factory-fods by creating a test results
report spreadsheet from structured data, writing to FODS, and verifying roundtrip.

Authority: P6 (SAL-FODS-00001: ODF 1.3 spreadsheet MIME type)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from src.python.fods.neutral_model import (
    build_workbook,
    workbook_sheet_order,
    workbook_numeric_summary,
    workbook_to_csv,
    workbook_get_cell_value,
)
from src.python.fods.writer import write_fods
from src.python.fods.parser import parse_fods

# Simulated test results (dogfood: using our own FODS library for project data)
TEST_RESULTS = [
    {"format": "FODS", "tests": 547, "passed": 547, "failed": 0},
    {"format": "FODT", "tests": 520, "passed": 520, "failed": 0},
    {"format": "ABW", "tests": 34, "passed": 34, "failed": 0},
    {"format": "Gnumeric", "tests": 30, "passed": 30, "failed": 0},
    {"format": "ODS", "tests": 28, "passed": 28, "failed": 0},
    {"format": "DIF", "tests": 8, "passed": 8, "failed": 0},
    {"format": "TSV", "tests": 35, "passed": 35, "failed": 0},
    {"format": "TOML", "tests": 8, "passed": 8, "failed": 0},
]

HEADERS = ["Format", "Tests", "Passed", "Failed"]


def _cell(value, value_type="string"):
    return {"value": value, "value_type": value_type}


def _row(cells):
    return {"cells": cells}


def _build_report_workbook():
    """Build a FODS workbook from the test results data using direct construction."""
    header_row = _row([_cell(h) for h in HEADERS])
    data_rows = []
    for entry in TEST_RESULTS:
        data_rows.append(_row([
            _cell(entry["format"], "string"),
            _cell(entry["tests"], "float"),
            _cell(entry["passed"], "float"),
            _cell(entry["failed"], "float"),
        ]))

    sheet = {
        "name": "Test Results",
        "rows": [header_row] + data_rows,
    }

    wb = build_workbook(
        odf_version_attr="1.3",
        mimetype="application/vnd.oasis.opendocument.spreadsheet-flat-xml",
        sheets=[sheet],
        warnings=[],
        unsupported_features=[],
        parse_errors=[],
    )
    return wb


class TestFodsDogfoodExport:
    def test_build_report(self):
        wb = _build_report_workbook()
        assert workbook_sheet_order(wb) == ["Test Results"]
        assert len(wb["sheets"][0]["rows"]) == len(TEST_RESULTS) + 1

    def test_cell_values_set(self):
        wb = _build_report_workbook()
        val = workbook_get_cell_value(wb, "Test Results", 1, 0)
        assert val == "FODS"
        tests = workbook_get_cell_value(wb, "Test Results", 1, 1)
        assert tests == 547

    def test_numeric_summary(self):
        wb = _build_report_workbook()
        summary = workbook_numeric_summary(wb)
        assert summary["total_numeric_cells"] > 0
        assert summary["global_min"] == 0

    def test_csv_export(self):
        wb = _build_report_workbook()
        csv_str = workbook_to_csv(wb)
        assert "Format" in csv_str
        assert "FODS" in csv_str
        lines = [line for line in csv_str.strip().split("\n") if line.strip()]
        assert len(lines) == len(TEST_RESULTS) + 1

    def test_write_and_reparse(self, tmp_path):
        wb = _build_report_workbook()
        out = tmp_path / "test-results.fods"
        write_fods(wb, str(out))
        assert out.exists()
        reloaded = parse_fods(str(out))
        assert len(reloaded["sheets"]) >= 1
        assert reloaded["sheets"][0]["name"] == "Test Results"

    def test_roundtrip_preserves_row_count(self, tmp_path):
        wb = _build_report_workbook()
        out = tmp_path / "test-results.fods"
        write_fods(wb, str(out))
        reloaded = parse_fods(str(out))
        assert len(reloaded["sheets"][0]["rows"]) == len(TEST_RESULTS) + 1
