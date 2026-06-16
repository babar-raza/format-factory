"""
tests/python/dogfood/test_dogfood_sylk_cell_dist_analytics_ndjson_export.py

Sprint: PRODUCT-DEEPENING-DOGFOOD-SYLK-DIST-20260616
Dogfood export: SYLK parse -> cell distribution/length analytics -> write as NDJSON -> verify.
Uses: sylk_cell_type_distribution, sylk_avg_row_length, sylk_max_row_length,
sylk_avg_cell_value_length, sylk_max_cell_value_length, sylk_min_cell_value_length,
sylk_unique_column_count.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from sylk import (
    sylk_avg_cell_value_length,
    sylk_avg_row_length,
    sylk_cell_type_distribution,
    sylk_max_cell_value_length,
    sylk_max_row_length,
    sylk_min_cell_value_length,
    sylk_unique_column_count,
)
from ndjson.ndjson_codec import load_ndjson, write_ndjson


_SYLK_DIR = _REPO / "samples" / "by-format" / "sylk" / "valid"


def _ap(f):
    return os.path.abspath(str(f))


def _valid_sylk_files():
    return sorted(p for p in _SYLK_DIR.glob("*") if p.suffix in (".slk", ".sylk"))


class TestSylkCellDistAnalyticsNdjsonExport:
    """SYLK -> cell distribution/length analytics -> NDJSON export -> roundtrip verification."""

    def test_cell_type_distribution_returns_dict(self):
        sample = _ap(next(f for f in _SYLK_DIR.glob("*") if f.suffix in (".slk", ".sylk")))
        dist = sylk_cell_type_distribution(sample)
        assert isinstance(dist, dict), f"cell_type_distribution must return dict, got {type(dist)}"
        assert "numeric" in dist, "distribution must have 'numeric' key"
        assert "string" in dist, "distribution must have 'string' key"
        assert "empty" in dist, "distribution must have 'empty' key"

    def test_concrete_values_minimal_2x2(self):
        path = _ap(_SYLK_DIR / "minimal-2x2.slk")
        dist = sylk_cell_type_distribution(path)
        assert dist["numeric"] == 1
        assert dist["string"] == 3
        assert dist["empty"] == 0
        assert abs(sylk_avg_row_length(path) - 2.0) < 1e-6
        assert sylk_max_row_length(path) == 2
        assert abs(sylk_avg_cell_value_length(path) - 4.0) < 1e-6
        assert sylk_max_cell_value_length(path) == 5
        assert sylk_min_cell_value_length(path) == 2
        assert sylk_unique_column_count(path) == 2

    def test_concrete_values_numeric_row(self):
        path = _ap(_SYLK_DIR / "numeric-row.slk")
        dist = sylk_cell_type_distribution(path)
        assert dist["numeric"] == 3
        assert dist["string"] == 0
        assert abs(sylk_avg_row_length(path) - 3.0) < 1e-6
        assert sylk_max_row_length(path) == 3
        assert sylk_unique_column_count(path) == 3

    def test_row_length_analytics_all_files(self):
        for f in _valid_sylk_files():
            path = _ap(f)
            avg = sylk_avg_row_length(path)
            max_r = sylk_max_row_length(path)
            assert avg >= 0.0, f"avg_row_length must be >= 0 for {f.name}"
            assert max_r >= 0, f"max_row_length must be >= 0 for {f.name}"
            if max_r > 0:
                assert avg <= max_r, f"avg_row_length <= max_row_length for {f.name}"

    def test_cell_value_length_analytics_all_files(self):
        for f in _valid_sylk_files():
            path = _ap(f)
            avg_cv = sylk_avg_cell_value_length(path)
            max_cv = sylk_max_cell_value_length(path)
            min_cv = sylk_min_cell_value_length(path)
            assert avg_cv >= 0.0, f"avg_cell_value_length must be >= 0 for {f.name}"
            assert max_cv >= 0, f"max_cell_value_length must be >= 0 for {f.name}"
            assert min_cv >= 0, f"min_cell_value_length must be >= 0 for {f.name}"

    def test_cell_dist_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_sylk_files():
            path = _ap(f)
            dist = sylk_cell_type_distribution(path)
            avg_row = sylk_avg_row_length(path)
            max_row = sylk_max_row_length(path)
            avg_cv = sylk_avg_cell_value_length(path)
            max_cv = sylk_max_cell_value_length(path)
            min_cv = sylk_min_cell_value_length(path)
            unique_col = sylk_unique_column_count(path)

            assert isinstance(dist, dict)
            assert avg_row >= 0.0
            assert max_row >= 0
            assert avg_cv >= 0.0
            assert max_cv >= 0
            assert min_cv >= 0
            assert unique_col >= 0

            records.append({
                "file": f.name,
                "numeric_cells": dist.get("numeric", 0),
                "string_cells": dist.get("string", 0),
                "empty_cells": dist.get("empty", 0),
                "avg_row_length": avg_row,
                "max_row_length": max_row,
                "avg_cell_value_length": avg_cv,
                "max_cell_value_length": max_cv,
                "min_cell_value_length": min_cv,
                "unique_column_count": unique_col,
                "source_format": "sylk",
            })

        dest = tmp_path / "sylk-cell-dist.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_sylk_files():
            path = _ap(f)
            dist = sylk_cell_type_distribution(path)
            records.append({
                "file": f.name,
                "numeric_cells": dist.get("numeric", 0),
                "avg_row_length": sylk_avg_row_length(path),
                "unique_column_count": sylk_unique_column_count(path),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["numeric_cells"] == back["numeric_cells"]
            assert abs(orig["avg_row_length"] - back["avg_row_length"]) < 1e-9
            assert orig["unique_column_count"] == back["unique_column_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = _ap(next(f for f in _SYLK_DIR.glob("*") if f.suffix in (".slk", ".sylk")))
        dist = sylk_cell_type_distribution(sample)
        records = [{
            "file": "sample.slk",
            "numeric_cells": dist.get("numeric", 0),
            "format": "sylk",
        }]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)
            assert obj["format"] == "sylk"

    def test_distribution_pipeline(self, tmp_path):
        records = []
        for f in _valid_sylk_files():
            path = _ap(f)
            dist = sylk_cell_type_distribution(path)
            unique_col = sylk_unique_column_count(path)
            records.append({
                "file": f.name,
                "numeric_cells": dist.get("numeric", 0),
                "string_cells": dist.get("string", 0),
                "unique_column_count": unique_col,
                "format": "sylk",
            })
        dest = tmp_path / "dist-pipeline.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "sylk" for r in loaded)
        assert all(r["numeric_cells"] >= 0 for r in loaded)
        assert all(r["unique_column_count"] >= 1 for r in loaded)
