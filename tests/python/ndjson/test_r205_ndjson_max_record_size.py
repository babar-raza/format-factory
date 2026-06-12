"""
Tests for ndjson_max_record_size — sprint product-deepening-rnext74.

Sprint: FORMAT-FACTORY-ABW-ZST-DEEPENING-001
"""
from __future__ import annotations

import sys
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src" / "python"))

from ndjson.ndjson_codec import ndjson_max_record_size


def test_import():
    assert callable(ndjson_max_record_size)


def test_empty_list_returns_zero():
    assert ndjson_max_record_size([]) == 0


def test_single_record_returns_json_length():
    records = [{"name": "alice", "age": 30}]
    expected = len(json.dumps(records[0]))
    assert ndjson_max_record_size(records) == expected


def test_two_records_returns_max():
    records = [{"name": "alice", "age": 30}, {"x": 1}]
    expected = max(len(json.dumps(r)) for r in records)
    assert ndjson_max_record_size(records) == expected


def test_returns_int():
    records = [{"k": "v"}]
    result = ndjson_max_record_size(records)
    assert isinstance(result, int)


def test_result_nonnegative():
    records = [{"a": 1}, {"b": 2, "c": 3}]
    assert ndjson_max_record_size(records) >= 0
