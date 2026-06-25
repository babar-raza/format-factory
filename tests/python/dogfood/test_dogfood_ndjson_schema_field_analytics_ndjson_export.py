"""
tests/python/dogfood/test_dogfood_ndjson_schema_field_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-71
Dogfood export: NDJSON parse -> schema/field analytics -> write as NDJSON -> verify.
Uses: probe_ndjson, get_field_names, get_record_count, field_stats,
filter_records, ndjson_record_count.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson import (
    probe_ndjson,
    get_field_names,
    get_record_count,
    field_stats,
    filter_records,
    ndjson_record_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


def _make_ndjson_file(tmp_dir: Path, name: str, records: list) -> str:
    path = tmp_dir / name
    write_ndjson(records, str(path))
    return str(path)


class TestNdjsonSchemaFieldAnalyticsNdjsonExport:
    """NDJSON schema/field analytics -> NDJSON export -> roundtrip verification."""

    def test_probe_and_field_names(self, tmp_path):
        src = _make_ndjson_file(tmp_path, "src.ndjson", [
            {"name": "Alice", "age": 30, "score": 95.5},
            {"name": "Bob", "age": 25, "score": 88.0},
            {"name": "Carol", "age": 35, "score": 92.3},
        ])
        valid = probe_ndjson(src)
        fields = get_field_names(src)
        assert isinstance(valid, bool)
        assert isinstance(fields, list)
        assert "name" in fields

    def test_record_count_and_stats(self, tmp_path):
        src = _make_ndjson_file(tmp_path, "src2.ndjson", [
            {"val": 10, "label": "x"},
            {"val": 20, "label": "y"},
            {"val": 30, "label": "z"},
        ])
        count = get_record_count(src)
        stats = field_stats(src, "val")
        assert count == 3
        assert isinstance(stats, dict)

    def test_schema_field_analytics_to_ndjson(self, tmp_path):
        sample_files = []
        for i in range(3):
            src = _make_ndjson_file(tmp_path, f"sample{i}.ndjson", [
                {"id": j, "value": j * 10.0, "tag": f"t{j}"} for j in range(5)
            ])
            sample_files.append(src)

        records = []
        for path in sample_files:
            valid = probe_ndjson(path)
            fields = get_field_names(path)
            count = get_record_count(path)
            stats = field_stats(path, "value")
            filtered = filter_records(path, "tag", "t0")
            ndjson_count = ndjson_record_count(path)
            assert isinstance(valid, bool), "probe_ndjson must be bool"
            assert isinstance(fields, list), "get_field_names must be list"
            assert count >= 0, "get_record_count must be >= 0"
            assert isinstance(stats, dict), "field_stats must be dict"
            assert isinstance(filtered, list), "filter_records must be list"
            assert ndjson_count >= 0, "ndjson_record_count must be >= 0"
            records.append({
                "file": Path(path).name,
                "is_valid": valid,
                "field_count": len(fields),
                "record_count": count,
                "filtered_count": len(filtered),
                "ndjson_record_count": ndjson_count,
                "source_format": "ndjson",
            })
        dest = tmp_path / "ndjson-schema-field.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for i in range(3):
            src = _make_ndjson_file(tmp_path, f"rt{i}.ndjson", [
                {"x": k, "y": k * 2} for k in range(4)
            ])
            fields = get_field_names(src)
            count = get_record_count(src)
            records.append({
                "file": Path(src).name,
                "field_count": len(fields),
                "record_count": count,
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["field_count"] == back["field_count"]
            assert orig["record_count"] == back["record_count"]

    def test_json_lines_valid(self, tmp_path):
        src = _make_ndjson_file(tmp_path, "jl.ndjson", [{"a": 1}, {"a": 2}])
        valid = probe_ndjson(src)
        count = get_record_count(src)
        records = [{"file": "jl.ndjson", "is_valid": valid, "record_count": count}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_field_filter_export(self, tmp_path):
        records = []
        for i in range(3):
            src = _make_ndjson_file(tmp_path, f"ff{i}.ndjson", [
                {"category": "A", "amount": j * 5} for j in range(4)
            ] + [{"category": "B", "amount": j * 3} for j in range(3)])
            fields = get_field_names(src)
            filtered_a = filter_records(src, "category", "A")
            stats = field_stats(src, "amount")
            assert isinstance(fields, list)
            assert isinstance(filtered_a, list)
            assert isinstance(stats, dict)
            records.append({
                "file": Path(src).name,
                "field_count": len(fields),
                "filtered_a_count": len(filtered_a),
                "format": "ndjson",
            })
        dest = tmp_path / "field-filter.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "ndjson" for r in loaded)
        assert all(r["filtered_a_count"] >= 0 for r in loaded)
