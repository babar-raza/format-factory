"""
Tests for Sprint r315: toml_bool_count, toml_has_boolean_value.
Uses inline bytes — no sample files required.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.toml.toml_codec import toml_bool_count, toml_has_boolean_value

_T1 = b'a = true\nb = false\nc = 1\n'
_T2 = b'x = 1\ny = 2\n'
_T3 = b'flag = true\nval = 42\n'


# --- toml_bool_count ---

def test_toml_bool_count_t1_two():
    assert toml_bool_count(_T1) == 2


def test_toml_bool_count_t2_zero():
    assert toml_bool_count(_T2) == 0


def test_toml_bool_count_t3_one():
    assert toml_bool_count(_T3) == 1


def test_toml_bool_count_returns_int_t1():
    assert isinstance(toml_bool_count(_T1), int)


def test_toml_bool_count_returns_int_t2():
    assert isinstance(toml_bool_count(_T2), int)


def test_toml_bool_count_all_three_distinct():
    results = [
        toml_bool_count(_T1),
        toml_bool_count(_T2),
        toml_bool_count(_T3),
    ]
    assert results == [2, 0, 1]


# --- toml_has_boolean_value ---

def test_toml_has_boolean_value_t1_true():
    assert toml_has_boolean_value(_T1) is True


def test_toml_has_boolean_value_t2_false():
    assert toml_has_boolean_value(_T2) is False


def test_toml_has_boolean_value_t3_true():
    assert toml_has_boolean_value(_T3) is True


def test_toml_has_boolean_value_returns_bool_t1():
    assert isinstance(toml_has_boolean_value(_T1), bool)


def test_toml_has_boolean_value_returns_bool_t2():
    assert isinstance(toml_has_boolean_value(_T2), bool)


def test_toml_has_boolean_value_all_three():
    results = [
        toml_has_boolean_value(_T1),
        toml_has_boolean_value(_T2),
        toml_has_boolean_value(_T3),
    ]
    assert results == [True, False, True]
