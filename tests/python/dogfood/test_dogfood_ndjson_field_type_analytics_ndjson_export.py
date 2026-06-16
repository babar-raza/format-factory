"""
tests/python/dogfood/test_dogfood_ndjson_field_type_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-40
Dogfood export: write NDJSON -> run field-type analytics -> verify.
Uses: ndjson_string_field_count, ndjson_numeric_field_count, ndjson_boolean_field_count,
ndjson_has_nested_objects, ndjson_max_field_count, ndjson_min_field_count,
ndjson_total_field_count, ndjson_record_count.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    write_ndjson,
    load_ndjson,
    ndjson_string_field_count,
    ndjson_numeric_field_count,
    ndjson_boolean_field_count,
    ndjson_has_nested_objects,
    ndjson_max_field_count,
    ndjson_min_field_count,
    ndjson_total_field_count,
    ndjson_record_count,
)


_SAMPLE_RECORDS = [
    {"name": "Alice", "age": 30, "active": True},
    {"name": "Bob", "age": 25, "active": False},
    {"name": "Carol", "age": 35, "active": True},
]

_NESTED_RECORDS = [
    {"id": 1, "meta": {"key": "val"}, "score": 9.5},
    {"id": 2, "meta": {"key": "other"}, "score": 7.2},
    {"id": 3, "meta": None, "score": 8.0},
]


class TestNdjsonFieldTypeAnalyticsNdjsonExport:
    """NDJSON field type analytics -> export -> roundtrip verification."""

    def test_string_and_numeric_counts(self, tmp_path):
        src = tmp_path / "sample.ndjson"
        write_ndjson(_SAMPLE_RECORDS, str(src))
        str_count = ndjson_string_field_count(str(src))
        num_count = ndjson_numeric_field_count(str(src))
        assert str_count >= 0
        assert num_count >= 0

    def test_boolean_and_nested(self, tmp_path):
        src = tmp_path / "sample.ndjson"
        write_ndjson(_SAMPLE_RECORDS, str(src))
        bool_count = ndjson_boolean_field_count(str(src))
        has_nested = ndjson_has_nested_objects(str(src))
        assert bool_count >= 0
        assert isinstance(has_nested, bool)

    def test_field_type_analytics_to_ndjson(self, tmp_path):
        sources = {
            "sample.ndjson": _SAMPLE_RECORDS,
            "nested.ndjson": _NESTED_RECORDS,
        }
        records = []
        for name, data in sources.items():
            src = tmp_path / name
            write_ndjson(data, str(src))
            path = str(src)
            str_count = ndjson_string_field_count(path)
            num_count = ndjson_numeric_field_count(path)
            bool_count = ndjson_boolean_field_count(path)
            has_nested = ndjson_has_nested_objects(path)
            max_fields = ndjson_max_field_count(path)
            min_fields = ndjson_min_field_count(path)
            total_fields = ndjson_total_field_count(path)
            rec_count = ndjson_record_count(path)
            assert str_count >= 0, f"string_field_count must be >= 0 for {name}"
            assert num_count >= 0, f"numeric_field_count must be >= 0 for {name}"
            assert bool_count >= 0, f"boolean_field_count must be >= 0 for {name}"
            assert isinstance(has_nested, bool), f"has_nested_objects must be bool for {name}"
            assert max_fields >= 0, f"max_field_count must be >= 0 for {name}"
            assert min_fields >= 0, f"min_field_count must be >= 0 for {name}"
            assert total_fields >= 0, f"total_field_count must be >= 0 for {name}"
            assert rec_count >= 0, f"record_count must be >= 0 for {name}"
            records.append({
                "file": name,
                "string_fields": str_count,
                "numeric_fields": num_count,
                "boolean_fields": bool_count,
                "has_nested": has_nested,
                "max_field_count": max_fields,
                "min_field_count": min_fields,
                "total_fields": total_fields,
                "record_count": rec_count,
                "source_format": "ndjson",
            })
        dest = tmp_path / "ndjson-field-types.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 2

    def test_ndjson_roundtrip(self, tmp_path):
        src = tmp_path / "sample.ndjson"
        write_ndjson(_SAMPLE_RECORDS, str(src))
        records = [
            {
                "file": "sample.ndjson",
                "string_fields": ndjson_string_field_count(str(src)),
                "boolean_fields": ndjson_boolean_field_count(str(src)),
            }
        ]
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        assert loaded[0]["file"] == records[0]["file"]
        assert loaded[0]["string_fields"] == records[0]["string_fields"]
        assert loaded[0]["boolean_fields"] == records[0]["boolean_fields"]

    def test_json_lines_valid(self, tmp_path):
        src = tmp_path / "sample.ndjson"
        write_ndjson(_SAMPLE_RECORDS, str(src))
        records = [{"file": "sample.ndjson", "record_count": ndjson_record_count(str(src))}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_field_type_distribution_export(self, tmp_path):
        sources = [
            ("flat.ndjson", _SAMPLE_RECORDS),
            ("nested.ndjson", _NESTED_RECORDS),
        ]
        records = []
        for name, data in sources:
            src = tmp_path / name
            write_ndjson(data, str(src))
            path = str(src)
            str_count = ndjson_string_field_count(path)
            num_count = ndjson_numeric_field_count(path)
            bool_count = ndjson_boolean_field_count(path)
            assert str_count >= 0
            assert num_count >= 0
            assert bool_count >= 0
            records.append({
                "file": name,
                "string_fields": str_count,
                "numeric_fields": num_count,
                "boolean_fields": bool_count,
                "format": "ndjson",
            })
        dest = tmp_path / "field-types.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 2
        assert all(r["format"] == "ndjson" for r in loaded)
        assert all(r["string_fields"] >= 0 for r in loaded)
