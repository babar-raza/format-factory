"""
test_r160_toml_diff_rename.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT20-001
Added: 2026-06-10

Tests for TOML diff_keys and rename_key functions.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.toml.toml_codec import diff_keys, rename_key, TomlError


class TestDiffKeys:
    def test_identical(self, tmp_path):
        a = tmp_path / "a.toml"
        b = tmp_path / "b.toml"
        a.write_text("x = 1\ny = 2\n")
        b.write_text("x = 1\ny = 2\n")
        assert diff_keys(a, b) == []

    def test_a_has_extra(self, tmp_path):
        a = tmp_path / "a.toml"
        b = tmp_path / "b.toml"
        a.write_text("x = 1\ny = 2\nz = 3\n")
        b.write_text("x = 1\n")
        assert diff_keys(a, b) == ["y", "z"]

    def test_b_has_extra(self, tmp_path):
        a = tmp_path / "a.toml"
        b = tmp_path / "b.toml"
        a.write_text("x = 1\n")
        b.write_text("x = 1\ny = 2\n")
        assert diff_keys(a, b) == []

    def test_disjoint(self, tmp_path):
        a = tmp_path / "a.toml"
        b = tmp_path / "b.toml"
        a.write_text("alpha = 1\nbeta = 2\n")
        b.write_text("gamma = 3\n")
        assert diff_keys(a, b) == ["alpha", "beta"]

    def test_from_bytes(self, tmp_path):
        result = diff_keys(b"a = 1\nb = 2\n", b"a = 1\n")
        assert result == ["b"]

    def test_empty_a(self, tmp_path):
        a = tmp_path / "a.toml"
        b = tmp_path / "b.toml"
        a.write_text("")
        b.write_text("x = 1\n")
        assert diff_keys(a, b) == []


class TestRenameKey:
    def test_basic_rename(self):
        data = {"old": 1, "other": 2}
        result = rename_key(data, "old", "new")
        assert result == {"new": 1, "other": 2}
        assert "old" not in result

    def test_preserves_order(self):
        data = {"a": 1, "b": 2, "c": 3}
        result = rename_key(data, "b", "beta")
        assert list(result.keys()) == ["a", "beta", "c"]

    def test_missing_key_raises(self):
        with pytest.raises(KeyError):
            rename_key({"a": 1}, "missing", "new")

    def test_existing_new_key_raises(self):
        with pytest.raises(ValueError):
            rename_key({"a": 1, "b": 2}, "a", "b")

    def test_rename_section(self):
        data = {"old_section": {"key": "value"}, "other": 1}
        result = rename_key(data, "old_section", "new_section")
        assert result["new_section"] == {"key": "value"}
        assert "old_section" not in result
