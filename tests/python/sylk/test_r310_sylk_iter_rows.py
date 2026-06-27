"""
tests/python/sylk/test_r310_sylk_iter_rows.py

Sprint: ff-sprint-s310-sylk-row-iterator-20260626
Authority: SYLK format — R (row) record

Tests for sylk_iter_rows() in sylk_row_iterator.py.
"""
from __future__ import annotations

from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_VALID_DIR = _REPO / "samples" / "by-format" / "sylk" / "valid"
_MINIMAL = _VALID_DIR / "minimal-2x2.slk"
_SINGLE = _VALID_DIR / "single-cell.slk"


class TestSylkIterRowsImport:
    def test_importable_from_sylk_row_iterator(self):
        from sylk.sylk_row_iterator import sylk_iter_rows
        assert callable(sylk_iter_rows)

    def test_importable_from_package(self):
        import sylk
        assert hasattr(sylk, "sylk_iter_rows")


class TestSylkIterRowsOutput:
    def test_returns_iterator(self):
        from sylk.sylk_row_iterator import sylk_iter_rows
        result = sylk_iter_rows(str(_MINIMAL))
        assert hasattr(result, "__iter__") and hasattr(result, "__next__")

    def test_minimal_yields_rows(self):
        from sylk.sylk_row_iterator import sylk_iter_rows
        rows = list(sylk_iter_rows(str(_MINIMAL)))
        assert len(rows) >= 1

    def test_row_type_is_spec_row(self):
        from sylk.sylk_row_iterator import sylk_iter_rows
        from sylk.spec.row.row import Row
        rows = list(sylk_iter_rows(str(_MINIMAL)))
        assert all(isinstance(r, Row) for r in rows)

    def test_row_has_spec_qname(self):
        from sylk.sylk_row_iterator import sylk_iter_rows
        rows = list(sylk_iter_rows(str(_MINIMAL)))
        assert all(hasattr(r, "spec_qname") for r in rows)

    def test_row_qname_value(self):
        from sylk.sylk_row_iterator import sylk_iter_rows
        rows = list(sylk_iter_rows(str(_MINIMAL)))
        assert all(r.spec_qname == "sylk:row" for r in rows)

    def test_row_has_index(self):
        from sylk.sylk_row_iterator import sylk_iter_rows
        rows = list(sylk_iter_rows(str(_MINIMAL)))
        for r in rows:
            assert isinstance(r.index, int) and r.index >= 1

    def test_row_has_cell_count(self):
        from sylk.sylk_row_iterator import sylk_iter_rows
        rows = list(sylk_iter_rows(str(_MINIMAL)))
        for r in rows:
            assert isinstance(r.cell_count, int) and r.cell_count >= 0

    def test_two_rows_for_2x2(self):
        from sylk.sylk_row_iterator import sylk_iter_rows
        rows = list(sylk_iter_rows(str(_MINIMAL)))
        assert len(rows) == 2

    def test_consistent(self):
        from sylk.sylk_row_iterator import sylk_iter_rows
        r1 = [r.index for r in sylk_iter_rows(str(_MINIMAL))]
        r2 = [r.index for r in sylk_iter_rows(str(_MINIMAL))]
        assert r1 == r2
