"""R1226: TOML document classification properties — has_only_scalars, is_mixed, array_count.

Tests for TomlDocument classification properties added in R1226.
Spec refs: SAL-TOML-00001 (toml:table structure).
"""

from __future__ import annotations

import pytest
from pathlib import Path

import sys
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from toml.models import TomlDocument

SAMPLE = Path("samples/by-format/toml/minimal.toml")


def _make_doc(data: dict) -> TomlDocument:
    """Build a TomlDocument from a raw dict."""
    return TomlDocument(data)


class TestHasOnlyScalars:
    def test_empty_doc_no_only_scalars(self):
        doc = _make_doc({})
        assert doc.has_only_scalars is False

    def test_all_scalars_true(self):
        doc = _make_doc({"a": 1, "b": "hello", "c": True})
        assert doc.has_only_scalars is True

    def test_has_nested_table_false(self):
        doc = _make_doc({"a": 1, "b": {"nested": 2}})
        assert doc.has_only_scalars is False

    def test_has_array_false(self):
        doc = _make_doc({"a": 1, "b": [1, 2, 3]})
        assert doc.has_only_scalars is False

    def test_mixed_content_false(self):
        doc = _make_doc({"a": 1, "b": {"x": 2}, "c": [3]})
        assert doc.has_only_scalars is False

    def test_returns_bool(self):
        doc = _make_doc({"key": "value"})
        assert isinstance(doc.has_only_scalars, bool)

    def test_single_scalar_true(self):
        doc = _make_doc({"version": "1.0"})
        assert doc.has_only_scalars is True


class TestIsMixed:
    def test_empty_not_mixed(self):
        doc = _make_doc({})
        assert doc.is_mixed is False

    def test_only_scalars_not_mixed(self):
        doc = _make_doc({"a": 1, "b": "x"})
        assert doc.is_mixed is False

    def test_only_tables_not_mixed(self):
        """No scalars → not mixed."""
        doc = _make_doc({"t": {"x": 1}})
        assert doc.is_mixed is False

    def test_scalar_and_table_is_mixed(self):
        doc = _make_doc({"name": "app", "settings": {"debug": True}})
        assert doc.is_mixed is True

    def test_scalar_and_array_is_mixed(self):
        doc = _make_doc({"version": "1.0", "deps": ["a", "b"]})
        assert doc.is_mixed is True

    def test_returns_bool(self):
        doc = _make_doc({"a": 1, "b": {"c": 2}})
        assert isinstance(doc.is_mixed, bool)


class TestArrayCount:
    def test_empty_doc_zero(self):
        doc = _make_doc({})
        assert doc.array_count == 0

    def test_no_arrays_zero(self):
        doc = _make_doc({"a": 1, "b": {"c": 2}})
        assert doc.array_count == 0

    def test_one_array(self):
        doc = _make_doc({"a": [1, 2, 3]})
        assert doc.array_count == 1

    def test_two_arrays(self):
        doc = _make_doc({"a": [1], "b": [2, 3], "c": "x"})
        assert doc.array_count == 2

    def test_all_arrays(self):
        doc = _make_doc({"x": [1], "y": [2], "z": [3]})
        assert doc.array_count == 3

    def test_returns_int(self):
        doc = _make_doc({"a": [1]})
        assert isinstance(doc.array_count, int)

    def test_nested_list_not_counted_separately(self):
        """Only top-level arrays count."""
        doc = _make_doc({"a": [[1, 2], [3, 4]]})
        assert doc.array_count == 1

    def test_from_file(self):
        doc = TomlDocument.from_file(SAMPLE)
        assert isinstance(doc.array_count, int)
        assert doc.array_count >= 0
