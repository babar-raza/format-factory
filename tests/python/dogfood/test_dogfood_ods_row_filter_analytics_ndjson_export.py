"""
tests/python/dogfood/test_dogfood_ods_row_filter_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-57
Dogfood export: ODS parse -> row/filter analytics -> write as NDJSON -> verify.
Uses: get_row_values, get_column_values, get_cell_value, sum_row,
filter_rows_by_value, ods_row_count.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods import (
    get_row_values,
    get_column_values,
    get_cell_value,
    sum_row,
    filter_rows_by_value,
    ods_row_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_ODS_DIR = _REPO / "samples" / "by-format" / "ods" / "valid"


def _valid_ods_files():
    return sorted(_ODS_DIR.glob("*.ods"))


class TestOdsRowFilterAnalyticsNdjsonExport:
    """ODS -> row/filter analytics -> NDJSON export -> roundtrip verification."""

    def test_row_values_and_cell_value(self):
        sample = str(next(_ODS_DIR.glob("*.ods")))
        row_vals = get_row_values(sample, 0, 0)
        cell_val = get_cell_value(sample, 0, 0, 0)
        assert isinstance(row_vals, list)

    def test_column_sum_and_filter(self):
        sample = str(next(_ODS_DIR.glob("*.ods")))
        col_vals = get_column_values(sample, 0)
        total = sum_row(sample, 0)
        row_count = ods_row_count(sample)
        filtered = filter_rows_by_value(sample, 0, None)
        assert isinstance(col_vals, list)
        assert isinstance(total, float)
        assert row_count >= 0
        assert isinstance(filtered, list)

    def test_row_filter_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_ods_files():
            path = str(f)
            row_vals = get_row_values(path, 0, 0)
            col_vals = get_column_values(path, 0)
            total = sum_row(path, 0)
            row_count = ods_row_count(path)
            filtered = filter_rows_by_value(path, 0, None)
            assert isinstance(row_vals, list), f"get_row_values must be list for {f.name}"
            assert isinstance(col_vals, list), f"get_column_values must be list for {f.name}"
            assert isinstance(total, float), f"sum_row must be float for {f.name}"
            assert row_count >= 0, f"ods_row_count must be >= 0 for {f.name}"
            assert isinstance(filtered, list), f"filter_rows_by_value must be list for {f.name}"
            records.append({
                "file": f.name,
                "row0_value_count": len(row_vals),
                "col0_value_count": len(col_vals),
                "sum_row0": total,
                "row_count": row_count,
                "filtered_null_count": len(filtered),
                "source_format": "ods",
            })
        dest = tmp_path / "ods-row-filter.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_ods_files():
            path = str(f)
            col_vals = get_column_values(path, 0)
            total = sum_row(path, 0)
            records.append({
                "file": f.name,
                "col0_value_count": len(col_vals),
                "sum_row0": total,
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["col0_value_count"] == back["col0_value_count"]
            assert orig["sum_row0"] == back["sum_row0"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(next(_ODS_DIR.glob("*.ods")))
        row_vals = get_row_values(sample, 0, 0)
        records = [{"file": "sample.ods", "row0_count": len(row_vals)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_col_sum_row_export(self, tmp_path):
        records = []
        for f in _valid_ods_files():
            path = str(f)
            col_vals = get_column_values(path, 0)
            total = sum_row(path, 0)
            row_count = ods_row_count(path)
            assert isinstance(col_vals, list)
            assert isinstance(total, float)
            assert row_count >= 0
            records.append({
                "file": f.name,
                "col0_value_count": len(col_vals),
                "sum_row0": total,
                "row_count": row_count,
                "format": "ods",
            })
        dest = tmp_path / "col-sum-row.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "ods" for r in loaded)
        assert all(r["row_count"] >= 0 for r in loaded)
