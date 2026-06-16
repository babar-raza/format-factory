"""
tests/python/dogfood/test_dogfood_dif_avg_numeric_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-63
Dogfood export: DIF parse -> avg/numeric analytics -> write as NDJSON -> verify.
Uses: dif_avg_row_length, dif_all_numeric, dif_column_unique_count,
dif_row_count, dif_column_count, dif_total_cell_count.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif import (
    dif_avg_row_length,
    dif_all_numeric,
    dif_column_unique_count,
    dif_row_count,
    dif_column_count,
    dif_total_cell_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_DIF_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"


def _valid_dif_files():
    return sorted(_DIF_DIR.glob("*.dif"))


class TestDifAvgNumericAnalyticsNdjsonExport:
    """DIF -> avg/numeric analytics -> NDJSON export -> roundtrip verification."""

    def test_avg_row_length_and_all_numeric(self):
        sample = str(next(_DIF_DIR.glob("*.dif")))
        avg = dif_avg_row_length(sample)
        all_num = dif_all_numeric(sample)
        assert isinstance(avg, float)
        assert isinstance(all_num, bool)

    def test_column_unique_count_and_basic_stats(self):
        sample = str(next(_DIF_DIR.glob("*.dif")))
        unique = dif_column_unique_count(sample, 0)
        row_count = dif_row_count(sample)
        col_count = dif_column_count(sample)
        total = dif_total_cell_count(sample)
        assert unique >= 0
        assert row_count >= 0
        assert col_count >= 0
        assert total >= 0

    def test_avg_numeric_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_dif_files():
            path = str(f)
            avg = dif_avg_row_length(path)
            all_num = dif_all_numeric(path)
            unique = dif_column_unique_count(path, 0)
            row_count = dif_row_count(path)
            col_count = dif_column_count(path)
            total = dif_total_cell_count(path)
            assert isinstance(avg, float), f"dif_avg_row_length must be float for {f.name}"
            assert isinstance(all_num, bool), f"dif_all_numeric must be bool for {f.name}"
            assert unique >= 0, f"dif_column_unique_count must be >= 0 for {f.name}"
            assert row_count >= 0, f"dif_row_count must be >= 0 for {f.name}"
            assert col_count >= 0, f"dif_column_count must be >= 0 for {f.name}"
            assert total >= 0, f"dif_total_cell_count must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "avg_row_length": avg,
                "all_numeric": all_num,
                "col0_unique_count": unique,
                "row_count": row_count,
                "col_count": col_count,
                "total_cells": total,
                "source_format": "dif",
            })
        dest = tmp_path / "dif-avg-numeric.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_dif_files():
            path = str(f)
            avg = dif_avg_row_length(path)
            all_num = dif_all_numeric(path)
            records.append({
                "file": f.name,
                "avg_row_length": avg,
                "all_numeric": all_num,
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["avg_row_length"] == back["avg_row_length"]
            assert orig["all_numeric"] == back["all_numeric"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(next(_DIF_DIR.glob("*.dif")))
        avg = dif_avg_row_length(sample)
        records = [{"file": "sample.dif", "avg_row_length": avg}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_unique_numeric_export(self, tmp_path):
        records = []
        for f in _valid_dif_files():
            path = str(f)
            avg = dif_avg_row_length(path)
            all_num = dif_all_numeric(path)
            unique = dif_column_unique_count(path, 0)
            assert isinstance(avg, float)
            assert isinstance(all_num, bool)
            assert unique >= 0
            records.append({
                "file": f.name,
                "avg_row_length": avg,
                "all_numeric": all_num,
                "col0_unique_count": unique,
                "format": "dif",
            })
        dest = tmp_path / "unique-numeric.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "dif" for r in loaded)
        assert all(r["col0_unique_count"] >= 0 for r in loaded)
