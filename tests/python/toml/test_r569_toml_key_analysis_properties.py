"""R569: TOML key analysis properties — has_scalars, is_single_key, is_nested.

Tests for TomlDocument key analysis properties added in R569.
Spec refs: SAL-TOML-00001.
"""

import pytest
from pathlib import Path

import sys
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from toml.models import TomlDocument

SAMPLES = Path("samples/by-format/toml")


def _make_doc(data: dict):
    """Build a minimal TomlDocument from a dict."""
    return TomlDocument({"data": data})


class TestHasScalars:
    def test_one_scalar_key(self):
        doc = _make_doc({"name": "Alice"})
        assert doc.has_scalars is True

    def test_multiple_scalar_keys(self):
        doc = _make_doc({"a": 1, "b": "hello", "c": True})
        assert doc.has_scalars is True

    def test_no_scalars_only_tables(self):
        doc = _make_doc({"server": {"host": "localhost"}})
        assert doc.has_scalars is False

    def test_empty_doc_no_scalars(self):
        doc = _make_doc({})
        assert doc.has_scalars is False

    def test_has_scalars_type(self):
        doc = _make_doc({"x": 1})
        assert isinstance(doc.has_scalars, bool)

    def test_has_scalars_consistent_with_scalar_key_count(self):
        for data in [{}, {"a": 1}, {"a": 1, "b": {"c": 2}}]:
            doc = _make_doc(data)
            assert doc.has_scalars == (doc.scalar_key_count > 0)


class TestIsSingleKey:
    def test_one_key_is_single(self):
        doc = _make_doc({"key": "value"})
        assert doc.is_single_key is True

    def test_zero_keys_not_single(self):
        doc = _make_doc({})
        assert doc.is_single_key is False

    def test_two_keys_not_single(self):
        doc = _make_doc({"a": 1, "b": 2})
        assert doc.is_single_key is False

    def test_single_table_key(self):
        doc = _make_doc({"server": {"host": "localhost"}})
        assert doc.is_single_key is True

    def test_is_single_key_type(self):
        doc = _make_doc({"x": 1})
        assert isinstance(doc.is_single_key, bool)

    def test_is_single_key_consistent_with_key_count(self):
        for n in range(5):
            keys = {f"k{i}": i for i in range(n)}
            doc = _make_doc(keys)
            assert doc.is_single_key == (n == 1)


class TestIsNested:
    def test_nested_table_is_nested(self):
        doc = _make_doc({"server": {"host": "localhost"}})
        assert doc.is_nested is True

    def test_array_is_nested(self):
        doc = _make_doc({"tags": ["a", "b"]})
        assert doc.is_nested is True

    def test_flat_doc_not_nested(self):
        doc = _make_doc({"name": "Alice", "age": 30})
        assert doc.is_nested is False

    def test_empty_doc_not_nested(self):
        doc = _make_doc({})
        assert doc.is_nested is False

    def test_is_nested_type(self):
        doc = _make_doc({"a": 1})
        assert isinstance(doc.is_nested, bool)

    def test_nested_implies_not_flat(self):
        doc = _make_doc({"table": {"key": "val"}})
        assert doc.is_nested
        assert not doc.is_flat


class TestKeyAnalysisConsistency:
    def test_single_key_consistent(self):
        doc = _make_doc({"only": "one"})
        assert doc.is_single_key
        assert doc.key_count == 1

    def test_has_scalars_and_tables(self):
        doc = _make_doc({"name": "Alice", "server": {"host": "localhost"}})
        assert doc.has_scalars
        assert doc.is_nested

    def test_is_nested_equals_has_nested_or_arrays(self):
        for data in [{}, {"a": 1}, {"t": {"k": "v"}}, {"arr": [1, 2]}]:
            doc = _make_doc(data)
            assert doc.is_nested == (doc.has_nested_tables or doc.has_arrays)

    def test_from_file_minimal(self):
        doc = TomlDocument.from_file(SAMPLES / "minimal.toml")
        assert isinstance(doc.has_scalars, bool)
        assert isinstance(doc.is_single_key, bool)
        assert isinstance(doc.is_nested, bool)
