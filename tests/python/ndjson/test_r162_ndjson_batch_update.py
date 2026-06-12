"""
test_r162_ndjson_batch_update.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT22-001
Added: 2026-06-12

Tests for NDJSON batch_update function.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import batch_update


class TestBatchUpdate:
    def test_sets_field_in_all_records(self):
        records = [{"a": 1}, {"a": 2}, {"a": 3}]
        result = batch_update(records, "a", 99)
        assert all(r["a"] == 99 for r in result)

    def test_adds_new_field(self):
        records = [{"x": 1}, {"x": 2}]
        result = batch_update(records, "new", "hello")
        assert all(r.get("new") == "hello" for r in result)

    def test_non_dict_records_pass_through(self):
        records = [{"a": 1}, "string", 42, None]
        result = batch_update(records, "a", 0)
        assert result[0]["a"] == 0
        assert result[1] == "string"
        assert result[2] == 42
        assert result[3] is None

    def test_returns_new_list(self):
        records = [{"a": 1}]
        result = batch_update(records, "a", 2)
        assert result is not records
        assert records[0]["a"] == 1  # original unchanged

    def test_empty_records(self):
        result = batch_update([], "field", "value")
        assert result == []

    def test_string_source(self):
        src = '{"k": 1}\n{"k": 2}\n'
        result = batch_update(src, "k", 0)
        assert len(result) == 2
        assert all(r["k"] == 0 for r in result)
