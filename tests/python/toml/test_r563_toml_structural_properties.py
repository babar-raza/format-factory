"""R563: TOML structural properties — is_flat, has_booleans, table_count.

Tests for TomlDocument structural properties added in R563.
Spec refs: FACT-TOML-002, FACT-TOML-004.
"""

import pytest
from pathlib import Path

import sys
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from toml.models import TomlDocument

SAMPLES = Path("samples/by-format/toml")


def _make_doc(data=None):
    """Build a minimal TomlDocument from a dict."""
    if data is None:
        data = {}
    return TomlDocument({"data": data})


class TestIsFlat:
    def test_no_nested_tables_is_flat(self):
        doc = _make_doc({"title": "hello", "count": 42})
        assert doc.is_flat is True

    def test_one_nested_table_not_flat(self):
        doc = _make_doc({"nested": {"key": "val"}})
        assert doc.is_flat is False

    def test_empty_doc_is_flat(self):
        doc = _make_doc({})
        assert doc.is_flat is True

    def test_only_scalars_is_flat(self):
        doc = _make_doc({"a": 1, "b": "two", "c": True, "d": [1, 2]})
        assert doc.is_flat is True

    def test_is_flat_type(self):
        doc = _make_doc({})
        assert isinstance(doc.is_flat, bool)

    def test_is_flat_inverse_of_has_nested_tables(self):
        for data in [{}, {"a": 1}, {"nested": {}}, {"a": 1, "b": {"c": 2}}]:
            doc = _make_doc(data)
            assert doc.is_flat != doc.has_nested_tables or (doc.is_flat and not doc.has_nested_tables)


class TestHasBooleans:
    def test_true_boolean(self):
        doc = _make_doc({"active": True})
        assert doc.has_booleans is True

    def test_false_boolean(self):
        doc = _make_doc({"enabled": False})
        assert doc.has_booleans is True

    def test_no_booleans(self):
        doc = _make_doc({"title": "hi", "count": 3})
        assert doc.has_booleans is False

    def test_empty_no_booleans(self):
        doc = _make_doc({})
        assert doc.has_booleans is False

    def test_has_booleans_type(self):
        doc = _make_doc({"flag": True})
        assert isinstance(doc.has_booleans, bool)

    def test_nested_bool_not_counted(self):
        # has_booleans only checks top-level
        doc = _make_doc({"nested": {"flag": True}})
        assert doc.has_booleans is False  # nested bool not counted at top level


class TestTableCount:
    def test_no_tables_zero_count(self):
        doc = _make_doc({"a": 1, "b": "text"})
        assert doc.table_count == 0

    def test_one_nested_table(self):
        doc = _make_doc({"section": {"key": "val"}})
        assert doc.table_count == 1

    def test_multiple_nested_tables(self):
        doc = _make_doc({"s1": {"k": 1}, "s2": {"k": 2}, "plain": "text"})
        assert doc.table_count == 2

    def test_empty_doc_zero_tables(self):
        doc = _make_doc({})
        assert doc.table_count == 0

    def test_table_count_type(self):
        doc = _make_doc({})
        assert isinstance(doc.table_count, int)

    def test_table_count_equals_nested_tables_count(self):
        data = {"a": {"x": 1}, "b": {"y": 2}, "c": 99}
        doc = _make_doc(data)
        assert doc.table_count == 2
        assert doc.has_nested_tables is True


class TestStructuralConsistency:
    def test_flat_implies_no_tables(self):
        doc = _make_doc({"a": 1, "b": "hi"})
        assert doc.is_flat
        assert doc.table_count == 0
        assert not doc.has_nested_tables

    def test_has_tables_implies_not_flat(self):
        doc = _make_doc({"section": {"key": "val"}})
        assert not doc.is_flat
        assert doc.table_count > 0
        assert doc.has_nested_tables

    def test_from_file(self):
        doc = TomlDocument.from_file(SAMPLES / "minimal.toml")
        assert isinstance(doc.is_flat, bool)
        assert isinstance(doc.has_booleans, bool)
        assert isinstance(doc.table_count, int)
        assert doc.is_flat == (not doc.has_nested_tables)
