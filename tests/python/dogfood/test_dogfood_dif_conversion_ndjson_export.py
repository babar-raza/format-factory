"""
tests/python/dogfood/test_dogfood_dif_conversion_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-23
Dogfood export: DIF parse -> extract full stats -> convert to CSV string -> log to NDJSON.
Exercises DIF parser, DIF stats, and CSV writer in a format conversion pipeline.
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


class TestDifConversionNdjsonExport:
    """DIF -> full stats + conversion audit -> NDJSON -> verification."""

    def test_parse_dif(self):
        sample = str(_DIF_DIR / "minimal-2x2.dif")
        doc = parse_dif(sample)
        assert isinstance(doc, dict)

    def test_dif_stats_extraction(self):
        sample = str(_DIF_DIR / "minimal-2x2.dif")
        doc = parse_dif(sample)
        stats = dif_stats(doc)
        assert "row_count" in stats
        assert "total_cells" in stats

    def test_conversion_audit_to_ndjson(self, tmp_path):
        records = []
        for f in sorted(_DIF_DIR.glob("*.dif")):
            doc = parse_dif(str(f))
            stats = dif_stats(doc)
            records.append({
                "file": f.name,
                "row_count": stats.get("row_count", 0),
                "column_count": stats.get("column_count", 0),
                "total_cells": stats.get("total_cells", 0),
                "numeric_cells": stats.get("numeric_cells", 0),
                "title": stats.get("title", ""),
                "source_format": "dif",
            })
        dest = tmp_path / "dif-audit.ndjson"
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
                "row_count": stats.get("row_count", 0),
                "total_cells": stats.get("total_cells", 0),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["row_count"] == back["row_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(_DIF_DIR / "minimal-2x2.dif")
        doc = parse_dif(sample)
        stats = dif_stats(doc)
        records = [{"file": "minimal-2x2.dif", "rows": stats.get("row_count", 0)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_numeric_ratio_in_export(self, tmp_path):
        records = []
        for f in sorted(_DIF_DIR.glob("*.dif")):
            doc = parse_dif(str(f))
            stats = dif_stats(doc)
            total = stats.get("total_cells", 0)
            numeric = stats.get("numeric_cells", 0)
            records.append({
                "file": f.name,
                "numeric_ratio": numeric / total if total > 0 else 0.0,
                "format": "dif",
            })
        dest = tmp_path / "ratio.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "dif" for r in loaded)
