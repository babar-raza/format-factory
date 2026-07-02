"""
tests/python/ndjson/test_r200_ndjson_advanced_ops.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-SPRINT3-001
TASK-017: NDJSON advanced operations dogfood — analytics, transformation, pipeline.

Covers: count_records, get_field_names, head, tail, pluck, filter_records, sort_by,
group_by, pick, omit, rename_field, sum_field, average_value, min_value, max_value,
distinct_values, count_by, field_stats, zip_with_index, to_markdown_table,
aggregate, merge_ndjson, validate_schema, ndjson_record_count, ndjson_field_exists,
to_jsonl_str, roundtrip, write_ndjson + ZST dogfood pipeline.
"""
from __future__ import annotations

import sys
import os
import json
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

import ndjson
from ndjson import (
    load_ndjson, write_ndjson, probe_ndjson, get_record_count,
    count_records, get_field_names, head, tail, pluck,
    filter_records, sort_by, group_by, pick, omit, rename_field,
    sum_field, average_value, min_value, max_value,
    distinct_values, count_by, field_stats,
    zip_with_index, to_markdown_table, aggregate, merge_ndjson,
    validate_schema, ndjson_record_count, ndjson_field_exists,
    to_jsonl_str, roundtrip,
    ndjson_average_field_count, ndjson_max_field_count, ndjson_min_field_count,
    ndjson_max_record_size, ndjson_null_field_count,
)
import pytest

try:
    import zstandard as _zstandard  # noqa: F401
    from zst import compress_bytes, decompress_bytes, validate_roundtrip
    _HAS_ZST = True
except Exception:
    _HAS_ZST = False

_RECORDS = [
    {"name": "Alice", "age": 30, "dept": "engineering"},
    {"name": "Bob", "age": 25, "dept": "design"},
    {"name": "Carol", "age": 35, "dept": "engineering"},
]


