"""
tests/python/dogfood/test_dogfood_ndjson_utility_ops1_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-88
Dogfood export: NDJSON utility ops batch 1 -> write as NDJSON -> verify.
Uses: filter_records, get_field_names, export_to_csv, get_record_count,
      field_stats, pluck, min_value, max_value, head.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson import (
    filter_records,
    get_field_names,
    export_to_csv,
    get_record_count,
    field_stats,
    pluck,
    min_value,
    max_value,
    head,
    write_ndjson,
    load_ndjson,
)


def _make_ndjson_file(tmp_path, records, name="data.ndjson"):
    dest = tmp_path / name
    write_ndjson(records, str(dest))
    return str(dest)


_SAMPLE_DATA = [
    {"id": 1, "cat": "a", "val": 10.0, "tag": "x"},
    {"id": 2, "cat": "b", "val": 20.0, "tag": "y"},
    {"id": 3, "cat": "a", "val": 30.0, "tag": "z"},
    {"id": 4, "cat": "c", "val": 5.0,  "tag": "x"},
    {"id": 5, "cat": "b", "val": 15.0, "tag": "y"},
]


class TestNdjsonUtilityOps1NdjsonExport:
    """NDJSON utility ops batch 1 -> NDJSON export -> roundtrip verification."""

    def test_field_names_record_count_basics(self, tmp_path):
        src = _make_ndjson_file(tmp_path, _SAMPLE_DATA)
        names = get_field_names(src)
        count = get_record_count(src)
        assert isinstance(names, list) and len(names) > 0
        assert isinstance(count, int) and count == len(_SAMPLE_DATA)

    def test_filter_pluck_basics(self, tmp_path):
        src = _make_ndjson_file(tmp_path, _SAMPLE_DATA)
        filtered = filter_records(src, "cat", "a")
        assert isinstance(filtered, list)
        plucked = pluck(src, "val")
        assert isinstance(plucked, list) and len(plucked) == len(_SAMPLE_DATA)

    def test_utility_ops1_to_ndjson(self, tmp_path):
        src = _make_ndjson_file(tmp_path, _SAMPLE_DATA)
        names = get_field_names(src)
        count = get_record_count(src)
        filtered = filter_records(src, "cat", "a")
        plucked = pluck(src, "val")
        min_val = min_value(src, "val")
        max_val = max_value(src, "val")
        top = head(src, 3)
        csv_str = export_to_csv(src)
        assert isinstance(names, list), "get_field_names must return list"
        assert isinstance(count, int), "get_record_count must return int"
        assert isinstance(filtered, list), "filter_records must return list"
        assert len(filtered) == 2, "filter_records with cat=a should return 2 records"
        assert isinstance(plucked, list), "pluck must return list"
        assert min_val <= max_val, "min_value must be <= max_value"
        assert isinstance(top, list) and len(top) == 3, "head(3) must return 3 records"
        assert isinstance(csv_str, str), "export_to_csv must return str"
        records = [{
            "field_count": len(names),
            "record_count": count,
            "filtered_count": len(filtered),
            "plucked_count": len(plucked),
            "min_val": float(min_val),
            "max_val": float(max_val),
            "head_count": len(top),
            "csv_length": len(csv_str),
            "source_format": "ndjson",
        }]
        dest = tmp_path / "ndjson-utility-ops1.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0

    def test_ndjson_roundtrip(self, tmp_path):
        src = _make_ndjson_file(tmp_path, _SAMPLE_DATA)
        names = get_field_names(src)
        count = get_record_count(src)
        records = [{"field_count": len(names), "record_count": count}]
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == 1
        assert loaded[0]["field_count"] == len(names)
        assert loaded[0]["record_count"] == count

    def test_json_lines_valid(self, tmp_path):
        src = _make_ndjson_file(tmp_path, _SAMPLE_DATA)
        min_val = min_value(src, "val")
        max_val = max_value(src, "val")
        records = [{"min_val": float(min_val), "max_val": float(max_val)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_field_stats_export(self, tmp_path):
        src = _make_ndjson_file(tmp_path, _SAMPLE_DATA)
        stats = field_stats(src, "val")
        assert isinstance(stats, dict), "field_stats must return dict"
        plucked = pluck(src, "cat")
        assert isinstance(plucked, list) and len(plucked) == len(_SAMPLE_DATA)
        records = [{
            "field_stats_keys": len(stats),
            "pluck_count": len(plucked),
            "format": "ndjson",
        }]
        dest = tmp_path / "field-stats.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == 1
        assert loaded[0]["format"] == "ndjson"
        assert loaded[0]["field_stats_keys"] > 0
