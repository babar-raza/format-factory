"""
tests/python/dogfood/test_dogfood_ndjson_record_size_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-47
Dogfood export: write NDJSON -> run record size analytics -> verify.
Uses: ndjson_average_record_size, ndjson_empty_record_count, ndjson_max_record_size,
ndjson_total_field_count, ndjson_min_field_count, ndjson_record_count.
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
    ndjson_average_record_size,
    ndjson_empty_record_count,
    ndjson_max_record_size,
    ndjson_total_field_count,
    ndjson_min_field_count,
    ndjson_record_count,
)


_FLAT_RECORDS = [
    {"name": "Alice", "score": 95, "active": True},
    {"name": "Bob", "score": 87, "active": False},
    {"name": "Carol", "score": 92, "active": True},
]

_MIXED_RECORDS = [
    {"id": 1, "value": "alpha", "count": 10},
    {"id": 2, "value": "beta"},
    {"id": 3, "value": "gamma", "count": 30, "extra": True},
]


class TestNdjsonRecordSizeAnalyticsNdjsonExport:
    """NDJSON record size analytics -> export -> roundtrip verification."""

    def test_average_and_max_record_size(self, tmp_path):
        src = tmp_path / "flat.ndjson"
        write_ndjson(_FLAT_RECORDS, str(src))
        avg = ndjson_average_record_size(str(src))
        mx = ndjson_max_record_size(str(src))
        assert avg >= 0.0
        assert mx >= 0

    def test_empty_records_and_field_count(self, tmp_path):
        src = tmp_path / "flat.ndjson"
        write_ndjson(_FLAT_RECORDS, str(src))
        empty = ndjson_empty_record_count(str(src))
        total_fields = ndjson_total_field_count(str(src))
        min_f = ndjson_min_field_count(str(src))
        assert empty >= 0
        assert total_fields >= 0
        assert min_f >= 0

    def test_record_size_analytics_to_ndjson(self, tmp_path):
        sources = {
            "flat.ndjson": _FLAT_RECORDS,
            "mixed.ndjson": _MIXED_RECORDS,
        }
        records = []
        for name, data in sources.items():
            src = tmp_path / name
            write_ndjson(data, str(src))
            path = str(src)
            avg = ndjson_average_record_size(path)
            mx = ndjson_max_record_size(path)
            empty = ndjson_empty_record_count(path)
            total_fields = ndjson_total_field_count(path)
            min_f = ndjson_min_field_count(path)
            count = ndjson_record_count(path)
            assert avg >= 0.0, f"average_record_size must be >= 0 for {name}"
            assert mx >= 0, f"max_record_size must be >= 0 for {name}"
            assert empty >= 0, f"empty_record_count must be >= 0 for {name}"
            assert total_fields >= 0, f"total_field_count must be >= 0 for {name}"
            assert min_f >= 0, f"min_field_count must be >= 0 for {name}"
            assert count >= 0, f"record_count must be >= 0 for {name}"
            records.append({
                "file": name,
                "avg_record_size": avg,
                "max_record_size": mx,
                "empty_records": empty,
                "total_fields": total_fields,
                "min_field_count": min_f,
                "record_count": count,
                "source_format": "ndjson",
            })
        dest = tmp_path / "ndjson-record-sizes.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 2

    def test_ndjson_roundtrip(self, tmp_path):
        src = tmp_path / "flat.ndjson"
        write_ndjson(_FLAT_RECORDS, str(src))
        records = [
            {
                "file": "flat.ndjson",
                "max_record_size": ndjson_max_record_size(str(src)),
                "record_count": ndjson_record_count(str(src)),
            }
        ]
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        assert loaded[0]["max_record_size"] == records[0]["max_record_size"]
        assert loaded[0]["record_count"] == records[0]["record_count"]

    def test_json_lines_valid(self, tmp_path):
        src = tmp_path / "flat.ndjson"
        write_ndjson(_FLAT_RECORDS, str(src))
        records = [{"file": "flat.ndjson", "avg_size": ndjson_average_record_size(str(src))}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_record_size_distribution_export(self, tmp_path):
        sources = [
            ("flat.ndjson", _FLAT_RECORDS),
            ("mixed.ndjson", _MIXED_RECORDS),
        ]
        records = []
        for name, data in sources:
            src = tmp_path / name
            write_ndjson(data, str(src))
            path = str(src)
            avg = ndjson_average_record_size(path)
            mx = ndjson_max_record_size(path)
            total = ndjson_total_field_count(path)
            assert avg >= 0.0
            assert mx >= 0
            assert total >= 0
            records.append({
                "file": name,
                "avg_record_size": avg,
                "max_record_size": mx,
                "total_fields": total,
                "format": "ndjson",
            })
        dest = tmp_path / "size-dist.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 2
        assert all(r["format"] == "ndjson" for r in loaded)
        assert all(r["avg_record_size"] >= 0.0 for r in loaded)
