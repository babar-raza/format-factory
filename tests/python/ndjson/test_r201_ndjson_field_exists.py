"""
Tests for ndjson_field_exists — sprint product-deepening-rnext70.

Sprint: FORMAT-FACTORY-ABW-ZST-DEEPENING-001
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src" / "python"))

from ndjson.ndjson_codec import ndjson_field_exists


def test_import():
    assert callable(ndjson_field_exists)


def test_field_present_returns_true():
    records = [{"name": "alice", "age": 30}]
    assert ndjson_field_exists(records, "name") is True


def test_field_absent_returns_false():
    records = [{"x": 1, "y": 2}]
    assert ndjson_field_exists(records, "name") is False


def test_empty_list_returns_false():
    assert ndjson_field_exists([], "name") is False


def test_returns_bool():
    records = [{"key": "value"}]
    result = ndjson_field_exists(records, "key")
    assert isinstance(result, bool)


def test_partial_records_have_field():
    records = [{"x": 1}, {"name": "bob"}, {"z": 3}]
    assert ndjson_field_exists(records, "name") is True
