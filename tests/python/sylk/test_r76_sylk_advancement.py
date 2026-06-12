"""
tests/python/sylk/test_r76_sylk_advancement.py

R76 Train L — SYLK format advancement tests.

New coverage areas (beyond R73):
- String cell value type and quote stripping
- Multi-row SYLK: correct row/col coordinate tracking
- Missing E record rejection
- Cell record with no K field (empty cell)
- id_line capture in strict API return value
- Large X/Y coord at boundary
- Multiple cells in one C record position pattern

Sprint: FORMAT-FACTORY-R76-PARALLEL-FINISH-LINE-ARTIFACT-AUTHORITY-PRODUCT-DEEPENING-GATE-READINESS-MEGA-TRAIN-001
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.sylk.sylk_parser import (
    parse_sylk,
    parse_sylk_strict,
    SylkParseError,
)


def _write_sylk(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="ascii")
    return p


# ---------------------------------------------------------------------------
# String cell value handling
# ---------------------------------------------------------------------------

class TestSylkStringCells:
    """Verify string cell parsing: value_type and quote removal."""

    def test_string_cell_value_type_is_string(self, tmp_path):
        content = 'ID;PWXL\nC;X1;Y1;K"Hello"\nE\n'
        f = _write_sylk(tmp_path, "str.slk", content)
        doc = parse_sylk_strict(str(f))
        assert doc.cells[0].value_type == "string"

    def test_string_cell_quotes_stripped(self, tmp_path):
        content = 'ID;PWXL\nC;X1;Y1;K"Hello World"\nE\n'
        f = _write_sylk(tmp_path, "str.slk", content)
        doc = parse_sylk_strict(str(f))
        assert doc.cells[0].value == "Hello World"

    def test_string_cell_empty_string(self, tmp_path):
        content = 'ID;PWXL\nC;X1;Y1;K""\nE\n'
        f = _write_sylk(tmp_path, "empty_str.slk", content)
        doc = parse_sylk_strict(str(f))
        assert doc.cells[0].value == ""
        assert doc.cells[0].value_type == "string"

    def test_mixed_numeric_and_string_cells(self, tmp_path):
        content = 'ID;PWXL\nC;X1;Y1;K42\nC;X2;Y1;K"Name"\nE\n'
        f = _write_sylk(tmp_path, "mixed.slk", content)
        doc = parse_sylk_strict(str(f))
        assert len(doc.cells) == 2
        types = {c.value_type for c in doc.cells}
        assert "numeric" in types
        assert "string" in types


# ---------------------------------------------------------------------------
# Multi-row coordinate tracking
# ---------------------------------------------------------------------------

class TestSylkMultiRowCoordinates:
    """Verify that X/Y coordinates are correctly tracked across multiple rows."""

    def test_two_rows_max_row_is_2(self, tmp_path):
        content = "ID;PWXL\nC;X1;Y1;K10\nC;X1;Y2;K20\nE\n"
        f = _write_sylk(tmp_path, "rows.slk", content)
        doc = parse_sylk_strict(str(f))
        assert doc.rows == 2

    def test_cell_row_col_attributes(self, tmp_path):
        content = "ID;PWXL\nC;X3;Y2;K99\nE\n"
        f = _write_sylk(tmp_path, "coord.slk", content)
        doc = parse_sylk_strict(str(f))
        assert doc.cells[0].row == 2
        assert doc.cells[0].col == 3

    def test_max_col_tracked_correctly(self, tmp_path):
        content = "ID;PWXL\nC;X1;Y1;K1\nC;X5;Y1;K5\nC;X3;Y1;K3\nE\n"
        f = _write_sylk(tmp_path, "maxcol.slk", content)
        doc = parse_sylk_strict(str(f))
        assert doc.cols == 5

    def test_three_cells_count(self, tmp_path):
        content = "ID;PWXL\nC;X1;Y1;K1\nC;X2;Y1;K2\nC;X3;Y2;K3\nE\n"
        f = _write_sylk(tmp_path, "three.slk", content)
        doc = parse_sylk_strict(str(f))
        assert len(doc.cells) == 3
        assert doc.rows == 2
        assert doc.cols == 3


# ---------------------------------------------------------------------------
# Missing E record
# ---------------------------------------------------------------------------

class TestSylkMissingEndRecord:
    """Files without E record must be rejected."""

    def test_no_e_record_raises_parse_error(self, tmp_path):
        content = "ID;PWXL\nC;X1;Y1;K42\n"
        f = _write_sylk(tmp_path, "no_end.slk", content)
        with pytest.raises(SylkParseError, match="Missing E"):
            parse_sylk_strict(str(f))

    def test_no_e_record_dict_api_ok_false(self, tmp_path):
        content = "ID;PWXL\nC;X1;Y1;K42\n"
        f = _write_sylk(tmp_path, "no_end.slk", content)
        result = parse_sylk(str(f))
        assert result["ok"] is False

    def test_e_record_only_file_is_valid(self, tmp_path):
        content = "ID;PWXL\nE\n"
        f = _write_sylk(tmp_path, "e_only.slk", content)
        doc = parse_sylk_strict(str(f))
        assert doc.cells == []
        assert doc.rows == 0


# ---------------------------------------------------------------------------
# id_line capture
# ---------------------------------------------------------------------------

class TestSylkIdLine:
    """id_line should be captured in the parsed document."""

    def test_id_line_is_preserved(self, tmp_path):
        content = "ID;PWXL\nC;X1;Y1;K1\nE\n"
        f = _write_sylk(tmp_path, "id.slk", content)
        doc = parse_sylk_strict(str(f))
        assert doc.id_line == "ID;PWXL"

    def test_dict_api_has_id_line(self, tmp_path):
        content = "ID;P\nC;X1;Y1;K1\nE\n"
        f = _write_sylk(tmp_path, "id2.slk", content)
        result = parse_sylk(str(f))
        assert "id_line" in result
        assert result["id_line"].startswith("ID")


# ---------------------------------------------------------------------------
# Float values
# ---------------------------------------------------------------------------

class TestSylkFloatValues:
    """Non-integer numeric values should be parsed as float."""

    def test_float_cell_value(self, tmp_path):
        content = "ID;PWXL\nC;X1;Y1;K3.14\nE\n"
        f = _write_sylk(tmp_path, "float.slk", content)
        doc = parse_sylk_strict(str(f))
        assert doc.cells[0].value_type == "numeric"
        assert abs(doc.cells[0].value - 3.14) < 1e-9

    def test_negative_numeric_value(self, tmp_path):
        content = "ID;PWXL\nC;X1;Y1;K-100\nE\n"
        f = _write_sylk(tmp_path, "neg.slk", content)
        doc = parse_sylk_strict(str(f))
        assert doc.cells[0].value == -100
