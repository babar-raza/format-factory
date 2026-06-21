"""
Tests for TOML additional numeric analytics (2 new FOSS functions).
Closes: GAP-TOML-FOSS-TOML_MAX_NUM-001, GAP-TOML-FOSS-TOML_MIN_NUM-001

Known sample values (inline bytes):
  empty: max=0.0, min=0.0
  age=42: max=42.0, min=42.0
  a=1,b=10,c=-5: max=10.0, min=-5.0
  flag=true (bool only): max=0.0, min=0.0
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from toml.toml_codec import toml_max_numeric_value, toml_min_numeric_value

_EMPTY = b""
_SINGLE = b"age = 42\n"
_MULTI = b"a = 1\nb = 10\nc = -5\n"
_BOOL_ONLY = b"flag = true\n"
_FLOAT = b"pi = 3.14\nrate = 0.5\n"
_TEXT_ONLY = b'name = "Alice"\n'


class TestTomlMaxNumericValue:
    def test_returns_float(self):
        assert isinstance(toml_max_numeric_value(_EMPTY), float)

    def test_empty_doc_returns_zero(self):
        assert toml_max_numeric_value(_EMPTY) == 0.0

    def test_bool_only_returns_zero(self):
        # booleans excluded from numeric consideration
        assert toml_max_numeric_value(_BOOL_ONLY) == 0.0

    def test_text_only_returns_zero(self):
        assert toml_max_numeric_value(_TEXT_ONLY) == 0.0

    def test_single_int_returns_value(self):
        assert toml_max_numeric_value(_SINGLE) == 42.0

    def test_multi_returns_max(self):
        # a=1, b=10, c=-5 → max=10
        assert toml_max_numeric_value(_MULTI) == 10.0

    def test_float_values(self):
        # pi=3.14, rate=0.5 → max=3.14
        assert toml_max_numeric_value(_FLOAT) == pytest_approx(3.14)

    def test_max_gte_min(self):
        assert toml_max_numeric_value(_MULTI) >= toml_min_numeric_value(_MULTI)

    def test_all_return_float(self):
        for src in [_EMPTY, _SINGLE, _MULTI, _BOOL_ONLY]:
            assert isinstance(toml_max_numeric_value(src), float)


class TestTomlMinNumericValue:
    def test_returns_float(self):
        assert isinstance(toml_min_numeric_value(_EMPTY), float)

    def test_empty_doc_returns_zero(self):
        assert toml_min_numeric_value(_EMPTY) == 0.0

    def test_bool_only_returns_zero(self):
        assert toml_min_numeric_value(_BOOL_ONLY) == 0.0

    def test_text_only_returns_zero(self):
        assert toml_min_numeric_value(_TEXT_ONLY) == 0.0

    def test_single_int_returns_value(self):
        assert toml_min_numeric_value(_SINGLE) == 42.0

    def test_multi_returns_min(self):
        # a=1, b=10, c=-5 → min=-5
        assert toml_min_numeric_value(_MULTI) == -5.0

    def test_float_values(self):
        # pi=3.14, rate=0.5 → min=0.5
        assert toml_min_numeric_value(_FLOAT) == pytest_approx(0.5)

    def test_min_lte_max(self):
        assert toml_min_numeric_value(_MULTI) <= toml_max_numeric_value(_MULTI)

    def test_all_return_float(self):
        for src in [_EMPTY, _SINGLE, _MULTI, _BOOL_ONLY]:
            assert isinstance(toml_min_numeric_value(src), float)


def pytest_approx(val, rel=1e-6):
    import pytest
    return pytest.approx(val, rel=rel)
