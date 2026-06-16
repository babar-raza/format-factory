"""
tests/python/dogfood/test_dogfood_sylk_stats_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-18
Dogfood export: SYLK parse -> extract cell stats -> write as NDJSON -> verify.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from sylk import (
    parse_sylk,
    sylk_row_count,
    sylk_column_count,
    sylk_total_cell_count,
    sylk_numeric_cell_count,
    sylk_string_cell_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_SYLK_DIR = _REPO / "samples" / "by-format" / "sylk" / "valid"


class TestSylkStatsNdjsonExport:
    """SYLK -> cell stats extraction -> NDJSON export -> roundtrip verification."""

    def test_parse_sylk_sample(self):
        sample = str(_SYLK_DIR / "minimal-2x2.slk")
        doc = parse_sylk(sample)
        assert isinstance(doc, dict)

    def test_extract_row_count(self):
        sample = str(_SYLK_DIR / "minimal-2x2.slk")
        rows = sylk_row_count(sample)
        assert rows >= 1

    def test_stats_to_ndjson(self, tmp_path):
        records = []
        for f in sorted(_SYLK_DIR.glob("*.slk")):
            records.append({
                "file": f.name,
                "row_count": sylk_row_count(str(f)),
                "column_count": sylk_column_count(str(f)),
                "total_cells": sylk_total_cell_count(str(f)),
                "numeric_cells": sylk_numeric_cell_count(str(f)),
                "string_cells": sylk_string_cell_count(str(f)),
                "source_format": "sylk",
            })
        dest = tmp_path / "sylk-stats.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in sorted(_SYLK_DIR.glob("*.slk")):
            records.append({
                "file": f.name,
                "row_count": sylk_row_count(str(f)),
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
        sample = str(_SYLK_DIR / "single-cell.slk")
        records = [{"file": "single-cell.slk", "rows": sylk_row_count(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_numeric_density_in_export(self, tmp_path):
        records = []
        for f in sorted(_SYLK_DIR.glob("*.slk")):
            total = sylk_total_cell_count(str(f))
            numeric = sylk_numeric_cell_count(str(f))
            records.append({
                "file": f.name,
                "numeric_density": numeric / total if total > 0 else 0.0,
                "format": "sylk",
            })
        dest = tmp_path / "density.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "sylk" for r in loaded)
