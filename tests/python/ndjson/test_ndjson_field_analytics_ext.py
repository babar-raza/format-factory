"""Tests for ndjson_field_analytics extension functions."""
from __future__ import annotations

from pathlib import Path

from ndjson.ndjson_field_analytics import (
    ndjson_all_key_names,
    ndjson_last_record_keys,
    ndjson_has_nested_records,
)

SAMPLES = Path("samples/by-format/ndjson/valid")
MINIMAL = SAMPLES / "minimal.ndjson"


# --- ndjson_all_key_names ---

def test_all_key_names_returns_list():
    result = ndjson_all_key_names(MINIMAL)
    assert isinstance(result, list)


def test_all_key_names_nonempty():
    result = ndjson_all_key_names(MINIMAL)
    assert len(result) > 0


def test_all_key_names_contains_expected():
    result = ndjson_all_key_names(MINIMAL)
    assert "name" in result


# --- ndjson_last_record_keys ---

def test_last_record_keys_returns_list():
    result = ndjson_last_record_keys(MINIMAL)
    assert isinstance(result, list)


def test_last_record_keys_nonempty():
    result = ndjson_last_record_keys(MINIMAL)
    assert len(result) > 0


def test_last_record_keys_subset_of_all_keys():
    all_keys = set(ndjson_all_key_names(MINIMAL))
    last_keys = set(ndjson_last_record_keys(MINIMAL))
    assert last_keys.issubset(all_keys)


# --- ndjson_has_nested_records ---

def test_has_nested_records_returns_bool():
    result = ndjson_has_nested_records(MINIMAL)
    assert isinstance(result, bool)


def test_has_nested_records_minimal_false():
    # minimal.ndjson has flat records
    result = ndjson_has_nested_records(MINIMAL)
    assert result is False
