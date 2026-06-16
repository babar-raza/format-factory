"""
tests/python/dogfood/test_dogfood_csv_uniformity_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-55
Dogfood export: CSV parse -> uniformity analytics -> write as NDJSON -> verify.
Uses: csv_all_rows_same_length, csv_field_type_ratio, csv_max_row_length,
csv_min_field_length, csv_unique_row_count, csv_row_count.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import (
    csv_all_rows_same_length,
    csv_field_type_ratio,
    csv_max_row_length,
    csv_min_field_length,
    csv_unique_row_count,
    csv_row_count,
)
from src.python.ndjson.ndjson_codec import write_ndjson, load_ndjson


_CSV_DIR = _REPO / "samples" / "by-format" / "csv"


def _valid_csv_files():
    return [f for f in sorted(_CSV_DIR.glob("*.csv")) if "invalid" not in f.name.lower()]


class TestCsvUniformityAnalyticsNdjsonExport:
    """CSV -> uniformity analytics -> NDJSON export -> roundtrip verification."""

    def test_all_rows_same_length_and_type_ratio(self):
        sample = str(_valid_csv_files()[0])
        same_len = csv_all_rows_same_length(sample)
        type_ratio = csv_field_type_ratio(sample)
        assert isinstance(same_len, bool)
        assert isinstance(type_ratio, float)

    def test_max_min_field_length_and_unique(self):
        sample = str(_valid_csv_files()[0])
        max_len = csv_max_row_length(sample)
        min_len = csv_min_field_length(sample)
        unique_rows = csv_unique_row_count(sample)
        row_count = csv_row_count(sample)
        assert max_len >= 0
        assert min_len >= 0
        assert unique_rows >= 0
        assert row_count >= 0

    def test_uniformity_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_csv_files():
            path = str(f)
            same_len = csv_all_rows_same_length(path)
            type_ratio = csv_field_type_ratio(path)
            max_len = csv_max_row_length(path)
            min_len = csv_min_field_length(path)
            unique_rows = csv_unique_row_count(path)
            row_count = csv_row_count(path)
            assert isinstance(same_len, bool), f"all_rows_same_length must be bool for {f.name}"
            assert isinstance(type_ratio, float), f"field_type_ratio must be in [0,1] for {f.name}"
            assert max_len >= 0, f"max_row_length must be >= 0 for {f.name}"
            assert min_len >= 0, f"min_field_length must be >= 0 for {f.name}"
            assert unique_rows >= 0, f"unique_row_count must be >= 0 for {f.name}"
            assert row_count >= 0, f"row_count must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "all_rows_same_length": same_len,
                "field_type_ratio": type_ratio,
                "max_row_length": max_len,
                "min_field_length": min_len,
                "unique_row_count": unique_rows,
                "row_count": row_count,
                "source_format": "csv",
            })
        dest = tmp_path / "csv-uniformity.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_csv_files():
            path = str(f)
            records.append({
                "file": f.name,
                "all_rows_same_length": csv_all_rows_same_length(path),
                "field_type_ratio": csv_field_type_ratio(path),
                "unique_row_count": csv_unique_row_count(path),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["all_rows_same_length"] == back["all_rows_same_length"]
            assert orig["unique_row_count"] == back["unique_row_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(_valid_csv_files()[0])
        records = [{"file": "sample.csv", "all_rows_same_length": csv_all_rows_same_length(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_type_ratio_max_export(self, tmp_path):
        records = []
        for f in _valid_csv_files():
            path = str(f)
            type_ratio = csv_field_type_ratio(path)
            max_len = csv_max_row_length(path)
            min_len = csv_min_field_length(path)
            assert isinstance(type_ratio, float)
            assert max_len >= 0
            assert min_len >= 0
            records.append({
                "file": f.name,
                "field_type_ratio": type_ratio,
                "max_row_length": max_len,
                "min_field_length": min_len,
                "format": "csv",
            })
        dest = tmp_path / "type-ratio.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "csv" for r in loaded)
        assert all(isinstance(r["field_type_ratio"], float) for r in loaded)
