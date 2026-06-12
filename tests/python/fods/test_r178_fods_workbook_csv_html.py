"""
test_r178_fods_workbook_csv_html.py -- Tests for FODS workbook_to_csv and workbook_to_html.

Coverage:
  - workbook_to_csv: returns string, CSV rows, commas/quoting, empty workbook,
    sheet_name selection, missing sheet, None values
  - workbook_to_html: returns string, table structure, HTML escaping,
    empty sheet, index out of range, cell values

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT54-001
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fods import (
    parse_fods,
    workbook_to_csv,
    workbook_to_html,
)

_SAMPLES = _REPO / "samples" / "by-format" / "fods"
_MINIMAL = str(_SAMPLES / "minimal-spreadsheet.fods")


def get_model():
    return parse_fods(_MINIMAL)


# ---------------------------------------------------------------------------
# workbook_to_csv tests
# ---------------------------------------------------------------------------

class TestWorkbookToCsv:
    def test_returns_string(self):
        model = get_model()
        out = workbook_to_csv(model)
        assert isinstance(out, str)

    def test_non_empty_for_real_file(self):
        model = get_model()
        out = workbook_to_csv(model)
        assert len(out) > 0

    def test_has_crlf_line_endings(self):
        model = get_model()
        out = workbook_to_csv(model)
        assert "\r\n" in out

    def test_empty_workbook_returns_empty(self):
        out = workbook_to_csv({"sheets": []})
        assert out == ""

    def test_missing_sheet_name_returns_empty(self):
        model = get_model()
        out = workbook_to_csv(model, sheet_name="__nonexistent__")
        assert out == ""

    def test_sheet_name_none_exports_first(self):
        model = get_model()
        out_none = workbook_to_csv(model, sheet_name=None)
        first_name = model["sheets"][0]["name"]
        out_named = workbook_to_csv(model, sheet_name=first_name)
        assert out_none == out_named

    def test_single_row_workbook(self):
        wb = {
            "sheets": [{
                "name": "Sheet1",
                "rows": [{"cells": [{"value": "hello"}, {"value": "world"}]}]
            }]
        }
        out = workbook_to_csv(wb)
        assert "hello" in out
        assert "world" in out

    def test_numeric_values_exported(self):
        wb = {
            "sheets": [{
                "name": "Sheet1",
                "rows": [{"cells": [{"value": 42}, {"value": 3.14}]}]
            }]
        }
        out = workbook_to_csv(wb)
        assert "42" in out
        assert "3.14" in out

    def test_none_cell_exported_as_empty(self):
        wb = {
            "sheets": [{
                "name": "Sheet1",
                "rows": [{"cells": [{"value": None}, {"value": "x"}]}]
            }]
        }
        out = workbook_to_csv(wb)
        assert "x" in out

    def test_comma_in_value_quoted(self):
        wb = {
            "sheets": [{
                "name": "Sheet1",
                "rows": [{"cells": [{"value": "a,b"}]}]
            }]
        }
        out = workbook_to_csv(wb)
        assert '"a,b"' in out


# ---------------------------------------------------------------------------
# workbook_to_html tests
# ---------------------------------------------------------------------------

class TestWorkbookToHtml:
    def test_returns_string(self):
        model = get_model()
        out = workbook_to_html(model)
        assert isinstance(out, str)

    def test_contains_table_tag(self):
        model = get_model()
        out = workbook_to_html(model)
        assert "<table>" in out
        assert "</table>" in out

    def test_contains_tr_and_td(self):
        model = get_model()
        out = workbook_to_html(model)
        assert "<tr>" in out
        assert "<td>" in out

    def test_empty_sheet_returns_empty_table(self):
        wb = {"sheets": [{"name": "S", "rows": []}]}
        out = workbook_to_html(wb)
        assert out == "<table></table>"

    def test_out_of_range_index_returns_empty(self):
        model = get_model()
        out = workbook_to_html(model, sheet_index=999)
        assert out == ""

    def test_negative_index_returns_empty(self):
        model = get_model()
        out = workbook_to_html(model, sheet_index=-1)
        assert out == ""

    def test_html_escaping_of_angle_brackets(self):
        wb = {
            "sheets": [{
                "name": "S",
                "rows": [{"cells": [{"value": "<script>"}]}]
            }]
        }
        out = workbook_to_html(wb)
        assert "<script>" not in out
        assert "&lt;script&gt;" in out

    def test_numeric_value_in_td(self):
        wb = {
            "sheets": [{
                "name": "S",
                "rows": [{"cells": [{"value": 99}]}]
            }]
        }
        out = workbook_to_html(wb)
        assert "99" in out
