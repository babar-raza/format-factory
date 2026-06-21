"""
Tests for Sprint r315: ndjson_max_record_key_count, ndjson_all_records_are_dicts.
Uses inline bytes — no sample files required.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import ndjson_max_record_key_count, ndjson_all_records_are_dicts

_S1 = b'{"name": "alice", "age": 30}\n{"name": "bob", "age": 25}\n'
_S2 = b'{"x": 1}\n{"y": 2}\n'
_S3 = b'"hello"\n42\n'


# --- ndjson_max_record_key_count ---

def test_ndjson_max_record_key_count_two_keys():
    assert ndjson_max_record_key_count(_S1) == 2


def test_ndjson_max_record_key_count_one_key():
    assert ndjson_max_record_key_count(_S2) == 1


def test_ndjson_max_record_key_count_no_dicts_zero():
    assert ndjson_max_record_key_count(_S3) == 0


def test_ndjson_max_record_key_count_returns_int_s1():
    assert isinstance(ndjson_max_record_key_count(_S1), int)


def test_ndjson_max_record_key_count_returns_int_s3():
    assert isinstance(ndjson_max_record_key_count(_S3), int)


def test_ndjson_max_record_key_count_all_three_distinct():
    results = [
        ndjson_max_record_key_count(_S1),
        ndjson_max_record_key_count(_S2),
        ndjson_max_record_key_count(_S3),
    ]
    assert results == [2, 1, 0]


# --- ndjson_all_records_are_dicts ---

def test_ndjson_all_records_are_dicts_s1_true():
    assert ndjson_all_records_are_dicts(_S1) is True


def test_ndjson_all_records_are_dicts_s2_true():
    assert ndjson_all_records_are_dicts(_S2) is True


def test_ndjson_all_records_are_dicts_s3_false():
    # "hello" and 42 are not dicts
    assert ndjson_all_records_are_dicts(_S3) is False


def test_ndjson_all_records_are_dicts_returns_bool_s1():
    assert isinstance(ndjson_all_records_are_dicts(_S1), bool)


def test_ndjson_all_records_are_dicts_returns_bool_s3():
    assert isinstance(ndjson_all_records_are_dicts(_S3), bool)


def test_ndjson_all_records_are_dicts_all_three():
    results = [
        ndjson_all_records_are_dicts(_S1),
        ndjson_all_records_are_dicts(_S2),
        ndjson_all_records_are_dicts(_S3),
    ]
    assert results == [True, True, False]
