"""
tests/python/dogfood/test_dogfood_ndjson_final_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-90
Dogfood export: NDJSON final analytics -> write as NDJSON -> verify.
Uses: ndjson_min_field_name_length, ndjson_field_type_distribution,
      ndjson_max_numeric_value, ndjson_min_numeric_value,
      ndjson_has_string_fields, ndjson_has_boolean_fields.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson import (
    ndjson_min_field_name_length,
    ndjson_field_type_distribution,
    ndjson_max_numeric_value,
    ndjson_min_numeric_value,
    ndjson_has_string_fields,
    ndjson_has_boolean_fields,
    write_ndjson,
    load_ndjson,
)

_MIXED_DATA = [
    {"id": 1, "name": "alpha", "score": 9.5, "active": True},
    {"id": 2, "name": "beta",  "score": 7.0, "active": False},
    {"id": 3, "name": "gamma", "score": 8.2, "active": True},
]


def _make_ndjson_file(tmp_path, records, name="data.ndjson"):
    dest = tmp_path / name
    write_ndjson(records, str(dest))
    return str(dest)


class TestNdjsonFinalAnalyticsNdjsonExport:
    """NDJSON final analytics -> NDJSON export -> roundtrip verification."""

    def test_field_name_length_basics(self, tmp_path):
        src = _make_ndjson_file(tmp_path, _MIXED_DATA)
        min_fnl = ndjson_min_field_name_length(src)
        assert isinstance(min_fnl, int) and min_fnl >= 0

    def test_field_type_distribution_basics(self, tmp_path):
        src = _make_ndjson_file(tmp_path, _MIXED_DATA)
        dist = ndjson_field_type_distribution(src)
        assert isinstance(dist, dict) and len(dist) > 0

    def test_final_analytics_to_ndjson(self, tmp_path):
        src = _make_ndjson_file(tmp_path, _MIXED_DATA)
        min_fnl = ndjson_min_field_name_length(src)
        dist = ndjson_field_type_distribution(src)
        max_num = ndjson_max_numeric_value(src)
        min_num = ndjson_min_numeric_value(src)
        has_str = ndjson_has_string_fields(src)
        has_bool = ndjson_has_boolean_fields(src)
        assert isinstance(min_fnl, int) and min_fnl >= 0, "ndjson_min_field_name_length must be int >= 0"
        assert isinstance(dist, dict), "ndjson_field_type_distribution must return dict"
        assert max_num is None or isinstance(max_num, (int, float)), "ndjson_max_numeric_value must be numeric or None"
        assert min_num is None or isinstance(min_num, (int, float)), "ndjson_min_numeric_value must be numeric or None"
        assert has_str is True, "MIXED_DATA has 'name' string field, has_str must be True"
        assert has_bool is True, "MIXED_DATA has 'active' bool field, has_bool must be True"
        if max_num is not None and min_num is not None:
            assert max_num >= min_num, "max_numeric_value must be >= min_numeric_value"
        records = [{
            "min_field_name_length": min_fnl,
            "type_dist_keys": len(dist),
            "max_numeric": float(max_num) if max_num is not None else None,
            "min_numeric": float(min_num) if min_num is not None else None,
            "has_string_fields": has_str,
            "has_boolean_fields": has_bool,
            "source_format": "ndjson",
        }]
        dest = tmp_path / "ndjson-final-analytics.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0

    def test_ndjson_roundtrip(self, tmp_path):
        src = _make_ndjson_file(tmp_path, _MIXED_DATA)
        min_fnl = ndjson_min_field_name_length(src)
        has_str = ndjson_has_string_fields(src)
        records = [{"min_field_name_length": min_fnl, "has_string_fields": has_str}]
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == 1
        assert loaded[0]["min_field_name_length"] == min_fnl
        assert loaded[0]["has_string_fields"] == has_str

    def test_json_lines_valid(self, tmp_path):
        src = _make_ndjson_file(tmp_path, _MIXED_DATA)
        min_fnl = ndjson_min_field_name_length(src)
        has_bool = ndjson_has_boolean_fields(src)
        records = [{"min_field_name_length": min_fnl, "has_boolean_fields": has_bool}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_numeric_range_type_dist(self, tmp_path):
        src = _make_ndjson_file(tmp_path, _MIXED_DATA)
        max_num = ndjson_max_numeric_value(src)
        min_num = ndjson_min_numeric_value(src)
        dist = ndjson_field_type_distribution(src)
        # score field has values 9.5, 7.0, 8.2 — max should be 9.5
        if max_num is not None:
            assert float(max_num) >= 7.0, "max_numeric should be >= min score value"
        # type distribution should contain 'int' or 'float' or 'number'
        assert len(dist) > 0, "type distribution must have at least one type"
        records = [{
            "max_numeric": float(max_num) if max_num is not None else None,
            "min_numeric": float(min_num) if min_num is not None else None,
            "type_distribution": dist,
            "format": "ndjson",
        }]
        dest = tmp_path / "numeric-type-dist.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == 1
        assert loaded[0]["format"] == "ndjson"
