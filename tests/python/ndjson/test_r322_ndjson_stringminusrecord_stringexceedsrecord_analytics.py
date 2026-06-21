"""
r322 NDJSON analytics: ndjson_string_value_count_minus_record_count,
ndjson_string_value_count_exceeds_record_count.
Uses inline bytes — no sample files required.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    ndjson_string_value_count_minus_record_count,
    ndjson_string_value_count_exceeds_record_count,
)

# S1: 1 record, 0 strings
_S1 = b'{"a":1}\n'
# S2: 1 record, 2 strings
_S2 = b'{"a":"x","b":"y"}\n'
# S3: 2 records, 4 strings
_S3 = b'{"p":"a","q":"b","r":"c"}\n{"s":"d"}\n'


# --- ndjson_string_value_count_minus_record_count ---

def test_string_minus_record_s1_zero():
    assert ndjson_string_value_count_minus_record_count(_S1) == 0

def test_string_minus_record_s2_one():
    assert ndjson_string_value_count_minus_record_count(_S2) == 1

def test_string_minus_record_s3_two():
    assert ndjson_string_value_count_minus_record_count(_S3) == 2

def test_string_minus_record_returns_int():
    result = ndjson_string_value_count_minus_record_count(_S1)
    assert isinstance(result, int)

def test_string_minus_record_nonnegative():
    for s in [_S1, _S2, _S3]:
        assert ndjson_string_value_count_minus_record_count(s) >= 0

def test_string_minus_record_all_distinct():
    results = [
        ndjson_string_value_count_minus_record_count(_S1),
        ndjson_string_value_count_minus_record_count(_S2),
        ndjson_string_value_count_minus_record_count(_S3),
    ]
    assert len(set(results)) == 3


# --- ndjson_string_value_count_exceeds_record_count ---

def test_string_exceeds_record_s1_false():
    assert ndjson_string_value_count_exceeds_record_count(_S1) is False

def test_string_exceeds_record_s2_true():
    assert ndjson_string_value_count_exceeds_record_count(_S2) is True

def test_string_exceeds_record_s3_true():
    assert ndjson_string_value_count_exceeds_record_count(_S3) is True

def test_string_exceeds_record_returns_bool():
    result = ndjson_string_value_count_exceeds_record_count(_S1)
    assert isinstance(result, bool)

def test_string_exceeds_record_s2_is_bool():
    result = ndjson_string_value_count_exceeds_record_count(_S2)
    assert isinstance(result, bool)

def test_string_exceeds_record_only_s1_false():
    results = [
        ndjson_string_value_count_exceeds_record_count(_S1),
        ndjson_string_value_count_exceeds_record_count(_S2),
        ndjson_string_value_count_exceeds_record_count(_S3),
    ]
    assert results.count(False) == 1
