"""
tests/python/dogfood/test_dogfood_gnumeric_final_ndjson_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-88
Dogfood export: Gnumeric final analytics + NDJSON analytics -> write as NDJSON -> verify.
Uses: gnumeric_min_row_count, gnumeric_has_empty_sheets,
      ndjson_max_field_count, ndjson_null_field_count, ndjson_record_count,
      ndjson_field_exists, ndjson_unique_field_names, ndjson_boolean_field_count.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric import gnumeric_min_row_count, gnumeric_has_empty_sheets
from ndjson import (
    ndjson_max_field_count,
    ndjson_null_field_count,
    ndjson_record_count,
    ndjson_field_exists,
    ndjson_unique_field_names,
    ndjson_boolean_field_count,
    write_ndjson,
    load_ndjson,
)


_GNU_DIR = _REPO / "samples" / "by-format" / "gnumeric"


def _ap(f):
    return os.path.abspath(str(f))


def _valid_gnumeric_files():
    return sorted(_GNU_DIR.glob("*.gnumeric"))


def _make_ndjson_file(tmp_path, records, name="data.ndjson"):
    dest = tmp_path / name
    write_ndjson(records, str(dest))
    return str(dest)


_SAMPLE_DATA = [
    {"id": 1, "name": "alpha", "active": True, "score": 9.5},
    {"id": 2, "name": "beta",  "active": False, "score": 7.0},
    {"id": 3, "name": "gamma", "active": True,  "score": 8.2},
]


class TestGnumericFinalNdjsonAnalyticsNdjsonExport:
    """Gnumeric final + NDJSON analytics -> NDJSON export -> roundtrip verification."""

    def test_gnumeric_final_basics(self):
        sample = _valid_gnumeric_files()[0]
        path = _ap(sample)
        min_rows = gnumeric_min_row_count(path)
        has_empty = gnumeric_has_empty_sheets(path)
        assert isinstance(min_rows, int) and min_rows >= 0
        assert isinstance(has_empty, bool)

    def test_ndjson_analytics_basics(self, tmp_path):
        src = _make_ndjson_file(tmp_path, _SAMPLE_DATA)
        max_fc = ndjson_max_field_count(src)
        rc = ndjson_record_count(src)
        exists = ndjson_field_exists(src, "name")
        assert isinstance(max_fc, int) and max_fc >= 0
        assert isinstance(rc, int) and rc == len(_SAMPLE_DATA)
        assert exists is True

    def test_combined_to_ndjson(self, tmp_path):
        src = _make_ndjson_file(tmp_path, _SAMPLE_DATA)
        max_fc = ndjson_max_field_count(src)
        null_count = ndjson_null_field_count(src, "name")
        rc = ndjson_record_count(src)
        exists = ndjson_field_exists(src, "active")
        uniq_names = ndjson_unique_field_names(src)
        bool_count = ndjson_boolean_field_count(src)
        assert isinstance(max_fc, int), "ndjson_max_field_count must return int"
        assert isinstance(null_count, int) and null_count >= 0, "ndjson_null_field_count must be int >= 0"
        assert isinstance(rc, int), "ndjson_record_count must return int"
        assert exists is True, "ndjson_field_exists must return True for 'active'"
        assert isinstance(uniq_names, list) and len(uniq_names) > 0, "ndjson_unique_field_names must return non-empty list"
        assert isinstance(bool_count, int) and bool_count >= 0, "ndjson_boolean_field_count must be int >= 0"
        gnu_records = []
        for f in _valid_gnumeric_files():
            path = _ap(f)
            min_rows = gnumeric_min_row_count(path)
            has_empty = gnumeric_has_empty_sheets(path)
            gnu_records.append({
                "file": f.name,
                "min_row_count": min_rows,
                "has_empty_sheets": has_empty,
                "source_format": "gnumeric",
            })
        ndjson_records = [{
            "max_field_count": max_fc,
            "null_field_count": null_count,
            "record_count": rc,
            "field_exists_active": exists,
            "unique_field_names_count": len(uniq_names),
            "boolean_field_count": bool_count,
            "source_format": "ndjson",
        }]
        all_records = gnu_records + ndjson_records
        dest = tmp_path / "gnumeric-final-ndjson-analytics.ndjson"
        write_ndjson(all_records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(all_records) >= 4

    def test_ndjson_roundtrip(self, tmp_path):
        src = _make_ndjson_file(tmp_path, _SAMPLE_DATA)
        rc = ndjson_record_count(src)
        uniq_names = ndjson_unique_field_names(src)
        gnu_sample = _valid_gnumeric_files()[0]
        min_rows = gnumeric_min_row_count(_ap(gnu_sample))
        records = [
            {"type": "ndjson", "record_count": rc, "field_names": len(uniq_names)},
            {"type": "gnumeric", "min_row_count": min_rows},
        ]
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == 2
        assert loaded[0]["record_count"] == rc

    def test_json_lines_valid(self, tmp_path):
        src = _make_ndjson_file(tmp_path, _SAMPLE_DATA)
        rc = ndjson_record_count(src)
        exists = ndjson_field_exists(src, "id")
        records = [{"record_count": rc, "has_id": exists}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_gnumeric_ndjson_combined_export(self, tmp_path):
        src = _make_ndjson_file(tmp_path, _SAMPLE_DATA)
        bool_count = ndjson_boolean_field_count(src)
        assert bool_count >= 1, "SAMPLE_DATA has 'active' bool field, count must be >= 1"
        records = []
        for f in _valid_gnumeric_files():
            path = _ap(f)
            min_rows = gnumeric_min_row_count(path)
            has_empty = gnumeric_has_empty_sheets(path)
            assert min_rows >= 0
            assert isinstance(has_empty, bool)
            records.append({
                "file": f.name,
                "min_row_count": min_rows,
                "has_empty_sheets": has_empty,
                "ndjson_bool_fields": bool_count,
                "format": "gnumeric",
            })
        dest = tmp_path / "combined.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "gnumeric" for r in loaded)
        assert all(r["min_row_count"] >= 0 for r in loaded)
