"""Tests for NDJSON field analytics in ndjson_field_analytics.py."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_field_analytics import (
    ndjson_first_record_keys,
    ndjson_first_record_field_count,
    ndjson_has_consistent_keys,
    ndjson_bool_value_count,
    ndjson_null_field_count,
    ndjson_sorted_key_names,
)

SAMPLES = Path("samples/by-format/ndjson/valid")
MINIMAL = SAMPLES / "minimal.ndjson"
# minimal.ndjson:
#   {name: Alice, score: 95, active: true}
#   {name: Bob,   score: 82, active: false}
#   {name: Carol, score: 91, active: true}
# All records have identical keys; 2 True boolean values; 0 nulls


# --- ndjson_first_record_keys ---

def test_first_record_keys_minimal():
    assert ndjson_first_record_keys(MINIMAL) == ["name", "score", "active"]


def test_first_record_keys_count():
    assert len(ndjson_first_record_keys(MINIMAL)) == 3


def test_first_record_keys_contains_name():
    assert "name" in ndjson_first_record_keys(MINIMAL)


def test_first_record_keys_returns_list():
    assert isinstance(ndjson_first_record_keys(MINIMAL), list)


# --- ndjson_first_record_field_count ---

def test_first_record_field_count_minimal():
    assert ndjson_first_record_field_count(MINIMAL) == 3


def test_first_record_field_count_returns_int():
    assert isinstance(ndjson_first_record_field_count(MINIMAL), int)


# --- ndjson_has_consistent_keys ---

def test_has_consistent_keys_minimal():
    assert ndjson_has_consistent_keys(MINIMAL) is True


def test_has_consistent_keys_returns_bool():
    assert isinstance(ndjson_has_consistent_keys(MINIMAL), bool)


# --- ndjson_bool_value_count ---

def test_bool_value_count_minimal():
    # Alice(active=True) + Carol(active=True) = 2 True values
    assert ndjson_bool_value_count(MINIMAL) == 2


def test_bool_value_count_returns_int():
    assert isinstance(ndjson_bool_value_count(MINIMAL), int)


def test_bool_value_count_nonnegative():
    assert ndjson_bool_value_count(MINIMAL) >= 0


# --- ndjson_null_field_count ---

def test_null_field_count_minimal():
    assert ndjson_null_field_count(MINIMAL) == 0


def test_null_field_count_returns_int():
    assert isinstance(ndjson_null_field_count(MINIMAL), int)


# --- ndjson_sorted_key_names ---

def test_sorted_key_names_minimal():
    result = ndjson_sorted_key_names(MINIMAL)
    assert result == sorted(["name", "score", "active"])


def test_sorted_key_names_is_sorted():
    result = ndjson_sorted_key_names(MINIMAL)
    assert result == sorted(result)


def test_sorted_key_names_returns_list():
    assert isinstance(ndjson_sorted_key_names(MINIMAL), list)


def test_sorted_key_names_count():
    assert len(ndjson_sorted_key_names(MINIMAL)) == 3
