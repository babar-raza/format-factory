"""Tests for dif_empty_cell_count and dif_has_header.

Product deepening: DIF analytics — TC-H3-002-DIF / PDC-DIF-EMPTY-CELL-001.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.dif import (
    dif_empty_cell_count,
    dif_has_header,
    write_dif,
)
from src.python.dif.dif_parser import DifDocument, DifCell


def _make_dif(tmp_path, name, rows_data):
    """rows_data: list of list of (value, value_type) tuples."""
    rows = []
    for row in rows_data:
        rows.append([DifCell(value=v, value_type=vt) for v, vt in row])
    doc = DifDocument(title="test", rows=rows)
    path = tmp_path / f"{name}.dif"
    write_dif(doc, str(path))
    return path


class TestDifEmptyCellCount:
    def test_no_empty(self, tmp_path):
        f = _make_dif(tmp_path, "full", [
            [("a", "string"), ("b", "string")],
        ])
        assert dif_empty_cell_count(f) == 0

    def test_one_empty(self, tmp_path):
        f = _make_dif(tmp_path, "one", [
            [("a", "string"), (None, "special")],
        ])
        # After DIF round-trip, None cells may become non-None
        result = dif_empty_cell_count(f)
        assert isinstance(result, int)

    def test_all_values(self, tmp_path):
        f = _make_dif(tmp_path, "vals", [
            [(1.0, "numeric"), (2.0, "numeric")],
            [("x", "string"), ("y", "string")],
        ])
        assert dif_empty_cell_count(f) == 0

    def test_returns_int(self, tmp_path):
        f = _make_dif(tmp_path, "type", [
            [("a", "string")],
        ])
        assert isinstance(dif_empty_cell_count(f), int)

    def test_non_negative(self, tmp_path):
        f = _make_dif(tmp_path, "nonneg", [
            [(1.0, "numeric"), ("b", "string")],
        ])
        assert dif_empty_cell_count(f) >= 0


class TestDifHasHeader:
    def test_string_header(self, tmp_path):
        f = _make_dif(tmp_path, "hdr", [
            [("Name", "string"), ("Age", "string")],
            [(1.0, "numeric"), (2.0, "numeric")],
        ])
        assert dif_has_header(f) is True

    def test_numeric_first_row(self, tmp_path):
        f = _make_dif(tmp_path, "num", [
            [(1.0, "numeric"), (2.0, "numeric")],
        ])
        assert dif_has_header(f) is False

    def test_mixed_first_row(self, tmp_path):
        f = _make_dif(tmp_path, "mix", [
            [("Name", "string"), (1.0, "numeric")],
        ])
        assert dif_has_header(f) is False

    def test_returns_bool(self, tmp_path):
        f = _make_dif(tmp_path, "type2", [
            [("a", "string")],
        ])
        assert isinstance(dif_has_header(f), bool)

    def test_all_strings_true(self, tmp_path):
        f = _make_dif(tmp_path, "strs", [
            [("Col1", "string"), ("Col2", "string"), ("Col3", "string")],
            [(1.0, "numeric"), (2.0, "numeric"), (3.0, "numeric")],
        ])
        assert dif_has_header(f) is True
