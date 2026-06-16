"""Tests for sylk_average_numeric_value and sylk_max_row_length.

Product deepening: SYLK analytics — TC-H3-002-SYLK / PDC-SYLK-AVG-NUMERIC-001.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.sylk import (
    sylk_average_numeric_value,
    sylk_max_row_length,
    write_sylk,
)
from src.python.sylk.sylk_parser import SylkDocument, SylkCell


def _make_sylk(tmp_path, name, cells_data):
    """cells_data: list of (row, col, value, value_type) tuples."""
    cells = [SylkCell(row=r, col=c, value=v, value_type=vt)
             for r, c, v, vt in cells_data]
    doc = SylkDocument(cells=cells)
    path = tmp_path / f"{name}.slk"
    write_sylk(doc, str(path))
    return path


class TestSylkAverageNumericValue:
    def test_single_numeric(self, tmp_path):
        f = _make_sylk(tmp_path, "one", [(1, 1, "10", "number")])
        assert sylk_average_numeric_value(f) == 10.0

    def test_multiple_numeric(self, tmp_path):
        f = _make_sylk(tmp_path, "multi", [
            (1, 1, "10", "number"),
            (1, 2, "20", "number"),
            (2, 1, "30", "number"),
        ])
        assert sylk_average_numeric_value(f) == 20.0

    def test_mixed_types(self, tmp_path):
        f = _make_sylk(tmp_path, "mix", [
            (1, 1, "5", "number"),
            (1, 2, "hello", "string"),
            (2, 1, "15", "number"),
        ])
        assert sylk_average_numeric_value(f) == 10.0

    def test_no_numerics(self, tmp_path):
        f = _make_sylk(tmp_path, "strs", [
            (1, 1, "hello", "string"),
        ])
        assert sylk_average_numeric_value(f) == 0.0

    def test_returns_float(self, tmp_path):
        f = _make_sylk(tmp_path, "type", [(1, 1, "42", "number")])
        assert isinstance(sylk_average_numeric_value(f), float)


class TestSylkMaxRowLength:
    def test_single_cell(self, tmp_path):
        f = _make_sylk(tmp_path, "one_r", [(1, 1, "a", "string")])
        assert sylk_max_row_length(f) == 1

    def test_two_cells_same_row(self, tmp_path):
        f = _make_sylk(tmp_path, "two_r", [
            (1, 1, "a", "string"),
            (1, 2, "b", "string"),
        ])
        assert sylk_max_row_length(f) == 2

    def test_different_row_lengths(self, tmp_path):
        f = _make_sylk(tmp_path, "diff", [
            (1, 1, "a", "string"),
            (1, 2, "b", "string"),
            (1, 3, "c", "string"),
            (2, 1, "d", "string"),
        ])
        assert sylk_max_row_length(f) == 3

    def test_returns_int(self, tmp_path):
        f = _make_sylk(tmp_path, "type_r", [(1, 1, "x", "string")])
        assert isinstance(sylk_max_row_length(f), int)

    def test_multiple_rows_equal(self, tmp_path):
        f = _make_sylk(tmp_path, "eq", [
            (1, 1, "a", "string"),
            (1, 2, "b", "string"),
            (2, 1, "c", "string"),
            (2, 2, "d", "string"),
        ])
        assert sylk_max_row_length(f) == 2
