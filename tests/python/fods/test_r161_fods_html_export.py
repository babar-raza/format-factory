"""Tests for FODS workbook_to_html export.

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT23-001
Covers: HTML table export from FODS workbooks
"""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fods.neutral_model import workbook_to_html


def _make_wb(sheets):
    return {"sheets": sheets}


def _make_sheet(name, rows_data):
    rows = []
    for row_vals in rows_data:
        cells = [{"value": v, "type": "string"} for v in row_vals]
        rows.append({"cells": cells})
    return {"name": name, "rows": rows}


class TestWorkbookToHtml:
    def test_basic_table(self):
        wb = _make_wb([_make_sheet("S1", [["Name", "Age"], ["Alice", "30"]])])
        html = workbook_to_html(wb)
        assert "<table>" in html
        assert "<td>Name</td>" in html
        assert "<td>Alice</td>" in html

    def test_empty_sheet(self):
        wb = _make_wb([{"name": "Empty", "rows": []}])
        html = workbook_to_html(wb)
        assert html == "<table></table>"

    def test_bad_sheet_index(self):
        wb = _make_wb([_make_sheet("S1", [["A"]])])
        html = workbook_to_html(wb, sheet_index=5)
        assert html == ""

    def test_html_escaping(self):
        wb = _make_wb([_make_sheet("S1", [["a & b"]])])
        html = workbook_to_html(wb)
        assert "&amp;" in html

    def test_multiple_rows(self):
        wb = _make_wb([_make_sheet("S1", [["R1"], ["R2"], ["R3"]])])
        html = workbook_to_html(wb)
        assert html.count("<tr>") == 3

    def test_second_sheet(self):
        wb = _make_wb([
            _make_sheet("S1", [["First"]]),
            _make_sheet("S2", [["Second"]]),
        ])
        html = workbook_to_html(wb, sheet_index=1)
        assert "<td>Second</td>" in html
        assert "First" not in html

    def test_none_value(self):
        wb = _make_wb([{"name": "S1", "rows": [{"cells": [{"value": None}]}]}])
        html = workbook_to_html(wb)
        assert "<td></td>" in html
