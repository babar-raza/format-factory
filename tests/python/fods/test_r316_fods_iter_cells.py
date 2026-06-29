"""
tests/python/fods/test_r316_fods_iter_cells.py

Sprint: ff-sprint-s316-fods-cell-iterator-20260626
Authority: ODF 1.3 §9.1 — table:table-cell

Tests for fods_iter_cells() in fods_cell_iterator.py.
"""
from __future__ import annotations

from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_MINIMAL = _REPO / "samples" / "by-format" / "fods" / "minimal-spreadsheet.fods"
_TYPED = _REPO / "samples" / "by-format" / "fods" / "typed-values-basic.fods"


class TestFodsIterCellsImport:
    def test_importable_from_fods_cell_iterator(self):
        from fods.fods_cell_iterator import fods_iter_cells
        assert callable(fods_iter_cells)

    def test_importable_from_package(self):
        import fods
        assert hasattr(fods, "fods_iter_cells")


class TestFodsIterCellsOutput:
    def test_returns_iterator(self):
        from fods.fods_cell_iterator import fods_iter_cells
        result = fods_iter_cells(str(_MINIMAL))
        assert hasattr(result, "__iter__") and hasattr(result, "__next__")

    def test_minimal_yields_cells(self):
        from fods.fods_cell_iterator import fods_iter_cells
        cells = list(fods_iter_cells(str(_MINIMAL)))
        assert len(cells) >= 1

    def test_cell_type_is_fods_cell(self):
        from fods.fods_cell_iterator import fods_iter_cells
        from fods.models import FodsCell
        cells = list(fods_iter_cells(str(_MINIMAL)))
        assert all(isinstance(c, FodsCell) for c in cells)

    def test_cell_has_spec_qname(self):
        from fods.fods_cell_iterator import fods_iter_cells
        cells = list(fods_iter_cells(str(_MINIMAL)))
        assert all(hasattr(c, "spec_qname") for c in cells)

    def test_cell_qname_value(self):
        from fods.fods_cell_iterator import fods_iter_cells
        cells = list(fods_iter_cells(str(_MINIMAL)))
        assert all(c.spec_qname == "table:table-cell" for c in cells)

    def test_cell_has_value_type(self):
        from fods.fods_cell_iterator import fods_iter_cells
        cells = list(fods_iter_cells(str(_MINIMAL)))
        for c in cells:
            assert isinstance(c.value_type, str)

    def test_typed_values_file_yields_multiple(self):
        from fods.fods_cell_iterator import fods_iter_cells
        cells = list(fods_iter_cells(str(_TYPED)))
        assert len(cells) >= 2

    def test_consistent(self):
        from fods.fods_cell_iterator import fods_iter_cells
        r1 = [c.value_type for c in fods_iter_cells(str(_MINIMAL))]
        r2 = [c.value_type for c in fods_iter_cells(str(_MINIMAL))]
        assert r1 == r2
