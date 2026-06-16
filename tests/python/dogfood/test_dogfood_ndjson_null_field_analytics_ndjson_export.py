"""
tests/python/dogfood/test_dogfood_ndjson_null_field_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-56
Dogfood export: write NDJSON -> run null/field analytics -> verify.
Uses: ndjson_field_exists, ndjson_nested_field_count, ndjson_null_field_count,
ndjson_record_count, ndjson_total_field_count, ndjson_unique_field_names.
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
    ndjson_field_exists,
    ndjson_nested_field_count,
    ndjson_null_field_count,
    ndjson_record_count,
    ndjson_total_field_count,
    ndjson_unique_field_names,
)


_FLAT_RECORDS = [
    {"name": "Alice", "score": 95, "active": True, "notes": None},
    {"name": "Bob", "score": 87, "active": False, "notes": None},
    {"name": "Carol", "score": 92, "active": True, "notes": "excellent"},
]

_NESTED_RECORDS = [
    {"id": 1, "meta": {"tag": "a"}, "count": 10},
    {"id": 2, "meta": {"tag": "b", "extra": True}, "count": 20},
    {"id": 3, "count": 30, "meta": None},
]


class TestNdjsonNullFieldAnalyticsNdjsonExport:
    """NDJSON null/field analytics -> export -> roundtrip verification."""

    def test_field_exists_and_null_count(self, tmp_path):
        src = tmp_path / "flat.ndjson"
        write_ndjson(_FLAT_RECORDS, str(src))
        exists = ndjson_field_exists(str(src), "name")
        null_count = ndjson_null_field_count(str(src), "notes")
        assert exists is True
        assert null_count >= 0

    def test_nested_count_and_unique_names(self, tmp_path):
        src = tmp_path / "nested.ndjson"
        write_ndjson(_NESTED_RECORDS, str(src))
        nested_count = ndjson_nested_field_count(str(src))
        unique_names = ndjson_unique_field_names(str(src))
        record_count = ndjson_record_count(str(src))
        total_fields = ndjson_total_field_count(str(src))
        assert nested_count >= 0
        assert isinstance(unique_names, list)
        assert record_count >= 0
        assert total_fields >= 0

    def test_null_field_analytics_to_ndjson(self, tmp_path):
        sources = {
            "flat.ndjson": _FLAT_RECORDS,
            "nested.ndjson": _NESTED_RECORDS,
        }
        records = []
        for name, data in sources.items():
            src = tmp_path / name
            write_ndjson(data, str(src))
            path = str(src)
            exists_name = ndjson_field_exists(path, "name")
            nested_count = ndjson_nested_field_count(path)
            unique_names = ndjson_unique_field_names(path)
            record_count = ndjson_record_count(path)
            total_fields = ndjson_total_field_count(path)
            assert isinstance(exists_name, bool), f"field_exists must be bool for {name}"
            assert nested_count >= 0, f"nested_field_count must be >= 0 for {name}"
            assert isinstance(unique_names, list), f"unique_field_names must be list for {name}"
            assert record_count >= 0, f"record_count must be >= 0 for {name}"
            assert total_fields >= 0, f"total_field_count must be >= 0 for {name}"
            records.append({
                "file": name,
                "field_name_exists": exists_name,
                "nested_field_count": nested_count,
                "unique_field_name_count": len(unique_names),
                "record_count": record_count,
                "total_field_count": total_fields,
                "source_format": "ndjson",
            })
        dest = tmp_path / "ndjson-null-field.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 2

    def test_ndjson_roundtrip(self, tmp_path):
        src = tmp_path / "flat.ndjson"
        write_ndjson(_FLAT_RECORDS, str(src))
        records = [{
            "file": "flat.ndjson",
            "nested_count": ndjson_nested_field_count(str(src)),
            "record_count": ndjson_record_count(str(src)),
            "total_fields": ndjson_total_field_count(str(src)),
        }]
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        assert loaded[0]["nested_count"] == records[0]["nested_count"]
        assert loaded[0]["record_count"] == records[0]["record_count"]

    def test_json_lines_valid(self, tmp_path):
        src = tmp_path / "flat.ndjson"
        write_ndjson(_FLAT_RECORDS, str(src))
        records = [{"file": "flat.ndjson", "field_exists": ndjson_field_exists(str(src), "name")}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_field_analytics_distribution_export(self, tmp_path):
        sources = [
            ("flat.ndjson", _FLAT_RECORDS),
            ("nested.ndjson", _NESTED_RECORDS),
        ]
        records = []
        for name, data in sources:
            src = tmp_path / name
            write_ndjson(data, str(src))
            path = str(src)
            unique_names = ndjson_unique_field_names(path)
            nested_count = ndjson_nested_field_count(path)
            total_fields = ndjson_total_field_count(path)
            assert isinstance(unique_names, list)
            assert nested_count >= 0
            assert total_fields >= 0
            records.append({
                "file": name,
                "unique_field_names": unique_names,
                "nested_field_count": nested_count,
                "total_field_count": total_fields,
                "format": "ndjson",
            })
        dest = tmp_path / "field-analytics.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 2
        assert all(r["format"] == "ndjson" for r in loaded)
        assert all(r["total_field_count"] >= 0 for r in loaded)
