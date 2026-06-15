"""
test_rnext20_ndjson_batch_min_fields.py

Sprint: FORMAT-FACTORY-CAPABILITY-REFRESH-AND-ADVANCE-RNEXT20-001
Gap IDs: GAP-NDJSON-FOSS-BATCH_UPDATE-001, GAP-NDJSON-FOSS-MIN_FIELD_COUNT-001

Tests for:
- batch_update(source, field, value): Set a field to a given value in every dict record.
- ndjson_min_field_count(source): Return the minimum number of fields in any dict record.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO_ROOT))

from src.python.ndjson.ndjson_codec import batch_update, ndjson_min_field_count


# ---------------------------------------------------------------------------
# batch_update
# ---------------------------------------------------------------------------


class TestBatchUpdate:

    def test_adds_new_field_to_all_records(self):
        records = [{"name": "Alice"}, {"name": "Bob"}, {"name": "Carol"}]
        result = batch_update(records, "active", True)
        assert all(r["active"] is True for r in result)

    def test_overwrites_existing_field_in_all_records(self):
        records = [{"name": "Alice", "score": 10}, {"name": "Bob", "score": 20}]
        result = batch_update(records, "score", 99)
        assert all(r["score"] == 99 for r in result)

    def test_non_dict_records_pass_through_unchanged(self):
        records = [{"a": 1}, "not-a-dict", 42, {"b": 2}]
        result = batch_update(records, "x", "val")
        assert result[1] == "not-a-dict"
        assert result[2] == 42
        assert result[0]["x"] == "val"
        assert result[3]["x"] == "val"

    def test_empty_input_returns_empty_list(self):
        result = batch_update([], "field", "value")
        assert result == []

    def test_single_record_is_updated(self):
        records = [{"id": 1}]
        result = batch_update(records, "status", "done")
        assert len(result) == 1
        assert result[0]["status"] == "done"
        assert result[0]["id"] == 1

    def test_does_not_mutate_original_list(self):
        records = [{"a": 1}, {"b": 2}]
        _ = batch_update(records, "new_key", 0)
        assert "new_key" not in records[0]
        assert "new_key" not in records[1]

    def test_can_set_field_to_none(self):
        records = [{"x": 5}]
        result = batch_update(records, "x", None)
        assert result[0]["x"] is None

    def test_can_set_field_to_zero(self):
        records = [{"val": 100}]
        result = batch_update(records, "val", 0)
        assert result[0]["val"] == 0

    def test_result_preserves_all_existing_fields(self):
        records = [{"a": 1, "b": 2, "c": 3}]
        result = batch_update(records, "d", 4)
        assert result[0]["a"] == 1
        assert result[0]["b"] == 2
        assert result[0]["c"] == 3
        assert result[0]["d"] == 4


# ---------------------------------------------------------------------------
# ndjson_min_field_count
# ---------------------------------------------------------------------------


class TestNdjsonMinFieldCount:

    def test_single_record_returns_its_field_count(self):
        records = [{"a": 1, "b": 2, "c": 3}]
        assert ndjson_min_field_count(records) == 3

    def test_returns_smallest_field_count_across_records(self):
        records = [{"a": 1, "b": 2, "c": 3}, {"a": 1, "b": 2}, {"a": 1}]
        assert ndjson_min_field_count(records) == 1

    def test_all_records_same_count(self):
        records = [{"x": 1, "y": 2}, {"x": 3, "y": 4}, {"x": 5, "y": 6}]
        assert ndjson_min_field_count(records) == 2

    def test_empty_list_returns_zero(self):
        assert ndjson_min_field_count([]) == 0

    def test_empty_dict_record_has_zero_fields(self):
        records = [{"a": 1, "b": 2}, {}]
        assert ndjson_min_field_count(records) == 0

    def test_accepts_file_path(self, tmp_path):
        records = [{"a": 1, "b": 2, "c": 3}, {"x": 9}]
        p = tmp_path / "test.ndjson"
        p.write_text("\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8")
        assert ndjson_min_field_count(str(p)) == 1

    def test_five_field_record_as_minimum(self):
        records = [
            {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6},
            {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5},
        ]
        assert ndjson_min_field_count(records) == 5
