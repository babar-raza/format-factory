"""Tests for dif_row_count and dif_column_count.

Product deepening: DIF analytics — TC-H3-002-DIF / PDC-DIF-ROWCOL-001.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.dif import write_dif, DifDocument, DifCell, dif_row_count, dif_column_count


def _make_dif(tmp_path, name, rows):
    dif_rows = []
    for row_data in rows:
        dif_rows.append([DifCell(value=v, value_type="string") for v in row_data])
    doc = DifDocument(title="test", vectors=len(rows[0]) if rows else 0, tuples=len(rows), rows=dif_rows)
    p = tmp_path / f"{name}.dif"
    write_dif(doc, str(p))
    return p


class TestDifRowCount:
    def test_two_rows(self, tmp_path):
        p = _make_dif(tmp_path, "two", [["a", "b"], ["c", "d"]])
        assert dif_row_count(p) == 2

    def test_one_row(self, tmp_path):
        p = _make_dif(tmp_path, "one", [["x", "y"]])
        assert dif_row_count(p) == 1

    def test_returns_int(self, tmp_path):
        p = _make_dif(tmp_path, "ft", [["a"]])
        assert isinstance(dif_row_count(p), int)

    def test_non_negative(self, tmp_path):
        p = _make_dif(tmp_path, "nn", [["a"]])
        assert dif_row_count(p) >= 0

    def test_multi_rows(self, tmp_path):
        p = _make_dif(tmp_path, "multi", [["a"], ["b"], ["c"]])
        assert dif_row_count(p) == 3


class TestDifColumnCount:
    def test_two_columns(self, tmp_path):
        p = _make_dif(tmp_path, "twocol", [["a", "b"], ["c", "d"]])
        assert dif_column_count(p) == 2

    def test_one_column(self, tmp_path):
        p = _make_dif(tmp_path, "onecol", [["x"], ["y"]])
        assert dif_column_count(p) == 1

    def test_returns_int(self, tmp_path):
        p = _make_dif(tmp_path, "ft2", [["a", "b"]])
        assert isinstance(dif_column_count(p), int)

    def test_three_columns(self, tmp_path):
        p = _make_dif(tmp_path, "three", [["a", "b", "c"]])
        assert dif_column_count(p) == 3

    def test_non_negative(self, tmp_path):
        p = _make_dif(tmp_path, "nn2", [["x"]])
        assert dif_column_count(p) >= 0
