"""Tests for NDJSON record stats extension (second batch)."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_record_stats import (
    ndjson_has_boolean_values,
    ndjson_string_field_names,
    ndjson_max_record_field_count,
    ndjson_min_record_field_count,
    ndjson_all_records_have_same_keys,
    ndjson_total_value_count,
)

SAMPLES = Path("samples/by-format/ndjson/valid")
MINIMAL = SAMPLES / "minimal.ndjson"
# minimal.ndjson: 3 records, each with {name:str, score:int, active:bool}


# --- ndjson_has_boolean_values ---

def test_has_boolean_values_minimal():
    # active is bool
    assert ndjson_has_boolean_values(MINIMAL) is True


def test_has_boolean_values_list_no_bool():
    records = [{"x": 1, "y": "hello"}]
    assert ndjson_has_boolean_values(records) is False


def test_has_boolean_values_list_with_bool():
    records = [{"flag": True}]
    assert ndjson_has_boolean_values(records) is True


def test_has_boolean_values_returns_bool():
    assert isinstance(ndjson_has_boolean_values(MINIMAL), bool)


# --- ndjson_string_field_names ---

def test_string_field_names_minimal():
    # 'name' is string in all records; 'score' is int; 'active' is bool
    assert ndjson_string_field_names(MINIMAL) == ["name"]


def test_string_field_names_returns_list():
    assert isinstance(ndjson_string_field_names(MINIMAL), list)


def test_string_field_names_empty_records():
    records: list = []
    assert ndjson_string_field_names(records) == []


# --- ndjson_max_record_field_count ---

def test_max_record_field_count_minimal():
    # each record has 3 fields
    assert ndjson_max_record_field_count(MINIMAL) == 3


def test_max_record_field_count_mixed():
    records = [{"a": 1, "b": 2}, {"a": 1}]
    assert ndjson_max_record_field_count(records) == 2


def test_max_record_field_count_returns_int():
    assert isinstance(ndjson_max_record_field_count(MINIMAL), int)


def test_max_record_field_count_positive():
    assert ndjson_max_record_field_count(MINIMAL) > 0


# --- ndjson_min_record_field_count ---

def test_min_record_field_count_minimal():
    # each record has 3 fields
    assert ndjson_min_record_field_count(MINIMAL) == 3


def test_min_record_field_count_mixed():
    records = [{"a": 1, "b": 2}, {"a": 1}]
    assert ndjson_min_record_field_count(records) == 1


def test_min_record_field_count_returns_int():
    assert isinstance(ndjson_min_record_field_count(MINIMAL), int)


# --- ndjson_all_records_have_same_keys ---

def test_all_records_same_keys_minimal():
    # all records have {name, score, active}
    assert ndjson_all_records_have_same_keys(MINIMAL) is True


def test_all_records_same_keys_different():
    records = [{"a": 1, "b": 2}, {"a": 1, "c": 3}]
    assert ndjson_all_records_have_same_keys(records) is False


def test_all_records_same_keys_single():
    records = [{"a": 1}]
    assert ndjson_all_records_have_same_keys(records) is True


def test_all_records_same_keys_returns_bool():
    assert isinstance(ndjson_all_records_have_same_keys(MINIMAL), bool)


# --- ndjson_total_value_count ---

def test_total_value_count_minimal():
    # 3 records * 3 fields each = 9
    assert ndjson_total_value_count(MINIMAL) == 9


def test_total_value_count_list():
    records = [{"a": 1, "b": 2}, {"c": 3}]
    assert ndjson_total_value_count(records) == 3


def test_total_value_count_returns_int():
    assert isinstance(ndjson_total_value_count(MINIMAL), int)


def test_total_value_count_positive():
    assert ndjson_total_value_count(MINIMAL) > 0
