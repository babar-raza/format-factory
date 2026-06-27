"""
tests/python/ods/test_r314_ods_iter_rows.py

Sprint: ff-sprint-s314-ods-row-iterator-20260626
Authority: ODF 1.3 §9.4 — table:table-row

Tests for ods_iter_rows() in ods_row_iterator.py.
"""
from __future__ import annotations

from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_VALID_DIR = _REPO / "samples" / "by-format" / "ods" / "valid"
_MINIMAL = _VALID_DIR / "minimal-spreadsheet.ods"


class TestOdsIterRowsImport:
    def test_importable_from_ods_row_iterator(self):
        from ods.ods_row_iterator import ods_iter_rows
        assert callable(ods_iter_rows)

    def test_importable_from_package(self):
        import ods
        assert hasattr(ods, "ods_iter_rows")


class TestOdsIterRowsOutput:
    def test_returns_iterator(self):
        from ods.ods_row_iterator import ods_iter_rows
        result = ods_iter_rows(str(_MINIMAL))
        assert hasattr(result, "__iter__") and hasattr(result, "__next__")

    def test_minimal_yields_rows(self):
        from ods.ods_row_iterator import ods_iter_rows
        rows = list(ods_iter_rows(str(_MINIMAL)))
        assert len(rows) >= 1

    def test_row_type_is_spec_table_row(self):
        from ods.ods_row_iterator import ods_iter_rows
        from ods.spec.table.table_row import TableRow
        rows = list(ods_iter_rows(str(_MINIMAL)))
        assert all(isinstance(r, TableRow) for r in rows)

    def test_row_has_spec_qname(self):
        from ods.ods_row_iterator import ods_iter_rows
        rows = list(ods_iter_rows(str(_MINIMAL)))
        assert all(hasattr(r, "spec_qname") for r in rows)

    def test_row_qname_value(self):
        from ods.ods_row_iterator import ods_iter_rows
        rows = list(ods_iter_rows(str(_MINIMAL)))
        assert all(r.spec_qname == "table:table-row" for r in rows)

    def test_row_has_cells(self):
        from ods.ods_row_iterator import ods_iter_rows
        rows = list(ods_iter_rows(str(_MINIMAL)))
        for r in rows:
            assert isinstance(r.cells, list)

    def test_consistent(self):
        from ods.ods_row_iterator import ods_iter_rows
        r1 = [len(r.cells) for r in ods_iter_rows(str(_MINIMAL))]
        r2 = [len(r.cells) for r in ods_iter_rows(str(_MINIMAL))]
        assert r1 == r2
