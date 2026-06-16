"""
tests/python/dogfood/test_dogfood_ndjson_analytics_batch2_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-89
Dogfood export: NDJSON analytics batch 2 -> write as NDJSON -> verify.
Uses: ndjson_empty_record_count, ndjson_numeric_field_count, ndjson_average_record_size,
      ndjson_string_field_count, ndjson_all_records_nonempty, ndjson_max_field_name_length.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson import (
    ndjson_empty_record_count,
    ndjson_numeric_field_count,
    ndjson_average_record_size,
    ndjson_string_field_count,
    ndjson_all_records_nonempty,
    ndjson_max_field_name_length,
    write_ndjson,
    load_ndjson,
)

_MIXED_DATA = [
    {"id": 1, "name": "alpha", "score": 9.5, "active": True},
    {"id": 2, "name": "beta",  "score": 7.0, "active": False},
    {"id": 3, "name": "gamma", "score": 8.2, "active": True},
]
_WITH_EMPTY = [
    {"id": 1, "name": "alpha"},
    {},
    {"id": 3, "name": "gamma"},
]


def _make_ndjson_file(tmp_path, records, name):
    dest = tmp_path / name
    write_ndjson(records, str(dest))
    return str(dest)


class TestNdjsonAnalyticsBatch2NdjsonExport:
    """NDJSON analytics batch 2 -> NDJSON export -> roundtrip verification."""

    def test_field_type_counts_basics(self, tmp_path):
        src = _make_ndjson_file(tmp_path, _MIXED_DATA, "mixed.ndjson")
        num_fc = ndjson_numeric_field_count(src)
        str_fc = ndjson_string_field_count(src)
        assert isinstance(num_fc, int) and num_fc >= 0
        assert isinstance(str_fc, int) and str_fc >= 0

    def test_empty_record_analytics_basics(self, tmp_path):
        src_mixed = _make_ndjson_file(tmp_path, _MIXED_DATA, "mixed.ndjson")
        src_empty = _make_ndjson_file(tmp_path, _WITH_EMPTY, "withempty.ndjson")
        empty_mixed = ndjson_empty_record_count(src_mixed)
        empty_count = ndjson_empty_record_count(src_empty)
        all_nonempty_mixed = ndjson_all_records_nonempty(src_mixed)
        assert empty_mixed == 0, "MIXED_DATA has no empty records"
        assert empty_count >= 1, "WITH_EMPTY has 1 empty record"
        assert all_nonempty_mixed is True, "MIXED_DATA must be all nonempty"

    def test_analytics_batch2_to_ndjson(self, tmp_path):
        src = _make_ndjson_file(tmp_path, _MIXED_DATA, "mixed.ndjson")
        empty_rc = ndjson_empty_record_count(src)
        num_fc = ndjson_numeric_field_count(src)
        avg_rs = ndjson_average_record_size(src)
        str_fc = ndjson_string_field_count(src)
        all_nonempty = ndjson_all_records_nonempty(src)
        max_fn_len = ndjson_max_field_name_length(src)
        assert isinstance(empty_rc, int) and empty_rc >= 0, "ndjson_empty_record_count must be int >= 0"
        assert isinstance(num_fc, int) and num_fc >= 0, "ndjson_numeric_field_count must be int >= 0"
        assert isinstance(avg_rs, float) and avg_rs >= 0.0, "ndjson_average_record_size must be float >= 0"
        assert isinstance(str_fc, int) and str_fc >= 0, "ndjson_string_field_count must be int >= 0"
        assert isinstance(all_nonempty, bool), "ndjson_all_records_nonempty must be bool"
        assert isinstance(max_fn_len, int) and max_fn_len >= 0, "ndjson_max_field_name_length must be int >= 0"
        records = [{
            "empty_record_count": empty_rc,
            "numeric_field_count": num_fc,
            "average_record_size": avg_rs,
            "string_field_count": str_fc,
            "all_records_nonempty": all_nonempty,
            "max_field_name_length": max_fn_len,
            "source_format": "ndjson",
        }]
        dest = tmp_path / "ndjson-analytics-batch2.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0

    def test_ndjson_roundtrip(self, tmp_path):
        src = _make_ndjson_file(tmp_path, _MIXED_DATA, "mixed.ndjson")
        num_fc = ndjson_numeric_field_count(src)
        str_fc = ndjson_string_field_count(src)
        records = [{"numeric_field_count": num_fc, "string_field_count": str_fc}]
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == 1
        assert loaded[0]["numeric_field_count"] == num_fc
        assert loaded[0]["string_field_count"] == str_fc

    def test_json_lines_valid(self, tmp_path):
        src = _make_ndjson_file(tmp_path, _MIXED_DATA, "mixed.ndjson")
        avg_rs = ndjson_average_record_size(src)
        max_fn_len = ndjson_max_field_name_length(src)
        records = [{"average_record_size": avg_rs, "max_field_name_length": max_fn_len}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_empty_vs_nonempty_export(self, tmp_path):
        src_mixed = _make_ndjson_file(tmp_path, _MIXED_DATA, "mixed.ndjson")
        src_empty = _make_ndjson_file(tmp_path, _WITH_EMPTY, "withempty.ndjson")
        all_ne_mixed = ndjson_all_records_nonempty(src_mixed)
        all_ne_empty = ndjson_all_records_nonempty(src_empty)
        empty_count = ndjson_empty_record_count(src_empty)
        assert all_ne_mixed is True
        assert all_ne_empty is False
        assert empty_count == 1, "WITH_EMPTY has exactly 1 empty record"
        records = [
            {"label": "mixed", "all_nonempty": all_ne_mixed, "empty_count": 0},
            {"label": "with_empty", "all_nonempty": all_ne_empty, "empty_count": empty_count},
        ]
        dest = tmp_path / "empty-vs-nonempty.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == 2
        assert loaded[0]["all_nonempty"] is True
        assert loaded[1]["all_nonempty"] is False
