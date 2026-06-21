"""
Sprint 41 — 5 new NDJSON analytics functions.
Tests: ndjson_nonempty_record_count, ndjson_nonempty_record_ratio,
       ndjson_max_field_count, ndjson_min_field_count,
       ndjson_total_field_count
"""
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson import (
    ndjson_nonempty_record_count,
    ndjson_nonempty_record_ratio,
    ndjson_max_field_count,
    ndjson_min_field_count,
    ndjson_total_field_count,
)


def _ndjson(*records) -> bytes:
    return b"\n".join(json.dumps(r).encode() for r in records)


_SRC2 = _ndjson({"a": 1, "b": 2}, {"c": 3})
_SRC1 = _ndjson({"x": "hello"})
_SRC_EMPTY = b""
_SRC_MIXED = _ndjson({"a": 1}, {}, {"b": 2, "c": 3})


# --- ndjson_nonempty_record_count ---

def test_nonempty_record_count_two_records():
    assert ndjson_nonempty_record_count(_SRC2) == 2


def test_nonempty_record_count_single():
    assert ndjson_nonempty_record_count(_SRC1) == 1


def test_nonempty_record_count_empty_src():
    assert ndjson_nonempty_record_count(_SRC_EMPTY) == 0


def test_nonempty_record_count_mixed_excludes_empty():
    assert ndjson_nonempty_record_count(_SRC_MIXED) == 2


def test_nonempty_record_count_is_int():
    assert isinstance(ndjson_nonempty_record_count(_SRC2), int)


# --- ndjson_nonempty_record_ratio ---

def test_nonempty_record_ratio_all_nonempty():
    assert ndjson_nonempty_record_ratio(_SRC2) == 1.0


def test_nonempty_record_ratio_empty_src():
    assert ndjson_nonempty_record_ratio(_SRC_EMPTY) == 0.0


def test_nonempty_record_ratio_mixed():
    result = ndjson_nonempty_record_ratio(_SRC_MIXED)
    assert 0.0 < result < 1.0


def test_nonempty_record_ratio_is_float():
    assert isinstance(ndjson_nonempty_record_ratio(_SRC2), float)


# --- ndjson_max_field_count ---

def test_max_field_count_two_records():
    assert ndjson_max_field_count(_SRC2) == 2


def test_max_field_count_single():
    assert ndjson_max_field_count(_SRC1) == 1


def test_max_field_count_empty():
    assert ndjson_max_field_count(_SRC_EMPTY) == 0


def test_max_field_count_mixed():
    assert ndjson_max_field_count(_SRC_MIXED) == 2


def test_max_field_count_is_int():
    assert isinstance(ndjson_max_field_count(_SRC2), int)


# --- ndjson_min_field_count ---

def test_min_field_count_two_records():
    assert ndjson_min_field_count(_SRC2) == 1


def test_min_field_count_single():
    assert ndjson_min_field_count(_SRC1) == 1


def test_min_field_count_empty():
    assert ndjson_min_field_count(_SRC_EMPTY) == 0


def test_min_field_count_mixed():
    assert ndjson_min_field_count(_SRC_MIXED) == 0


def test_min_field_count_is_int():
    assert isinstance(ndjson_min_field_count(_SRC2), int)


# --- ndjson_total_field_count ---

def test_total_field_count_two_records():
    assert ndjson_total_field_count(_SRC2) == 3


def test_total_field_count_single():
    assert ndjson_total_field_count(_SRC1) == 1


def test_total_field_count_empty():
    assert ndjson_total_field_count(_SRC_EMPTY) == 0


def test_total_field_count_mixed():
    assert ndjson_total_field_count(_SRC_MIXED) == 3


def test_total_field_count_is_int():
    assert isinstance(ndjson_total_field_count(_SRC2), int)
