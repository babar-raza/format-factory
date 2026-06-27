"""
tests/python/sylk/test_r290_sylk_iter_cells.py

Sprint: ff-sprint-s290-sylk-cell-iterator-20260626
Authority: SYLK (Symbolic Link) format specification

Tests for sylk_iter_cells() in sylk_cell_iterator.py.
"""
from __future__ import annotations

from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_MINIMAL = _REPO / "samples" / "by-format" / "sylk" / "valid" / "minimal-2x2.slk"
_SINGLE = _REPO / "samples" / "by-format" / "sylk" / "valid" / "single-cell.slk"


class TestSylkIterCellsImport:
    def test_importable_from_sylk_cell_iterator(self):
        from sylk.sylk_cell_iterator import sylk_iter_cells
        assert callable(sylk_iter_cells)

    def test_importable_from_package(self):
        import sylk
        assert hasattr(sylk, "sylk_iter_cells")


class TestSylkIterCellsOutput:
    def test_returns_iterator(self):
        from sylk.sylk_cell_iterator import sylk_iter_cells
        result = sylk_iter_cells(str(_MINIMAL))
        import types
        assert hasattr(result, "__iter__") and hasattr(result, "__next__")

    def test_minimal_yields_cells(self):
        from sylk.sylk_cell_iterator import sylk_iter_cells
        cells = list(sylk_iter_cells(str(_MINIMAL)))
        assert len(cells) >= 1

    def test_cell_type_is_spec_cell(self):
        from sylk.sylk_cell_iterator import sylk_iter_cells
        from sylk.spec.row.cell import Cell
        cells = list(sylk_iter_cells(str(_MINIMAL)))
        assert all(isinstance(c, Cell) for c in cells)

    def test_cell_has_spec_qname(self):
        from sylk.sylk_cell_iterator import sylk_iter_cells
        cells = list(sylk_iter_cells(str(_MINIMAL)))
        assert all(hasattr(c, "spec_qname") for c in cells)

    def test_cell_qname_value(self):
        from sylk.sylk_cell_iterator import sylk_iter_cells
        cells = list(sylk_iter_cells(str(_MINIMAL)))
        assert all(c.spec_qname == "sylk:cell" for c in cells)

    def test_cells_have_row_col(self):
        from sylk.sylk_cell_iterator import sylk_iter_cells
        cells = list(sylk_iter_cells(str(_MINIMAL)))
        for c in cells:
            assert isinstance(c.row, int) and c.row >= 1
            assert isinstance(c.col, int) and c.col >= 1

    def test_row_major_order(self):
        from sylk.sylk_cell_iterator import sylk_iter_cells
        cells = list(sylk_iter_cells(str(_MINIMAL)))
        for i in range(1, len(cells)):
            prev, curr = cells[i - 1], cells[i]
            assert (prev.row, prev.col) <= (curr.row, curr.col)

    def test_single_cell_doc(self):
        from sylk.sylk_cell_iterator import sylk_iter_cells
        cells = list(sylk_iter_cells(str(_SINGLE)))
        assert len(cells) == 1

    def test_minimal_2x2_has_4_cells(self):
        from sylk.sylk_cell_iterator import sylk_iter_cells
        cells = list(sylk_iter_cells(str(_MINIMAL)))
        assert len(cells) == 4
