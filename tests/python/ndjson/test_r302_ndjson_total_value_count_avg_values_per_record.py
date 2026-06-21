"""Tests for ndjson_total_value_count and ndjson_avg_values_per_record (Sprint 92, R302)."""
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import ndjson_total_value_count, ndjson_avg_values_per_record


ONE_FIELD = '{"a": 1}'
TWO_FIELDS = '{"a": 1, "b": 2}'
THREE_TOTAL = '{"a": 1, "b": 2}\n{"c": 3}'


def test_total_value_count_one_field():
    assert ndjson_total_value_count(ONE_FIELD) == 1


def test_total_value_count_two_fields():
    assert ndjson_total_value_count(TWO_FIELDS) == 2


def test_total_value_count_three_total():
    assert ndjson_total_value_count(THREE_TOTAL) == 3


def test_total_value_count_returns_int():
    assert isinstance(ndjson_total_value_count(ONE_FIELD), int)


def test_total_value_count_nonnegative():
    assert ndjson_total_value_count(ONE_FIELD) >= 0


def test_avg_values_per_record_one_field():
    assert abs(ndjson_avg_values_per_record(ONE_FIELD) - 1.0) < 0.01


def test_avg_values_per_record_two_fields():
    assert abs(ndjson_avg_values_per_record(TWO_FIELDS) - 2.0) < 0.01


def test_avg_values_per_record_mixed():
    assert abs(ndjson_avg_values_per_record(THREE_TOTAL) - 1.5) < 0.01


def test_avg_values_per_record_returns_float():
    assert isinstance(ndjson_avg_values_per_record(ONE_FIELD), float)


def test_avg_values_per_record_positive_for_nonempty():
    assert ndjson_avg_values_per_record(TWO_FIELDS) > 0.0
