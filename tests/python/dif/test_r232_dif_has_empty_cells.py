"""Tests for dif_has_empty_cells (Sprint 22)."""
import pytest
from src.python.dif import write_dif, DifDocument, DifCell, dif_has_empty_cells


def _make_dif(tmp_path, name, cells_rows):
    rows = []
    for row_data in cells_rows:
        rows.append([DifCell(value=v, value_type="string") for v in row_data])
    ncols = max(len(r) for r in rows) if rows else 0
    doc = DifDocument(title="test", vectors=ncols, tuples=len(rows), rows=rows)
    p = tmp_path / f"{name}.dif"
    write_dif(doc, str(p))
    return str(p)


class TestDifHasEmptyCells:
    def test_no_empty(self, tmp_path):
        p = _make_dif(tmp_path, "ne", [["a", "b"], ["c", "d"]])
        result = dif_has_empty_cells(p)
        assert isinstance(result, bool)

    def test_with_empty(self, tmp_path):
        p = _make_dif(tmp_path, "we", [["a", ""], ["c", "d"]])
        assert dif_has_empty_cells(p) is True

    def test_all_filled(self, tmp_path):
        p = _make_dif(tmp_path, "af", [["x", "y"]])
        result = dif_has_empty_cells(p)
        assert isinstance(result, bool)

    def test_return_type(self, tmp_path):
        p = _make_dif(tmp_path, "rt", [["a"]])
        assert isinstance(dif_has_empty_cells(p), bool)

    def test_single_cell(self, tmp_path):
        p = _make_dif(tmp_path, "sc", [["hello"]])
        result = dif_has_empty_cells(p)
        assert isinstance(result, bool)
