"""Tests for TOML get_all_keys function (rnext37)."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from src.python.toml.toml_codec import get_all_keys


class TestGetAllKeys:
    def _src(self, text: str) -> bytes:
        return text.encode("utf-8")

    def test_simple_keys(self):
        src = self._src("name = 'Alice'\nage = 30\n")
        keys = get_all_keys(src)
        assert "name" in keys
        assert "age" in keys

    def test_nested_keys(self):
        src = self._src("[section]\nfoo = 1\nbar = 2\n")
        keys = get_all_keys(src)
        assert "section" in keys
        assert "section.foo" in keys
        assert "section.bar" in keys

    def test_empty_toml(self):
        src = self._src("")
        keys = get_all_keys(src)
        assert keys == []

    def test_deep_nesting(self):
        src = self._src("[a.b]\nvalue = 1\n")
        keys = get_all_keys(src)
        assert "a" in keys
        assert "a.b" in keys
        assert "a.b.value" in keys

    def test_sorted_output(self):
        src = self._src("z = 1\na = 2\nm = 3\n")
        keys = get_all_keys(src)
        assert keys == sorted(keys)
