"""
Sprint 52 — 5 new NDJSON analytics functions.
Tests: ndjson_numeric_field_count, ndjson_bool_field_count, ndjson_null_field_count,
       ndjson_unique_key_count, ndjson_avg_string_value_length
"""
import sys
import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson import (
    ndjson_numeric_field_count,
    ndjson_bool_field_count,
    ndjson_null_field_count,
    ndjson_unique_key_count,
    ndjson_avg_string_value_length,
)


def _ndjson(*records) -> bytes:
    return b"\n".join(json.dumps(r).encode() for r in records)


_SRC_MIXED = _ndjson(
    {"name": "Alice", "age": 30, "active": True, "score": None},
    {"name": "Bob", "age": 25, "active": False},
    {"name": "Carol", "age": 35},
)
_SRC_NUMERIC = _ndjson({"x": 1, "y": 2.5}, {"x": 3, "y": 4.0})
_SRC_BOOL = _ndjson({"flag": True}, {"flag": False, "ok": True})
_SRC_EMPTY = b""


# --- ndjson_numeric_field_count ---

def test_numeric_field_count_numeric_is_int():
    assert isinstance(ndjson_numeric_field_count(_SRC_NUMERIC), int)


def test_numeric_field_count_numeric_positive():
    assert ndjson_numeric_field_count(_SRC_NUMERIC) >= 1


def test_numeric_field_count_mixed_positive():
    assert ndjson_numeric_field_count(_SRC_MIXED) >= 1


def test_numeric_field_count_empty_is_zero():
    assert ndjson_numeric_field_count(_SRC_EMPTY) == 0


# --- ndjson_bool_field_count ---

def test_bool_field_count_bool_is_int():
    assert isinstance(ndjson_bool_field_count(_SRC_BOOL), int)


def test_bool_field_count_bool_positive():
    assert ndjson_bool_field_count(_SRC_BOOL) >= 1


def test_bool_field_count_mixed_positive():
    assert ndjson_bool_field_count(_SRC_MIXED) >= 1


def test_bool_field_count_numeric_is_zero():
    assert ndjson_bool_field_count(_SRC_NUMERIC) == 0


# --- ndjson_null_field_count ---

def test_null_field_count_mixed_is_int():
    assert isinstance(ndjson_null_field_count(_SRC_MIXED), int)


def test_null_field_count_mixed_positive():
    # _SRC_MIXED has score: null
    assert ndjson_null_field_count(_SRC_MIXED) >= 1


def test_null_field_count_numeric_is_zero():
    assert ndjson_null_field_count(_SRC_NUMERIC) == 0


def test_null_field_count_empty_is_zero():
    assert ndjson_null_field_count(_SRC_EMPTY) == 0


# --- ndjson_unique_key_count ---

def test_unique_key_count_mixed_is_int():
    assert isinstance(ndjson_unique_key_count(_SRC_MIXED), int)


def test_unique_key_count_mixed_positive():
    assert ndjson_unique_key_count(_SRC_MIXED) >= 1


def test_unique_key_count_numeric_positive():
    assert ndjson_unique_key_count(_SRC_NUMERIC) >= 1


def test_unique_key_count_empty_is_zero():
    assert ndjson_unique_key_count(_SRC_EMPTY) == 0


# --- ndjson_avg_string_value_length ---

def test_avg_string_value_length_mixed_is_float():
    assert isinstance(ndjson_avg_string_value_length(_SRC_MIXED), float)


def test_avg_string_value_length_mixed_positive():
    assert ndjson_avg_string_value_length(_SRC_MIXED) > 0.0


def test_avg_string_value_length_numeric_is_zero():
    assert ndjson_avg_string_value_length(_SRC_NUMERIC) == 0.0


def test_avg_string_value_length_empty_is_zero():
    assert ndjson_avg_string_value_length(_SRC_EMPTY) == 0.0
