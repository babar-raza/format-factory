"""Tests for toml_numeric_value_count and toml_boolean_value_count (Sprint 23)."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from toml import toml_numeric_value_count, toml_boolean_value_count


def _make_toml(tmp_path, name, content):
    p = tmp_path / f"{name}.toml"
    p.write_text(content, encoding="utf-8")
    return str(p)


class TestTomlNumericValueCount:
    def test_all_numerics(self, tmp_path):
        p = _make_toml(tmp_path, "an", "x = 1\ny = 2.5\n")
        assert toml_numeric_value_count(p) == 2

    def test_mixed_types(self, tmp_path):
        p = _make_toml(tmp_path, "mt", 'x = 1\ns = "hello"\nb = true\n')
        assert toml_numeric_value_count(p) == 1

    def test_no_numerics(self, tmp_path):
        p = _make_toml(tmp_path, "nn", 'a = "text"\nb = true\n')
        assert toml_numeric_value_count(p) == 0

    def test_bool_not_counted_as_numeric(self, tmp_path):
        p = _make_toml(tmp_path, "bn", "flag = true\ncount = 5\n")
        assert toml_numeric_value_count(p) == 1

    def test_return_type(self, tmp_path):
        p = _make_toml(tmp_path, "rt", "x = 42\n")
        assert isinstance(toml_numeric_value_count(p), int)


class TestTomlBooleanValueCount:
    def test_all_booleans(self, tmp_path):
        p = _make_toml(tmp_path, "ab", "a = true\nb = false\n")
        assert toml_boolean_value_count(p) == 2

    def test_mixed(self, tmp_path):
        p = _make_toml(tmp_path, "mx", 'a = true\nb = 1\nc = "hello"\n')
        assert toml_boolean_value_count(p) == 1

    def test_no_booleans(self, tmp_path):
        p = _make_toml(tmp_path, "nb", "x = 1\ny = 2\n")
        assert toml_boolean_value_count(p) == 0

    def test_return_type(self, tmp_path):
        p = _make_toml(tmp_path, "rt2", "flag = true\n")
        assert isinstance(toml_boolean_value_count(p), int)

    def test_numeric_not_counted_as_bool(self, tmp_path):
        p = _make_toml(tmp_path, "nc", "x = 0\ny = 1\n")
        assert toml_boolean_value_count(p) == 0
