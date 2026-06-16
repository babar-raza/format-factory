"""
tests/python/dogfood/test_dogfood_dif_structure_analytics_ndjson_export.py

Sprint: PRODUCT-DEEPENING-DOGFOOD-DIF-STRUCT-20260616
Dogfood export: DIF parse -> structure/type analytics -> write as NDJSON -> verify.
Uses: dif_all_numeric, dif_avg_row_length, dif_min_numeric_value,
dif_string_row_count, dif_vectors_count.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif import (
    dif_all_numeric,
    dif_avg_row_length,
    dif_min_numeric_value,
    dif_string_row_count,
    dif_vectors_count,
)
from ndjson.ndjson_codec import load_ndjson, write_ndjson


_DIF_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"


def _ap(f):
    return os.path.abspath(str(f))


def _valid_dif_files():
    return sorted(_DIF_DIR.glob("*.dif"))


class TestDifStructureAnalyticsNdjsonExport:
    """DIF -> structure/type analytics -> NDJSON export -> roundtrip verification."""

    def test_all_numeric_returns_bool(self):
        for f in _valid_dif_files():
            result = dif_all_numeric(_ap(f))
            assert isinstance(result, bool), f"dif_all_numeric must return bool for {f.name}"

    def test_concrete_values_numeric_row(self):
        path = _ap(_DIF_DIR / "numeric-row.dif")
        assert dif_all_numeric(path) is True
        assert abs(dif_avg_row_length(path) - 3.0) < 1e-6
        assert abs(dif_min_numeric_value(path) - 1.0) < 1e-6
        assert dif_string_row_count(path) == 0
        assert dif_vectors_count(path) == 3

    def test_concrete_values_minimal_2x2(self):
        path = _ap(_DIF_DIR / "minimal-2x2.dif")
        assert dif_all_numeric(path) is False
        assert abs(dif_avg_row_length(path) - 8.0) < 1e-6
        assert abs(dif_min_numeric_value(path) - 42.0) < 1e-6
        assert dif_string_row_count(path) == 1
        assert dif_vectors_count(path) == 2

    def test_vectors_count_all_files(self):
        for f in _valid_dif_files():
            path = _ap(f)
            vect = dif_vectors_count(path)
            avg_row = dif_avg_row_length(path)
            assert vect >= 0, f"vectors_count must be >= 0 for {f.name}"
            assert avg_row >= 0.0, f"avg_row_length must be >= 0 for {f.name}"

    def test_structure_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_dif_files():
            path = _ap(f)
            all_num = dif_all_numeric(path)
            avg_row = dif_avg_row_length(path)
            min_num = dif_min_numeric_value(path)
            str_rows = dif_string_row_count(path)
            vect = dif_vectors_count(path)

            assert isinstance(all_num, bool)
            assert avg_row >= 0.0
            assert str_rows >= 0
            assert vect >= 0

            records.append({
                "file": f.name,
                "all_numeric": all_num,
                "avg_row_length": avg_row,
                "min_numeric_value": min_num,
                "string_row_count": str_rows,
                "vectors_count": vect,
                "source_format": "dif",
            })

        dest = tmp_path / "dif-structure.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_dif_files():
            path = _ap(f)
            records.append({
                "file": f.name,
                "all_numeric": dif_all_numeric(path),
                "vectors_count": dif_vectors_count(path),
                "string_row_count": dif_string_row_count(path),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["all_numeric"] == back["all_numeric"]
            assert orig["vectors_count"] == back["vectors_count"]
            assert orig["string_row_count"] == back["string_row_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = _ap(next(_DIF_DIR.glob("*.dif")))
        records = [{
            "file": "sample.dif",
            "all_numeric": dif_all_numeric(sample),
            "vectors_count": dif_vectors_count(sample),
            "format": "dif",
        }]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)
            assert obj["format"] == "dif"

    def test_avg_row_pipeline(self, tmp_path):
        records = []
        for f in _valid_dif_files():
            path = _ap(f)
            records.append({
                "file": f.name,
                "avg_row_length": dif_avg_row_length(path),
                "vectors_count": dif_vectors_count(path),
                "all_numeric": dif_all_numeric(path),
                "format": "dif",
            })
        dest = tmp_path / "avg-row.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "dif" for r in loaded)
        assert all(r["avg_row_length"] >= 0.0 for r in loaded)
        assert all(r["vectors_count"] >= 1 for r in loaded)
