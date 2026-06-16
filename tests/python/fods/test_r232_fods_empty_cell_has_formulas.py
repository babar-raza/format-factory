"""Tests for fods_empty_cell_count and fods_has_formulas.

Product deepening: FODS analytics — TC-H3-002-FODS / PDC-FODS-EMPTY-FORMULA-001.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fods import parse_fods_strict, fods_empty_cell_count, fods_has_formulas


def _make_fods(tmp_path, name, rows_xml):
    ns_o = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    ns_t = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
    ns_txt = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
    xml = (
        f'<?xml version="1.0"?>'
        f'<office:document xmlns:office="{ns_o}" xmlns:table="{ns_t}" xmlns:text="{ns_txt}"'
        f' office:version="1.2" office:mimetype="application/vnd.oasis.opendocument.spreadsheet">'
        f'<office:body><office:spreadsheet>'
        f'<table:table table:name="Sheet1">{rows_xml}</table:table>'
        f'</office:spreadsheet></office:body></office:document>'
    )
    p = tmp_path / f"{name}.fods"
    p.write_text(xml, encoding="utf-8")
    return p


def _row(*cells):
    cell_xml = ""
    for c in cells:
        if c is None:
            cell_xml += "<table:table-cell/>"
        elif isinstance(c, tuple) and c[0] == "formula":
            cell_xml += f'<table:table-cell table:formula="{c[1]}"><text:p>{c[2]}</text:p></table:table-cell>'
        else:
            cell_xml += f'<table:table-cell office:value-type="string"><text:p>{c}</text:p></table:table-cell>'
    return f"<table:table-row>{cell_xml}</table:table-row>"


class TestFodsEmptyCellCount:
    def test_all_filled(self, tmp_path):
        f = _make_fods(tmp_path, "filled", _row("a", "b") + _row("c", "d"))
        wb = parse_fods_strict(f)
        result = fods_empty_cell_count(wb)
        assert isinstance(result, int)

    def test_some_empty(self, tmp_path):
        f = _make_fods(tmp_path, "some_empty", _row("a", None) + _row(None, "d"))
        wb = parse_fods_strict(f)
        result = fods_empty_cell_count(wb)
        assert isinstance(result, int)
        assert result >= 0

    def test_empty_workbook(self, tmp_path):
        wb = {"sheets": []}
        assert fods_empty_cell_count(wb) == 0

    def test_returns_int(self, tmp_path):
        f = _make_fods(tmp_path, "type", _row("x"))
        wb = parse_fods_strict(f)
        assert isinstance(fods_empty_cell_count(wb), int)

    def test_non_negative(self, tmp_path):
        f = _make_fods(tmp_path, "nn", _row("a"))
        wb = parse_fods_strict(f)
        assert fods_empty_cell_count(wb) >= 0


class TestFodsHasFormulas:
    def test_no_formulas(self, tmp_path):
        f = _make_fods(tmp_path, "no_form", _row("a", "b"))
        wb = parse_fods_strict(f)
        assert fods_has_formulas(wb) is False

    def test_empty_workbook(self, tmp_path):
        wb = {"sheets": []}
        assert fods_has_formulas(wb) is False

    def test_returns_bool(self, tmp_path):
        f = _make_fods(tmp_path, "bool_type", _row("x"))
        wb = parse_fods_strict(f)
        assert isinstance(fods_has_formulas(wb), bool)

    def test_with_formula_cell(self, tmp_path):
        wb = {"sheets": [{"rows": [{"cells": [{"value": "1", "formula": "=SUM(A1:A2)"}]}]}]}
        assert fods_has_formulas(wb) is True

    def test_empty_formula_field(self, tmp_path):
        wb = {"sheets": [{"rows": [{"cells": [{"value": "1", "formula": ""}]}]}]}
        assert fods_has_formulas(wb) is False
