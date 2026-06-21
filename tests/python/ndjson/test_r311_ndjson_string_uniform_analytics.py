"""
Tests for Sprint r311: ndjson_string_value_count, ndjson_has_uniform_types.
No sample files — uses inline bytes.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import ndjson_string_value_count, ndjson_has_uniform_types

_S1 = b'{"name": "alice", "age": 30}\n{"name": "bob", "age": 25}\n'
_S2 = b'{"x": 1}\n{"y": 2}\n'
_S3 = b'"hello"\n42\n'


# --- ndjson_string_value_count ---

def test_ndjson_string_value_count_s1_two():
    # Two dicts each with one string value ("alice", "bob")
    assert ndjson_string_value_count(_S1) == 2


def test_ndjson_string_value_count_s2_zero():
    # Two dicts with only numeric values
    assert ndjson_string_value_count(_S2) == 0


def test_ndjson_string_value_count_s3_zero():
    # Records are string and int, not dicts — no dict string values
    assert ndjson_string_value_count(_S3) == 0


def test_ndjson_string_value_count_returns_int_s1():
    assert isinstance(ndjson_string_value_count(_S1), int)


def test_ndjson_string_value_count_returns_int_s2():
    assert isinstance(ndjson_string_value_count(_S2), int)


def test_ndjson_string_value_count_all_three():
    results = [
        ndjson_string_value_count(_S1),
        ndjson_string_value_count(_S2),
        ndjson_string_value_count(_S3),
    ]
    assert results == [2, 0, 0]


# --- ndjson_has_uniform_types ---

def test_ndjson_has_uniform_types_s1_true():
    # Both records are dicts
    assert ndjson_has_uniform_types(_S1) is True


def test_ndjson_has_uniform_types_s2_true():
    # Both records are dicts
    assert ndjson_has_uniform_types(_S2) is True


def test_ndjson_has_uniform_types_s3_false():
    # str and int — mixed types
    assert ndjson_has_uniform_types(_S3) is False


def test_ndjson_has_uniform_types_returns_bool_s1():
    assert isinstance(ndjson_has_uniform_types(_S1), bool)


def test_ndjson_has_uniform_types_returns_bool_s3():
    assert isinstance(ndjson_has_uniform_types(_S3), bool)


def test_ndjson_has_uniform_types_all_three():
    results = [
        ndjson_has_uniform_types(_S1),
        ndjson_has_uniform_types(_S2),
        ndjson_has_uniform_types(_S3),
    ]
    assert results == [True, True, False]
