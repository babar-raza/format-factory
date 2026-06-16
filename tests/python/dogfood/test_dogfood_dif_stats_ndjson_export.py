"""
tests/python/dogfood/test_dogfood_dif_stats_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-12
Dogfood export: DIF parse -> extract stats -> write as NDJSON -> verify.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif import parse_dif
from dif.dif_stats import dif_stats
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_DIF_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"


class TestDifStatsNdjsonExport:
    """DIF -> stats extraction -> NDJSON export -> roundtrip verification."""

    def test_parse_dif_sample(self):
        sample = str(_DIF_DIR / "minimal-2x2.dif")
        doc = parse_dif(sample)
        assert isinstance(doc, dict)

    def test_extract_stats(self):
        sample = str(_DIF_DIR / "minimal-2x2.dif")
        doc = parse_dif(sample)
        stats = dif_stats(doc)
        assert isinstance(stats, dict)
        assert stats["row_count"] >= 1
        assert stats["total_cells"] >= 1

    def test_stats_to_ndjson(self, tmp_path):
        records = []
        for f in sorted(_DIF_DIR.glob("*.dif")):
            doc = parse_dif(str(f))
            stats = dif_stats(doc)
            records.append({
                "file": f.name,
                "rows": stats["row_count"],
                "total_cells": stats["total_cells"],
                "numeric_cells": stats["numeric_cells"],
                "source_format": "dif",
            })
        dest = tmp_path / "dif-stats.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in sorted(_DIF_DIR.glob("*.dif")):
            doc = parse_dif(str(f))
            stats = dif_stats(doc)
            records.append({
                "file": f.name,
                "rows": stats["row_count"],
                "title": stats.get("title", ""),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["rows"] == back["rows"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(_DIF_DIR / "single-cell.dif")
        doc = parse_dif(sample)
        stats = dif_stats(doc)
        records = [{"file": "single-cell.dif", "cells": stats["total_cells"]}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_title_field_preserved(self, tmp_path):
        sample = str(_DIF_DIR / "minimal-2x2.dif")
        doc = parse_dif(sample)
        stats = dif_stats(doc)
        record = {"file": "minimal-2x2.dif", "title": stats["title"], "format": "dif"}
        dest = tmp_path / "title.ndjson"
        write_ndjson([record], str(dest))
        loaded = load_ndjson(str(dest))
        assert loaded[0]["title"] == stats["title"]
        assert loaded[0]["format"] == "dif"