def _make_ndjson_file(records=None):
    """Create a temp NDJSON file from records list."""
    records = records or _RECORDS
    fd, path = tempfile.mkstemp(suffix=".ndjson")
    with os.fdopen(fd, "w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    return path


class TestNdjsonProbeAndLoad:
    """Load and probe functions."""

    def test_load_ndjson_returns_list(self):
        path = _make_ndjson_file()
        try:
            result = load_ndjson(path)
            assert isinstance(result, list)
            assert len(result) == 3
        finally:
            os.unlink(path)

    def test_probe_ndjson_returns_truthy(self):
        path = _make_ndjson_file()
        try:
            result = probe_ndjson(path)
            assert result is not None
        finally:
            os.unlink(path)

    def test_get_record_count_positive(self):
        path = _make_ndjson_file()
        try:
            n = get_record_count(path)
            assert isinstance(n, int)
            assert n == 3
        finally:
            os.unlink(path)

    def test_count_records_matches_load(self):
        path = _make_ndjson_file()
        try:
            assert count_records(path) == len(load_ndjson(path))
        finally:
            os.unlink(path)

    def test_ndjson_record_count_positive(self):
        path = _make_ndjson_file()
        try:
            n = ndjson_record_count(path)
            assert isinstance(n, int)
            assert n == 3
        finally:
            os.unlink(path)

    def test_ndjson_field_exists_true(self):
        path = _make_ndjson_file()
        try:
            result = ndjson_field_exists(path, "name")
            assert result is True
        finally:
            os.unlink(path)

    def test_ndjson_field_exists_false_missing(self):
        path = _make_ndjson_file()
        try:
            result = ndjson_field_exists(path, "nonexistent_xyz")
            assert result is False
        finally:
            os.unlink(path)


class TestNdjsonFieldAnalytics:
    """Field-level analytics."""

    def test_get_field_names_returns_list(self):
        path = _make_ndjson_file()
        try:
            fields = get_field_names(path)
            assert isinstance(fields, list)
            assert "name" in fields
            assert "age" in fields
        finally:
            os.unlink(path)

    def test_sum_field_correct(self):
        path = _make_ndjson_file()
        try:
            total = sum_field(path, "age")
            assert total == 90.0
        finally:
            os.unlink(path)

    def test_average_value_correct(self):
        path = _make_ndjson_file()
        try:
            avg = average_value(path, "age")
            assert avg == 30.0
        finally:
            os.unlink(path)

    def test_min_value_correct(self):
        path = _make_ndjson_file()
        try:
            assert min_value(path, "age") == 25
        finally:
            os.unlink(path)

    def test_max_value_correct(self):
        path = _make_ndjson_file()
        try:
            assert max_value(path, "age") == 35
        finally:
            os.unlink(path)

    def test_distinct_values_returns_list(self):
        path = _make_ndjson_file()
        try:
            vals = distinct_values(path, "dept")
            assert isinstance(vals, list)
            assert "engineering" in vals
        finally:
            os.unlink(path)

    def test_count_by_returns_dict(self):
        path = _make_ndjson_file()
        try:
            result = count_by(path, "dept")
            assert isinstance(result, dict)
            assert result.get("engineering", 0) == 2
        finally:
            os.unlink(path)

    def test_field_stats_complete(self):
        path = _make_ndjson_file()
        try:
            stats = field_stats(path, "age")
            assert isinstance(stats, dict)
            assert stats["count"] == 3
            assert stats["sum"] == 90.0
        finally:
            os.unlink(path)

    def test_aggregate_sum(self):
        path = _make_ndjson_file()
        try:
            result = aggregate(path, "age", "sum")
            assert result == 90.0
        finally:
            os.unlink(path)


class TestNdjsonSliceAndProject:
    """Head, tail, pluck, pick, omit operations."""

    def test_head_returns_first(self):
        path = _make_ndjson_file()
        try:
            result = head(path, 1)
            assert len(result) == 1
            assert result[0]["name"] == "Alice"
        finally:
            os.unlink(path)

    def test_tail_returns_last(self):
        path = _make_ndjson_file()
        try:
            result = tail(path, 1)
            assert len(result) == 1
            assert result[0]["name"] == "Carol"
        finally:
            os.unlink(path)

    def test_pluck_returns_field_values(self):
        path = _make_ndjson_file()
        try:
            result = pluck(path, "name")
            assert isinstance(result, list)
            assert "Alice" in result
        finally:
            os.unlink(path)

    def test_pick_projects_fields(self):
        path = _make_ndjson_file()
        try:
            result = pick(path, ["name"])
            assert all("name" in r for r in result)
            assert all("age" not in r for r in result)
        finally:
            os.unlink(path)

    def test_omit_excludes_fields(self):
        path = _make_ndjson_file()
        try:
            result = omit(path, ["age"])
            assert all("age" not in r for r in result)
            assert all("name" in r for r in result)
        finally:
            os.unlink(path)


class TestNdjsonTransformation:
    """Sort, filter, group, rename, zip, merge."""

    def test_filter_records_by_value(self):
        path = _make_ndjson_file()
        try:
            result = filter_records(path, "dept", "engineering")
            assert len(result) == 2
        finally:
            os.unlink(path)

    def test_sort_by_field(self):
        path = _make_ndjson_file()
        try:
            result = sort_by(path, "age")
            assert result[0]["age"] <= result[-1]["age"]
        finally:
            os.unlink(path)

    def test_group_by_field(self):
        path = _make_ndjson_file()
        try:
            result = group_by(path, "dept")
            assert isinstance(result, dict)
            assert "engineering" in result
        finally:
            os.unlink(path)

    def test_rename_field_changes_name(self):
        path = _make_ndjson_file()
        try:
            result = rename_field(path, "name", "full_name")
            assert all("full_name" in r for r in result)
            assert all("name" not in r for r in result)
        finally:
            os.unlink(path)

    def test_zip_with_index_adds_index(self):
        path = _make_ndjson_file()
        try:
            result = zip_with_index(path)
            assert all("_index" in r for r in result)
            assert result[0]["_index"] == 0
        finally:
            os.unlink(path)

    def test_merge_ndjson_combines_records(self):
        path_a = _make_ndjson_file([{"x": 1}])
        path_b = _make_ndjson_file([{"y": 2}])
        try:
            result = merge_ndjson(path_a, path_b)
            assert len(result) == 2
        finally:
            os.unlink(path_a)
            os.unlink(path_b)

    def test_to_markdown_table_contains_headers(self):
        path = _make_ndjson_file()
        try:
            md = to_markdown_table(path)
            assert isinstance(md, str)
            assert "name" in md
            assert "age" in md
        finally:
            os.unlink(path)

    def test_to_jsonl_str_produces_lines(self):
        records = [{"a": 1}, {"b": 2}]
        result = to_jsonl_str(records)
        assert isinstance(result, str)
        lines = [l for l in result.strip().split("\n") if l]
        assert len(lines) == 2


class TestNdjsonStats:
    """NDJSON field count and size stats."""

    def test_ndjson_average_field_count_positive(self):
        path = _make_ndjson_file()
        try:
            n = ndjson_average_field_count(path)
            assert isinstance(n, (int, float))
            assert n == 3.0
        finally:
            os.unlink(path)

    def test_ndjson_max_field_count_positive(self):
        path = _make_ndjson_file()
        try:
            n = ndjson_max_field_count(path)
            assert isinstance(n, int)
            assert n == 3
        finally:
            os.unlink(path)

    def test_ndjson_min_field_count_positive(self):
        path = _make_ndjson_file()
        try:
            n = ndjson_min_field_count(path)
            assert isinstance(n, int)
            assert n == 3
        finally:
            os.unlink(path)

    def test_ndjson_max_record_size_positive(self):
        path = _make_ndjson_file()
        try:
            n = ndjson_max_record_size(path)
            assert isinstance(n, int)
            assert n > 0
        finally:
            os.unlink(path)

    def test_ndjson_null_field_count_zero(self):
        path = _make_ndjson_file()
        try:
            n = ndjson_null_field_count(path, "age")
            assert isinstance(n, int)
            assert n == 0
        finally:
            os.unlink(path)


class TestNdjsonValidateAndRoundtrip:
    """Schema validation and roundtrip."""

    def test_validate_schema_returns_dict(self):
        path = _make_ndjson_file()
        try:
            schema = {"name": str, "age": int}
            result = validate_schema(path, schema)
            assert isinstance(result, dict)
        finally:
            os.unlink(path)

    def test_roundtrip_produces_file(self):
        src = _make_ndjson_file()
        fd, dst = tempfile.mkstemp(suffix=".ndjson")
        os.close(fd)
        try:
            roundtrip(src, dst)
            assert os.path.getsize(dst) > 0
        finally:
            os.unlink(src)
            os.unlink(dst)

    def test_write_ndjson_produces_file(self):
        path = _make_ndjson_file()
        records = load_ndjson(path)
        fd, out = tempfile.mkstemp(suffix=".ndjson")
        os.close(fd)
        try:
            write_ndjson(records, out)
            assert os.path.getsize(out) > 0
        finally:
            os.unlink(path)
            os.unlink(out)


@pytest.mark.skipif(not _HAS_ZST, reason="python-zstandard not installed")
class TestNdjsonZstDogfoodPipeline:
    """NDJSON→ZST dogfood pipeline proof."""

    def test_ndjson_to_zst_compress_roundtrip(self):
        path = _make_ndjson_file()
        try:
            records = load_ndjson(path)
            jsonl = to_jsonl_str(records).encode("utf-8")
            compressed = compress_bytes(jsonl)
            assert len(compressed) > 0
            recovered = decompress_bytes(compressed)
            assert recovered == jsonl
        finally:
            os.unlink(path)

    def test_ndjson_zst_validate_roundtrip(self):
        path = _make_ndjson_file()
        try:
            records = load_ndjson(path)
            jsonl = to_jsonl_str(records).encode("utf-8")
            result = validate_roundtrip(jsonl)
            assert result["valid"] is True
            assert result["match"] is True
        finally:
            os.unlink(path)

    def test_ndjson_pipeline_preserves_records(self):
        """Full pipeline: load → JSONL → ZST compress → decompress → parse → verify."""
        path = _make_ndjson_file()
        try:
            original = load_ndjson(path)
            jsonl_bytes = to_jsonl_str(original).encode("utf-8")
            compressed = compress_bytes(jsonl_bytes)
            recovered_bytes = decompress_bytes(compressed)
            recovered_lines = [l for l in recovered_bytes.decode("utf-8").strip().split("\n") if l]
            recovered_records = [json.loads(line) for line in recovered_lines]
            assert len(recovered_records) == len(original)
            assert recovered_records[0]["name"] == original[0]["name"]
        finally:
            os.unlink(path)
