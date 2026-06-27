"""
tests/python/toml/test_r309_toml_iter_tables.py

Sprint: ff-sprint-s309-toml-table-iterator-20260626
Authority: TOML v1.0.0 — Tables

Tests for toml_iter_tables() in toml_table_iterator.py.
"""
from __future__ import annotations

from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_MINIMAL = _REPO / "samples" / "by-format" / "toml" / "minimal.toml"


class TestTomlIterTablesImport:
    def test_importable_from_toml_table_iterator(self):
        from toml.toml_table_iterator import toml_iter_tables
        assert callable(toml_iter_tables)

    def test_importable_from_package(self):
        import toml
        assert hasattr(toml, "toml_iter_tables")


class TestTomlIterTablesOutput:
    def test_returns_iterator(self):
        from toml.toml_table_iterator import toml_iter_tables
        result = toml_iter_tables(str(_MINIMAL))
        assert hasattr(result, "__iter__") and hasattr(result, "__next__")

    def test_minimal_yields_tables(self):
        from toml.toml_table_iterator import toml_iter_tables
        tables = list(toml_iter_tables(str(_MINIMAL)))
        assert len(tables) >= 1

    def test_table_type_is_spec_table(self):
        from toml.toml_table_iterator import toml_iter_tables
        from toml.spec.table.table import Table
        tables = list(toml_iter_tables(str(_MINIMAL)))
        assert all(isinstance(t, Table) for t in tables)

    def test_table_has_spec_qname(self):
        from toml.toml_table_iterator import toml_iter_tables
        tables = list(toml_iter_tables(str(_MINIMAL)))
        assert all(hasattr(t, "spec_qname") for t in tables)

    def test_table_qname_value(self):
        from toml.toml_table_iterator import toml_iter_tables
        tables = list(toml_iter_tables(str(_MINIMAL)))
        assert all(t.spec_qname == "toml:table" for t in tables)

    def test_table_has_keys(self):
        from toml.toml_table_iterator import toml_iter_tables
        tables = list(toml_iter_tables(str(_MINIMAL)))
        for t in tables:
            assert isinstance(t.keys, list)

    def test_table_has_key_count(self):
        from toml.toml_table_iterator import toml_iter_tables
        tables = list(toml_iter_tables(str(_MINIMAL)))
        for t in tables:
            assert isinstance(t.key_count, int) and t.key_count >= 0

    def test_consistent(self):
        from toml.toml_table_iterator import toml_iter_tables
        r1 = [t.key_count for t in toml_iter_tables(str(_MINIMAL))]
        r2 = [t.key_count for t in toml_iter_tables(str(_MINIMAL))]
        assert r1 == r2
