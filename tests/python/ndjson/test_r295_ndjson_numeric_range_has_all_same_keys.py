"""Tests for ndjson_numeric_range and ndjson_has_all_same_keys (Sprint 85, R295)."""
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson.ndjson_codec import ndjson_numeric_range, ndjson_has_all_same_keys

SAME_KEYS = '{"a": 1, "b": 2}\n{"a": 3, "b": 4}'
DIFF_KEYS = '{"x": 10}\n{"y": 20}'
SINGLE = '{"v": 5}'
EMPTY = ''


def test_numeric_range_same_keys():
    assert abs(ndjson_numeric_range(SAME_KEYS) - 3.0) < 0.001


def test_numeric_range_diff_keys():
    assert abs(ndjson_numeric_range(DIFF_KEYS) - 10.0) < 0.001


def test_numeric_range_single_record():
    assert abs(ndjson_numeric_range(SINGLE) - 0.0) < 0.001


def test_numeric_range_returns_float():
    assert isinstance(ndjson_numeric_range(SAME_KEYS), float)


def test_has_all_same_keys_same_true():
    assert ndjson_has_all_same_keys(SAME_KEYS) is True


def test_has_all_same_keys_diff_false():
    assert ndjson_has_all_same_keys(DIFF_KEYS) is False


def test_has_all_same_keys_single_true():
    assert ndjson_has_all_same_keys(SINGLE) is True


def test_has_all_same_keys_returns_bool():
    assert isinstance(ndjson_has_all_same_keys(SAME_KEYS), bool)


def test_numeric_range_nonnegative():
    assert ndjson_numeric_range(SAME_KEYS) >= 0.0


def test_has_all_same_keys_extra_field_false():
    src = '{"a": 1}\n{"a": 2, "b": 3}'
    assert ndjson_has_all_same_keys(src) is False
