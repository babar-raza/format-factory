"""Tests for dif_numeric_cell_count function."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif.dif_parser import dif_numeric_cell_count


def _write_dif(tmp_path, vectors, tuples, data_rows):
    """Write a minimal DIF file.

    data_rows: list of lists, each inner list is a row of (type_indicator, numeric_value, string_value).
    type_indicator: 0 = numeric, 1 = string, -1 = BOT (begin of tuple), blank = special.
    """
    lines = [
        "TABLE", "0,1", '""',
        "VECTORS", f"0,{vectors}", '""',
        "TUPLES", f"0,{tuples}", '""',
        "DATA", "0,0", '""',
    ]
    for row in data_rows:
        lines.extend(["-1,0", "BOT"])  # begin of tuple
        for cell_type, num_val, str_val in row:
            if cell_type == 0:
                lines.extend([f"0,{num_val}", f'"{str_val}"'])
            else:
                lines.extend([f"1,0", f'"{str_val}"'])
    lines.extend(["-1,0", "EOD"])
    p = tmp_path / "test.dif"
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(p)


class TestDifNumericCellCount:
    def test_all_numeric(self, tmp_path):
        rows = [
            [(0, 10, ""), (0, 20, ""), (0, 30, "")],
        ]
        path = _write_dif(tmp_path, 3, 1, rows)
        assert dif_numeric_cell_count(path) == 3

    def test_all_string(self, tmp_path):
        rows = [
            [(1, 0, "hello"), (1, 0, "world")],
        ]
        path = _write_dif(tmp_path, 2, 1, rows)
        assert dif_numeric_cell_count(path) == 0

    def test_mixed(self, tmp_path):
        rows = [
            [(1, 0, "Name"), (1, 0, "Age")],
            [(1, 0, "Alice"), (0, 30, "")],
        ]
        path = _write_dif(tmp_path, 2, 2, rows)
        assert dif_numeric_cell_count(path) == 1

    def test_empty_document(self, tmp_path):
        path = _write_dif(tmp_path, 0, 0, [])
        assert dif_numeric_cell_count(path) == 0

    def test_multiple_rows_all_numeric(self, tmp_path):
        rows = [
            [(0, 1, ""), (0, 2, "")],
            [(0, 3, ""), (0, 4, "")],
            [(0, 5, ""), (0, 6, "")],
        ]
        path = _write_dif(tmp_path, 2, 3, rows)
        assert dif_numeric_cell_count(path) == 6

    def test_single_numeric_cell(self, tmp_path):
        rows = [[(0, 42, "")]]
        path = _write_dif(tmp_path, 1, 1, rows)
        assert dif_numeric_cell_count(path) == 1

    def test_importable_from_package(self):
        from dif import dif_numeric_cell_count as fn
        assert callable(fn)
