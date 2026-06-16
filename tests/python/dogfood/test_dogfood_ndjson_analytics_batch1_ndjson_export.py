"""
tests/python/dogfood/test_dogfood_ndjson_analytics_batch1_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-89
Dogfood export: NDJSON analytics batch 1 -> write as NDJSON -> verify.
Uses: ndjson_average_field_count, ndjson_min_field_count, ndjson_max_record_size,
      ndjson_total_field_count, ndjson_nested_field_count, ndjson_has_nested_objects.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson import (
    ndjson_average_field_count,
    ndjson_min_field_count,
    ndjson_max_record_size,
    ndjson_total_field_count,
    ndjson_nested_field_count,
    ndjson_has_nested_objects,
    write_ndjson,
    load_ndjson,
)

_FLAT_DATA = [
    {"id": 1, "name": "alpha", "score": 9.5},
    {"id": 2, "name": "beta",  "score": 7.0},
    {"id": 3, "name": "gamma", "score": 8.2},
]
_NESTED_DATA = [
    {"id": 1, "meta": {"type": "a"}, "val": 10},
    {"id": 2, "meta": {"type": "b"}, "val": 20},
    {"id": 3, "inner": {"x": 1, "y": 2}, "val": 30},
]


def _make_ndjson_file(tmp_path, records, name):
    dest = tmp_path / name
    write_ndjson(records, str(dest))
    return str(dest)


class TestNdjsonAnalyticsBatch1NdjsonExport:
    """NDJSON analytics batch 1 -> NDJSON export -> roundtrip verification."""

    def test_field_count_analytics_basics(self, tmp_path):
        src = _make_ndjson_file(tmp_path, _FLAT_DATA, "flat.ndjson")
        avg_fc = ndjson_average_field_count(src)
        min_fc = ndjson_min_field_count(src)
        total_fc = ndjson_total_field_count(src)
        assert isinstance(avg_fc, float) and avg_fc >= 0.0
        assert isinstance(min_fc, int) and min_fc >= 0
        assert isinstance(total_fc, int) and total_fc >= 0

    def test_nested_analytics_basics(self, tmp_path):
        src = _make_ndjson_file(tmp_path, _NESTED_DATA, "nested.ndjson")
        nested_count = ndjson_nested_field_count(src)
        has_nested = ndjson_has_nested_objects(src)
        assert isinstance(nested_count, int) and nested_count >= 0
        assert has_nested is True, "NESTED_DATA has nested objects, has_nested must be True"

    def test_analytics_batch1_to_ndjson(self, tmp_path):
        flat_src = _make_ndjson_file(tmp_path, _FLAT_DATA, "flat.ndjson")
        nested_src = _make_ndjson_file(tmp_path, _NESTED_DATA, "nested.ndjson")
        records = []
        for src, label in [(flat_src, "flat"), (nested_src, "nested")]:
            avg_fc = ndjson_average_field_count(src)
            min_fc = ndjson_min_field_count(src)
            max_rs = ndjson_max_record_size(src)
            total_fc = ndjson_total_field_count(src)
            nested_count = ndjson_nested_field_count(src)
            has_nested = ndjson_has_nested_objects(src)
            assert isinstance(avg_fc, float), f"ndjson_average_field_count must be float for {label}"
            assert isinstance(min_fc, int), f"ndjson_min_field_count must be int for {label}"
            assert isinstance(max_rs, int) and max_rs >= 0, f"ndjson_max_record_size must be int >= 0 for {label}"
            assert isinstance(total_fc, int), f"ndjson_total_field_count must be int for {label}"
            assert isinstance(nested_count, int), f"ndjson_nested_field_count must be int for {label}"
            assert isinstance(has_nested, bool), f"ndjson_has_nested_objects must be bool for {label}"
            records.append({
                "label": label,
                "average_field_count": avg_fc,
                "min_field_count": min_fc,
                "max_record_size": max_rs,
                "total_field_count": total_fc,
                "nested_field_count": nested_count,
                "has_nested_objects": has_nested,
                "source_format": "ndjson",
            })
        dest = tmp_path / "ndjson-analytics-batch1.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) == 2

    def test_ndjson_roundtrip(self, tmp_path):
        src = _make_ndjson_file(tmp_path, _FLAT_DATA, "flat.ndjson")
        avg_fc = ndjson_average_field_count(src)
        min_fc = ndjson_min_field_count(src)
        records = [{"average_field_count": avg_fc, "min_field_count": min_fc}]
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == 1
        assert loaded[0]["min_field_count"] == min_fc

    def test_json_lines_valid(self, tmp_path):
        src = _make_ndjson_file(tmp_path, _FLAT_DATA, "flat.ndjson")
        avg_fc = ndjson_average_field_count(src)
        total_fc = ndjson_total_field_count(src)
        records = [{"average_field_count": avg_fc, "total_field_count": total_fc}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_nested_vs_flat_comparison(self, tmp_path):
        flat_src = _make_ndjson_file(tmp_path, _FLAT_DATA, "flat.ndjson")
        nested_src = _make_ndjson_file(tmp_path, _NESTED_DATA, "nested.ndjson")
        flat_nested = ndjson_has_nested_objects(flat_src)
        nested_nested = ndjson_has_nested_objects(nested_src)
        assert flat_nested is False, "flat data must have no nested objects"
        assert nested_nested is True, "nested data must have nested objects"
        flat_nc = ndjson_nested_field_count(flat_src)
        nested_nc = ndjson_nested_field_count(nested_src)
        assert flat_nc == 0, "flat data must have 0 nested fields"
        assert nested_nc > 0, "nested data must have > 0 nested fields"
        records = [
            {"label": "flat", "nested_count": flat_nc, "has_nested": flat_nested},
            {"label": "nested", "nested_count": nested_nc, "has_nested": nested_nested},
        ]
        dest = tmp_path / "comparison.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == 2
        assert all(isinstance(r["nested_count"], int) for r in loaded)
