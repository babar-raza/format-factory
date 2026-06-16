"""
tests/python/dogfood/test_dogfood_sylk_density_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-27
Dogfood export: SYLK parse -> data density analytics -> write as NDJSON -> verify.
Uses deeper SYLK analytics: numeric/string density, average numeric value, max row length, etc.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from sylk import (
    sylk_numeric_density,
    sylk_string_density,
    sylk_average_numeric_value,
    sylk_max_row_length,
    sylk_nonempty_cell_count,
    sylk_total_cell_count,
    sylk_total_sum,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_SYLK_DIR = _REPO / "samples" / "by-format" / "sylk" / "valid"


class TestSylkDensityAnalyticsNdjsonExport:
    """SYLK -> data density analytics -> NDJSON export -> roundtrip verification."""

    def test_numeric_density(self):
        sample = str(_SYLK_DIR / "minimal-2x2.slk")
        density = sylk_numeric_density(sample)
        assert isinstance(density, (int, float))
        assert 0.0 <= density <= 1.0

    def test_string_density(self):
        sample = str(_SYLK_DIR / "minimal-2x2.slk")
        density = sylk_string_density(sample)
        assert isinstance(density, (int, float))
        assert 0.0 <= density <= 1.0

    def test_density_to_ndjson(self, tmp_path):
        records = []
        for f in sorted(_SYLK_DIR.glob("*.slk")):
            total = sylk_total_cell_count(str(f))
            nonempty = sylk_nonempty_cell_count(str(f))
            assert nonempty <= total, f"nonempty ({nonempty}) > total ({total})"
            records.append({
                "file": f.name,
                "numeric_density": sylk_numeric_density(str(f)),
                "string_density": sylk_string_density(str(f)),
                "avg_numeric": sylk_average_numeric_value(str(f)),
                "max_row_length": sylk_max_row_length(str(f)),
                "nonempty_cells": nonempty,
                "total_cells": total,
                "total_sum": sylk_total_sum(str(f)),
                "source_format": "sylk",
            })
        dest = tmp_path / "sylk-density.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in sorted(_SYLK_DIR.glob("*.slk")):
            records.append({
                "file": f.name,
                "numeric_density": sylk_numeric_density(str(f)),
                "total_cells": sylk_total_cell_count(str(f)),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["total_cells"] == back["total_cells"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(_SYLK_DIR / "minimal-2x2.slk")
        records = [{"file": "minimal-2x2.slk", "density": sylk_numeric_density(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_density_balance_export(self, tmp_path):
        records = []
        for f in sorted(_SYLK_DIR.glob("*.slk")):
            nd = sylk_numeric_density(str(f))
            sd = sylk_string_density(str(f))
            assert nd + sd <= 1.0 + 1e-9, f"densities sum > 1 for {f.name}"
            records.append({
                "file": f.name,
                "numeric_density": nd,
                "string_density": sd,
                "format": "sylk",
            })
        dest = tmp_path / "balance.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "sylk" for r in loaded)
