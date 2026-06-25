"""Tests for TomlDocument computed properties: is_empty, has_nested_tables,
has_arrays, scalar_key_count.

Sprint: FORMAT-FACTORY-TOML-PYTHON-PROPS-20260625
Ledger: R118-GOVERNED-PYTHON-TOML-DOCUMENT-PROPS-001
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO / "src" / "python") not in sys.path:
    sys.path.insert(0, str(_REPO / "src" / "python"))

from toml.models import TomlDocument


def _doc(data: dict) -> TomlDocument:
    return TomlDocument(data)


class TestIsEmpty:
    def test_empty_dict_returns_true(self):
        assert _doc({}).is_empty

    def test_one_key_returns_false(self):
        assert not _doc({"a": 1}).is_empty

    def test_nested_empty_still_not_empty_if_has_key(self):
        assert not _doc({"nested": {}}).is_empty


class TestHasNestedTables:
    def test_no_tables_returns_false(self):
        assert not _doc({"a": 1, "b": "hello"}).has_nested_tables

    def test_dict_value_returns_true(self):
        assert _doc({"server": {"host": "localhost"}}).has_nested_tables

    def test_empty_dict_value_returns_true(self):
        assert _doc({"empty_table": {}}).has_nested_tables

    def test_only_scalars_returns_false(self):
        assert not _doc({"x": 1, "y": 2.0, "z": True}).has_nested_tables

    def test_mixed_table_and_scalar_returns_true(self):
        assert _doc({"a": 1, "b": {"c": 2}}).has_nested_tables


class TestHasArrays:
    def test_no_arrays_returns_false(self):
        assert not _doc({"a": 1, "b": "text"}).has_arrays

    def test_list_value_returns_true(self):
        assert _doc({"ports": [8080, 8443]}).has_arrays

    def test_empty_list_value_returns_true(self):
        assert _doc({"items": []}).has_arrays

    def test_only_dicts_and_scalars_returns_false(self):
        assert not _doc({"a": 1, "b": {"c": 2}}).has_arrays


class TestScalarKeyCount:
    def test_all_scalars_returns_total(self):
        assert _doc({"a": 1, "b": "x", "c": True}).scalar_key_count == 3

    def test_empty_doc_returns_zero(self):
        assert _doc({}).scalar_key_count == 0

    def test_only_tables_returns_zero(self):
        assert _doc({"x": {}, "y": {"k": "v"}}).scalar_key_count == 0

    def test_mixed_counts_only_scalars(self):
        # 2 scalars, 1 table, 1 array
        d = {"a": 1, "b": "text", "c": {"nested": True}, "d": [1, 2, 3]}
        assert _doc(d).scalar_key_count == 2
