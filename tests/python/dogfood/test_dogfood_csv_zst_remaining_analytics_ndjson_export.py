"""
tests/python/dogfood/test_dogfood_csv_zst_remaining_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-72
Dogfood export: CSV remaining analytics + ZST remaining analytics -> write as NDJSON -> verify.
Uses CSV: csv_empty_cell_ratio, csv_distinct_value_count, csv_row_count, csv_column_count.
Uses ZST: zst_is_single_frame, zst_max_frame_size, zst_frame_count, zst_compressed_size.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]

# CSV uses repo-level path due to stdlib conflict
sys.path.insert(0, str(_REPO))
from src.python.ff_csv.csv_parser import (
    csv_empty_cell_ratio,
    csv_distinct_value_count,
    csv_row_count,
    csv_column_count,
)

# ZST uses src/python-level path
sys.path.insert(0, str(_REPO / "src" / "python"))
from zst import (
    zst_is_single_frame,
    zst_max_frame_size,
    zst_frame_count,
    zst_compressed_size,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_CSV_DIR = _REPO / "samples" / "by-format" / "csv"
_ZST_DIR = _REPO / "samples" / "by-format" / "zst" / "valid"


def _valid_csv_files():
    return sorted(_CSV_DIR.glob("*.csv"))


def _valid_zst_files():
    return sorted(_ZST_DIR.glob("*.zst"))


class TestCsvZstRemainingAnalyticsNdjsonExport:
    """CSV/ZST remaining analytics -> NDJSON export -> roundtrip verification."""

    def test_csv_remaining_basics(self):
        sample = str(next(_CSV_DIR.glob("*.csv")))
        ratio = csv_empty_cell_ratio(sample)
        distinct = csv_distinct_value_count(sample)
        assert isinstance(ratio, float)
        assert distinct >= 0

    def test_zst_remaining_basics(self):
        sample = str(next(_ZST_DIR.glob("*.zst")))
        is_single = zst_is_single_frame(sample)
        max_size = zst_max_frame_size(sample)
        assert isinstance(is_single, bool)
        assert max_size >= 0

    def test_csv_remaining_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_csv_files():
            path = str(f)
            ratio = csv_empty_cell_ratio(path)
            distinct = csv_distinct_value_count(path)
            row_count = csv_row_count(path)
            col_count = csv_column_count(path)
            assert isinstance(ratio, float), f"csv_empty_cell_ratio must be float for {f.name}"
            assert distinct >= 0, f"csv_distinct_value_count must be >= 0 for {f.name}"
            assert row_count >= 0, f"csv_row_count must be >= 0 for {f.name}"
            assert col_count >= 0, f"csv_column_count must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "empty_cell_ratio": ratio,
                "distinct_value_count": distinct,
                "row_count": row_count,
                "col_count": col_count,
                "source_format": "csv",
            })
        dest = tmp_path / "csv-remaining.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_zst_remaining_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_zst_files():
            path = str(f)
            is_single = zst_is_single_frame(path)
            max_size = zst_max_frame_size(path)
            frame_count = zst_frame_count(path)
            total_size = zst_compressed_size(path)
            assert isinstance(is_single, bool), f"zst_is_single_frame must be bool for {f.name}"
            assert max_size >= 0, f"zst_max_frame_size must be >= 0 for {f.name}"
            assert frame_count >= 0, f"zst_frame_count must be >= 0 for {f.name}"
            assert total_size >= 0, f"zst_compressed_size must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "is_single_frame": is_single,
                "max_frame_size": max_size,
                "frame_count": frame_count,
                "total_compressed_size": total_size,
                "source_format": "zst",
            })
        dest = tmp_path / "zst-remaining.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_csv_files():
            path = str(f)
            ratio = csv_empty_cell_ratio(path)
            distinct = csv_distinct_value_count(path)
            records.append({
                "file": f.name,
                "empty_cell_ratio": ratio,
                "distinct_value_count": distinct,
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["empty_cell_ratio"] == back["empty_cell_ratio"]
            assert orig["distinct_value_count"] == back["distinct_value_count"]

    def test_json_lines_valid(self, tmp_path):
        sample_csv = str(next(_CSV_DIR.glob("*.csv")))
        ratio = csv_empty_cell_ratio(sample_csv)
        sample_zst = str(next(_ZST_DIR.glob("*.zst")))
        is_single = zst_is_single_frame(sample_zst)
        records = [
            {"file": "sample.csv", "empty_cell_ratio": ratio, "format": "csv"},
            {"file": "sample.zst", "is_single_frame": is_single, "format": "zst"},
        ]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)
