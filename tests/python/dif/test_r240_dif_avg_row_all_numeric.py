"""Tests for dif_avg_row_length and dif_all_numeric (Sprint 30)."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from src.python.dif import write_dif, DifDocument, DifCell, dif_avg_row_length, dif_all_numeric


def _make_dif(tmp_path, name, rows, value_type="string"):
    dif_rows = []
    for row_data in rows:
        dif_rows.append([DifCell(value=str(v), value_type=value_type) for v in row_data])
    vectors = len(rows[0]) if rows else 0
    doc = DifDocument(title="test", vectors=vectors, tuples=len(rows), rows=dif_rows)
    p = tmp_path / f"{name}.dif"
    write_dif(doc, str(p))
    return str(p)


class TestDifAvgRowLength:
    def test_return_type(self, tmp_path):
        p = _make_dif(tmp_path, "rt", [["a", "b"]])
        assert isinstance(dif_avg_row_length(p), float)

    def test_two_cells_per_row(self, tmp_path):
        # 2 rows, each 2 cells -> avg = 2.0
        p = _make_dif(tmp_path, "tc", [["a", "b"], ["c", "d"]])
        assert dif_avg_row_length(p) == 2.0

    def test_single_row_two_cells(self, tmp_path):
        p = _make_dif(tmp_path, "sr", [["x", "y"]])
        assert dif_avg_row_length(p) == 2.0

    def test_nonnegative(self, tmp_path):
        p = _make_dif(tmp_path, "nn", [["a"]])
        assert dif_avg_row_length(p) >= 0.0

    def test_three_cells_avg(self, tmp_path):
        # 1 row, 3 cells -> 3.0
        p = _make_dif(tmp_path, "th", [["a", "b", "c"]])
        assert dif_avg_row_length(p) == 3.0


class TestDifAllNumeric:
    def test_return_type(self, tmp_path):
        p = _make_dif(tmp_path, "rt2", [["1", "2"]], value_type="float")
        assert isinstance(dif_all_numeric(p), bool)

    def test_all_numeric_true(self, tmp_path):
        p = _make_dif(tmp_path, "an", [["1", "2"], ["3", "4"]], value_type="float")
        assert dif_all_numeric(p) is True

    def test_string_cells_false(self, tmp_path):
        p = _make_dif(tmp_path, "sf", [["hello", "world"]], value_type="string")
        assert dif_all_numeric(p) is False

    def test_mixed_is_false(self, tmp_path):
        # row with "1" (numeric) and "abc" (string)
        dif_rows = [[DifCell(value="1", value_type="float"), DifCell(value="abc", value_type="string")]]
        doc = DifDocument(title="t", vectors=2, tuples=1, rows=dif_rows)
        p = tmp_path / "mixed.dif"
        write_dif(doc, str(p))
        assert dif_all_numeric(str(p)) is False

    def test_single_numeric_cell(self, tmp_path):
        p = _make_dif(tmp_path, "sn", [["42"]], value_type="float")
        assert dif_all_numeric(p) is True
