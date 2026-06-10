"""Tests for SYLK sylk_to_html export.

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT23-001
Covers: HTML table export from SYLK files
"""

import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from sylk.sylk_parser import (
    SylkDocument,
    SylkCell,
    write_sylk,
    sylk_to_html,
)


def _make_sylk_file(cells):
    doc = SylkDocument(cells=cells)
    path = Path(tempfile.mktemp(suffix=".sylk"))
    write_sylk(doc, path)
    return path


class TestSylkToHtml:
    def test_basic_table(self):
        path = _make_sylk_file([
            SylkCell(row=1, col=1, value="Name", value_type="string"),
            SylkCell(row=1, col=2, value="Age", value_type="string"),
            SylkCell(row=2, col=1, value="Alice", value_type="string"),
            SylkCell(row=2, col=2, value=30, value_type="numeric"),
        ])
        try:
            html = sylk_to_html(path)
            assert "<table>" in html
            assert "</table>" in html
            assert "<td>Name</td>" in html
            assert "<td>Alice</td>" in html
            assert "<td>30</td>" in html
        finally:
            path.unlink(missing_ok=True)

    def test_empty_file(self):
        path = _make_sylk_file([])
        try:
            html = sylk_to_html(path)
            assert "<table></table>" == html
        finally:
            path.unlink(missing_ok=True)

    def test_html_escaping(self):
        path = _make_sylk_file([
            SylkCell(row=1, col=1, value="a < b", value_type="string"),
        ])
        try:
            html = sylk_to_html(path)
            assert "&lt;" in html
        finally:
            path.unlink(missing_ok=True)

    def test_has_tr_tags(self):
        path = _make_sylk_file([
            SylkCell(row=1, col=1, value="X", value_type="string"),
            SylkCell(row=2, col=1, value="Y", value_type="string"),
        ])
        try:
            html = sylk_to_html(path)
            assert html.count("<tr>") == 2
            assert html.count("</tr>") == 2
        finally:
            path.unlink(missing_ok=True)

    def test_sparse_cells(self):
        path = _make_sylk_file([
            SylkCell(row=1, col=1, value="A", value_type="string"),
            SylkCell(row=1, col=3, value="C", value_type="string"),
        ])
        try:
            html = sylk_to_html(path)
            assert html.count("<td>") == 3
        finally:
            path.unlink(missing_ok=True)
