"""
tests/python/dogfood/test_dogfood_sylk_numeric_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-44
Dogfood export: SYLK parse -> numeric/density analytics -> write as NDJSON -> verify.
Uses: sylk_numeric_cell_count, sylk_string_cell_count, sylk_total_sum,
sylk_column_count, sylk_average_numeric_value, sylk_numeric_density, sylk_string_density.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from sylk import (
    sylk_numeric_cell_count,
    sylk_string_cell_count,
    sylk_total_sum,
    sylk_column_count,
    sylk_average_numeric_value,
    sylk_numeric_density,
    sylk_string_density,
    sylk_total_cell_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_SYLK_DIR = _REPO / "samples" / "by-format" / "sylk" / "valid"


def _valid_sylk_files():
    return sorted(_SYLK_DIR.glob("*.slk"))


class TestSylkNumericAnalyticsNdjsonExport:
    """SYLK -> numeric/density analytics -> NDJSON export -> roundtrip verification."""

    def test_numeric_and_string_counts(self):
        sample = str(next(_SYLK_DIR.glob("*.slk")))
        num = sylk_numeric_cell_count(sample)
        strs = sylk_string_cell_count(sample)
        assert num >= 0
        assert strs >= 0

    def test_density_and_sum(self):
        sample = str(next(_SYLK_DIR.glob("*.slk")))
        nd = sylk_numeric_density(sample)
        sd = sylk_string_density(sample)
        total_sum = sylk_total_sum(sample)
        assert 0.0 <= nd <= 1.0
        assert 0.0 <= sd <= 1.0
        assert isinstance(total_sum, float)

    def test_numeric_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_sylk_files():
            path = str(f)
            num = sylk_numeric_cell_count(path)
            strs = sylk_string_cell_count(path)
            total_sum = sylk_total_sum(path)
            cols = sylk_column_count(path)
            avg = sylk_average_numeric_value(path)
            nd = sylk_numeric_density(path)
            sd = sylk_string_density(path)
            total = sylk_total_cell_count(path)
            assert num >= 0, f"numeric_cell_count must be >= 0 for {f.name}"
            assert strs >= 0, f"string_cell_count must be >= 0 for {f.name}"
            assert isinstance(total_sum, float), f"total_sum must be float for {f.name}"
            assert cols >= 0, f"column_count must be >= 0 for {f.name}"
            assert isinstance(avg, float), f"average_numeric_value must be float for {f.name}"
            assert 0.0 <= nd <= 1.0, f"numeric_density out of range for {f.name}"
            assert 0.0 <= sd <= 1.0, f"string_density out of range for {f.name}"
            records.append({
                "file": f.name,
                "numeric_cells": num,
                "string_cells": strs,
                "total_sum": total_sum,
                "column_count": cols,
                "avg_numeric_value": avg,
                "numeric_density": nd,
                "string_density": sd,
                "total_cells": total,
                "source_format": "sylk",
            })
        dest = tmp_path / "sylk-numeric.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_sylk_files():
            path = str(f)
            records.append({
                "file": f.name,
                "numeric_cells": sylk_numeric_cell_count(path),
                "numeric_density": sylk_numeric_density(path),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["numeric_cells"] == back["numeric_cells"]
            assert abs(orig["numeric_density"] - back["numeric_density"]) < 1e-9

    def test_json_lines_valid(self, tmp_path):
        sample = str(next(_SYLK_DIR.glob("*.slk")))
        records = [{"file": "sample.slk", "numeric_density": sylk_numeric_density(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_density_distribution_export(self, tmp_path):
        records = []
        for f in _valid_sylk_files():
            path = str(f)
            nd = sylk_numeric_density(path)
            sd = sylk_string_density(path)
            num = sylk_numeric_cell_count(path)
            strs = sylk_string_cell_count(path)
            assert 0.0 <= nd <= 1.0
            assert 0.0 <= sd <= 1.0
            assert num >= 0
            assert strs >= 0
            records.append({
                "file": f.name,
                "numeric_density": nd,
                "string_density": sd,
                "numeric_cells": num,
                "string_cells": strs,
                "format": "sylk",
            })
        dest = tmp_path / "density-dist.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "sylk" for r in loaded)
        assert all(0.0 <= r["numeric_density"] <= 1.0 for r in loaded)
