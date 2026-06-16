"""
tests/python/dogfood/test_dogfood_ods_new_analytics_ndjson_export.py

Sprint: PRODUCT-DEEPENING-SPRINT-20-20260616
Dogfood export: ODS new analytics -> NDJSON export -> verify.
Uses: ods_avg_numeric_value, ods_nonempty_row_ratio, ods_longest_row_index,
      ods_numeric_sum_all, ods_empty_column_count.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods import (
    ods_avg_numeric_value,
    ods_nonempty_row_ratio,
    ods_longest_row_index,
    ods_numeric_sum_all,
    ods_empty_column_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_ODS_DIR = _REPO / "samples" / "by-format" / "ods" / "valid"


class TestOdsNewAnalyticsNdjsonExport:
    """ODS new analytics -> NDJSON export pipeline."""

    def test_avg_numeric_value_returns_float(self):
        sample = str(_ODS_DIR / "numeric-row.ods")
        result = ods_avg_numeric_value(sample)
        assert isinstance(result, float)
        assert result >= 0.0

    def test_nonempty_row_ratio_in_range(self):
        sample = str(_ODS_DIR / "minimal-spreadsheet.ods")
        result = ods_nonempty_row_ratio(sample)
        assert 0.0 <= result <= 1.0

    def test_longest_row_index_nonneg(self):
        sample = str(_ODS_DIR / "minimal-spreadsheet.ods")
        result = ods_longest_row_index(sample)
        assert result >= 0

    def test_numeric_sum_all_nonneg(self):
        sample = str(_ODS_DIR / "numeric-row.ods")
        result = ods_numeric_sum_all(sample)
        assert isinstance(result, float)
        assert result >= 0.0

    def test_empty_column_count_nonneg(self):
        sample = str(_ODS_DIR / "minimal-spreadsheet.ods")
        result = ods_empty_column_count(sample)
        assert isinstance(result, int)
        assert result >= 0

    def test_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in sorted(_ODS_DIR.glob("*.ods")):
            records.append({
                "file": f.name,
                "avg_numeric": ods_avg_numeric_value(str(f)),
                "nonempty_row_ratio": ods_nonempty_row_ratio(str(f)),
                "longest_row_index": ods_longest_row_index(str(f)),
                "numeric_sum_all": ods_numeric_sum_all(str(f)),
                "empty_column_count": ods_empty_column_count(str(f)),
                "source_format": "ods",
            })
        dest = tmp_path / "ods-new-analytics.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in sorted(_ODS_DIR.glob("*.ods")):
            records.append({
                "file": f.name,
                "avg_numeric": ods_avg_numeric_value(str(f)),
                "nonempty_row_ratio": ods_nonempty_row_ratio(str(f)),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(_ODS_DIR / "single-cell.ods")
        records = [{
            "file": "single-cell.ods",
            "avg_numeric": ods_avg_numeric_value(sample),
            "numeric_sum_all": ods_numeric_sum_all(sample),
        }]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)
