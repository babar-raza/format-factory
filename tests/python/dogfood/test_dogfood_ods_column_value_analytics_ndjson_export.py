"""
tests/python/dogfood/test_dogfood_ods_column_value_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-55
Dogfood export: ODS parse -> column value analytics -> write as NDJSON -> verify.
Uses: spreadsheet_stats, count_distinct_values, average_column, sum_column,
get_all_values, ods_sheet_count.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods import (
    parse_ods,
    spreadsheet_stats,
    count_distinct_values,
    average_column,
    sum_column,
    get_all_values,
    ods_sheet_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_ODS_DIR = _REPO / "samples" / "by-format" / "ods" / "valid"


def _valid_ods_files():
    return sorted(_ODS_DIR.glob("*.ods"))


class TestOdsColumnValueAnalyticsNdjsonExport:
    """ODS -> column value analytics -> NDJSON export -> roundtrip verification."""

    def test_spreadsheet_stats(self):
        sample = str(next(_ODS_DIR.glob("*.ods")))
        doc = parse_ods(sample)
        stats = spreadsheet_stats(doc)
        assert isinstance(stats, dict)

    def test_column_value_analytics(self):
        sample = str(next(_ODS_DIR.glob("*.ods")))
        distinct = count_distinct_values(sample, 0)
        avg = average_column(sample, 0)
        total = sum_column(sample, 0)
        all_vals = get_all_values(sample)
        sheet_count = ods_sheet_count(sample)
        assert distinct >= 0
        assert isinstance(avg, float)
        assert isinstance(total, float)
        assert isinstance(all_vals, list)
        assert sheet_count >= 0

    def test_column_value_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_ods_files():
            path = str(f)
            doc = parse_ods(path)
            stats = spreadsheet_stats(doc)
            distinct = count_distinct_values(path, 0)
            avg = average_column(path, 0)
            total = sum_column(path, 0)
            all_vals = get_all_values(path)
            sheet_count = ods_sheet_count(path)
            assert isinstance(stats, dict), f"spreadsheet_stats must be dict for {f.name}"
            assert distinct >= 0, f"count_distinct_values must be >= 0 for {f.name}"
            assert isinstance(avg, float), f"average_column must be float for {f.name}"
            assert isinstance(total, float), f"sum_column must be float for {f.name}"
            assert isinstance(all_vals, list), f"get_all_values must be list for {f.name}"
            assert sheet_count >= 0, f"ods_sheet_count must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "stats_keys": len(stats),
                "distinct_col0": distinct,
                "avg_col0": avg,
                "sum_col0": total,
                "total_value_count": len(all_vals),
                "sheet_count": sheet_count,
                "source_format": "ods",
            })
        dest = tmp_path / "ods-column-value.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_ods_files():
            path = str(f)
            doc = parse_ods(path)
            stats = spreadsheet_stats(doc)
            distinct = count_distinct_values(path, 0)
            records.append({
                "file": f.name,
                "stats_keys": len(stats),
                "distinct_col0": distinct,
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["stats_keys"] == back["stats_keys"]
            assert orig["distinct_col0"] == back["distinct_col0"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(next(_ODS_DIR.glob("*.ods")))
        doc = parse_ods(sample)
        stats = spreadsheet_stats(doc)
        records = [{"file": "sample.ods", "stats_keys": len(stats)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_sum_avg_export(self, tmp_path):
        records = []
        for f in _valid_ods_files():
            path = str(f)
            avg = average_column(path, 0)
            total = sum_column(path, 0)
            distinct = count_distinct_values(path, 0)
            assert isinstance(avg, float)
            assert isinstance(total, float)
            assert distinct >= 0
            records.append({
                "file": f.name,
                "avg_col0": avg,
                "sum_col0": total,
                "distinct_col0": distinct,
                "format": "ods",
            })
        dest = tmp_path / "sum-avg.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "ods" for r in loaded)
        assert all(r["distinct_col0"] >= 0 for r in loaded)
