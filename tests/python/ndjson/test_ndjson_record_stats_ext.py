"""Tests for extended NDJSON record statistics functions."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_record_stats import (
    ndjson_record_count,
    ndjson_dict_record_count,
    ndjson_common_keys,
    ndjson_unique_key_count,
    ndjson_has_null_values,
    ndjson_numeric_field_count,
)

SAMPLE = Path("samples/by-format/ndjson/valid/minimal.ndjson")

# --- ndjson_record_count ---

def test_record_count_file():
    assert ndjson_record_count(SAMPLE) == 3


def test_record_count_list():
    assert ndjson_record_count([{"a": 1}, {"b": 2}]) == 2


def test_record_count_empty():
    assert ndjson_record_count([]) == 0


def test_record_count_single():
    assert ndjson_record_count([{"x": 1}]) == 1


# --- ndjson_dict_record_count ---

def test_dict_record_count_file():
    assert ndjson_dict_record_count(SAMPLE) == 3


def test_dict_record_count_mixed():
    assert ndjson_dict_record_count([{"a": 1}, [1, 2], {"b": 2}]) == 2


def test_dict_record_count_no_dicts():
    assert ndjson_dict_record_count([[1, 2], "scalar"]) == 0


def test_dict_record_count_empty():
    assert ndjson_dict_record_count([]) == 0


# --- ndjson_common_keys ---

def test_common_keys_file():
    assert ndjson_common_keys(SAMPLE) == ["active", "name", "score"]


def test_common_keys_partial_overlap():
    records = [{"a": 1, "b": 2}, {"a": 3, "c": 4}]
    assert ndjson_common_keys(records) == ["a"]


def test_common_keys_no_overlap():
    records = [{"a": 1}, {"b": 2}]
    assert ndjson_common_keys(records) == []


def test_common_keys_empty():
    assert ndjson_common_keys([]) == []


def test_common_keys_no_dicts():
    assert ndjson_common_keys([[1, 2], [3, 4]]) == []


# --- ndjson_unique_key_count ---

def test_unique_key_count_file():
    assert ndjson_unique_key_count(SAMPLE) == 3


def test_unique_key_count_overlap():
    records = [{"a": 1, "b": 2}, {"b": 3, "c": 4}]
    assert ndjson_unique_key_count(records) == 3


def test_unique_key_count_empty():
    assert ndjson_unique_key_count([]) == 0


def test_unique_key_count_no_dicts():
    assert ndjson_unique_key_count([[1, 2]]) == 0


# --- ndjson_has_null_values ---

def test_has_null_values_false_from_file():
    assert ndjson_has_null_values(SAMPLE) is False


def test_has_null_values_true():
    assert ndjson_has_null_values([{"a": None}]) is True


def test_has_null_values_false_nonempty():
    assert ndjson_has_null_values([{"a": 1, "b": "x"}]) is False


def test_has_null_values_empty():
    assert ndjson_has_null_values([]) is False


def test_has_null_values_null_among_many():
    records = [{"a": 1}, {"b": None}, {"c": 3}]
    assert ndjson_has_null_values(records) is True


# --- ndjson_numeric_field_count ---

def test_numeric_field_count_file():
    # Only "score" is numeric (active=bool excluded, name=str excluded)
    assert ndjson_numeric_field_count(SAMPLE) == 1


def test_numeric_field_count_multiple():
    records = [{"x": 1.0, "y": 2, "z": "text"}]
    assert ndjson_numeric_field_count(records) == 2


def test_numeric_field_count_bools_excluded():
    records = [{"flag": True, "val": 42}]
    assert ndjson_numeric_field_count(records) == 1


def test_numeric_field_count_no_numeric():
    records = [{"a": "str", "b": None}]
    assert ndjson_numeric_field_count(records) == 0


def test_numeric_field_count_empty():
    assert ndjson_numeric_field_count([]) == 0
