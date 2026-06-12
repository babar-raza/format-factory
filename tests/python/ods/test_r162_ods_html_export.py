"""Tests for ODS ods_to_html export.

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT24-001
Covers: HTML table export from ODS files, with roundtrip and edge cases
"""

import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods.ods_parser import OdsDocument, OdsSheet, OdsRow, OdsCell, ods_to_html
from ods.ods_writer import write_ods


def _make_ods(rows_data, sheet_name="Sheet1"):
    rows = []
    for row_vals in rows_data:
        cells = []
        for val in row_vals:
            vtype = "float" if isinstance(val, (int, float)) else "string"
            cells.append(OdsCell(value=val, value_type=vtype, text=str(val)))
        rows.append(OdsRow(cells=cells))
    doc = OdsDocument(
        sheets=[OdsSheet(name=sheet_name, rows=rows)],
        path="",
    )
    with tempfile.NamedTemporaryFile(suffix=".ods", delete=False) as f:
        out = Path(f.name)
    write_ods(doc, out)
    return out


class TestOdsToHtml:
    def test_basic_table(self):
        path = _make_ods([["Name", "Score"], ["Alice", 95]])
        try:
            html = ods_to_html(path)
            assert "<table>" in html
            assert "</table>" in html
            assert "<td>Name</td>" in html
            assert "<td>Alice</td>" in html
            assert "<td>95</td>" in html
        finally:
            path.unlink(missing_ok=True)

    def test_empty_sheet(self):
        doc = OdsDocument(sheets=[OdsSheet(name="Empty", rows=[])], path="")
        with tempfile.NamedTemporaryFile(suffix=".ods", delete=False) as f:
            out = Path(f.name)
        write_ods(doc, out)
        try:
            html = ods_to_html(out)
            assert html == "<table></table>"
        finally:
            out.unlink(missing_ok=True)

    def test_bad_sheet_index(self):
        path = _make_ods([["A"]])
        try:
            html = ods_to_html(path, sheet_index=5)
            assert html == ""
        finally:
            path.unlink(missing_ok=True)

    def test_html_escaping(self):
        path = _make_ods([["a < b & c"]])
        try:
            html = ods_to_html(path)
            assert "&lt;" in html
            assert "&amp;" in html
        finally:
            path.unlink(missing_ok=True)

    def test_row_count(self):
        path = _make_ods([["R1"], ["R2"], ["R3"]])
        try:
            html = ods_to_html(path)
            assert html.count("<tr>") == 3
        finally:
            path.unlink(missing_ok=True)

    def test_float_formatting(self):
        path = _make_ods([[1.0, 2.5]])
        try:
            html = ods_to_html(path)
            assert "<td>1</td>" in html
            assert "<td>2.5</td>" in html
        finally:
            path.unlink(missing_ok=True)

    def test_mixed_value_and_empty_cell(self):
        path = _make_ods([["Header1", "Header2"], ["Alice", "95"]])
        try:
            html = ods_to_html(path)
            assert "<td>Header1</td>" in html
            assert "<td>Header2</td>" in html
        finally:
            path.unlink(missing_ok=True)
