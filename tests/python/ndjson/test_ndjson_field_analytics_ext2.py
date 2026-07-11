"""Tests for 6 new functions in ndjson_field_analytics (ext2 batch)."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson.ndjson_field_analytics import (
    ndjson_record_count,
    ndjson_dict_record_count,
    ndjson_unique_key_count,
    ndjson_min_field_count,
    ndjson_has_arrays,
    ndjson_total_field_count,
)

VALID = _REPO / "samples" / "by-format" / "ndjson" / "valid"
MINIMAL = VALID / "minimal.ndjson"

# minimal.ndjson has 3 records, each dict with keys: name, score, active


# --- ndjson_record_count ---

def test_record_count_minimal():
    assert ndjson_record_count(MINIMAL) == 3

def test_record_count_bytes():
    data = b'{"a": 1}\n{"b": 2}\n'
    assert ndjson_record_count(data) == 2

def test_record_count_empty():
    assert ndjson_record_count(b"") == 0


# --- ndjson_dict_record_count ---

def test_dict_record_count_minimal():
    assert ndjson_dict_record_count(MINIMAL) == 3

def test_dict_record_count_mixed():
    # bytes with non-dict records
    data = b'{"a": 1}\n42\n"hello"\n{"b": 2}\n'
    assert ndjson_dict_record_count(data) == 2

def test_dict_record_count_empty():
    assert ndjson_dict_record_count(b"") == 0


# --- ndjson_unique_key_count ---

def test_unique_key_count_minimal():
    # keys: name, score, active → 3 unique
    assert ndjson_unique_key_count(MINIMAL) == 3

def test_unique_key_count_bytes():
    data = b'{"a": 1, "b": 2}\n{"b": 3, "c": 4}\n'
    # keys: a, b, c → 3 unique
    assert ndjson_unique_key_count(data) == 3

def test_unique_key_count_empty():
    assert ndjson_unique_key_count(b"") == 0


# --- ndjson_min_field_count ---

def test_min_field_count_minimal():
    # all 3 records have 3 fields → min = 3
    assert ndjson_min_field_count(MINIMAL) == 3

def test_min_field_count_varied():
    data = b'{"a": 1}\n{"a": 2, "b": 3}\n'
    assert ndjson_min_field_count(data) == 1

def test_min_field_count_empty():
    assert ndjson_min_field_count(b"") == 0


# --- ndjson_has_arrays ---

def test_has_arrays_minimal():
    # minimal.ndjson has no list values
    assert ndjson_has_arrays(MINIMAL) is False

def test_has_arrays_with_list():
    data = b'{"tags": ["a", "b"]}\n'
    assert ndjson_has_arrays(data) is True

def test_has_arrays_without_list():
    data = b'{"name": "Alice", "score": 99}\n'
    assert ndjson_has_arrays(data) is False


# --- ndjson_total_field_count ---

def test_total_field_count_minimal():
    # 3 records × 3 fields = 9 total
    assert ndjson_total_field_count(MINIMAL) == 9

def test_total_field_count_varied():
    data = b'{"a": 1}\n{"a": 2, "b": 3}\n'
    assert ndjson_total_field_count(data) == 3

def test_total_field_count_empty():
    assert ndjson_total_field_count(b"") == 0
