"""
tests/python/dogfood/test_dogfood_sylk_ndjson_pipeline.py

Sprint: IDEMPOTENT-SWARM-SPRINT-8
Dogfood export: SYLK parse -> extract metadata -> write as NDJSON -> read back.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from sylk import parse_sylk, sylk_row_count, sylk_column_count
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_SYLK_SAMPLE = str(
    _REPO / "samples" / "by-format" / "sylk" / "valid" / "minimal-2x2.slk"
)


class TestSylkNdjsonPipeline:
    """SYLK -> metadata extraction -> NDJSON write -> read roundtrip."""

    def test_sylk_parses(self):
        doc = parse_sylk(_SYLK_SAMPLE)
        assert isinstance(doc, dict)
        assert doc.get("ok", True)

    def test_extract_metadata_record(self):
        doc = parse_sylk(_SYLK_SAMPLE)
        record = {
            "source_format": "sylk",
            "rows": doc.get("rows", 0),
            "cols": doc.get("cols", 0),
            "cells": doc.get("cell_count", 0),
        }
        assert record["rows"] >= 1
        assert record["cols"] >= 1

    def test_write_metadata_to_ndjson(self, tmp_path):
        doc = parse_sylk(_SYLK_SAMPLE)
        records = [{
            "source_format": "sylk",
            "rows": doc.get("rows", 0),
            "cols": doc.get("cols", 0),
            "cells": doc.get("cell_count", 0),
            "source_file": "minimal-2x2.slk",
        }]
        dest = tmp_path / "sylk-metadata.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0

    def test_roundtrip_preserves_metadata(self, tmp_path):
        doc = parse_sylk(_SYLK_SAMPLE)
        row_count = doc.get("rows", 0)
        records = [{
            "source_format": "sylk",
            "rows": row_count,
            "cols": doc.get("cols", 0),
        }]
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == 1
        assert loaded[0]["source_format"] == "sylk"
        assert loaded[0]["rows"] == row_count

    def test_ndjson_lines_valid_json(self, tmp_path):
        doc = parse_sylk(_SYLK_SAMPLE)
        records = [{"format": "sylk", "cells": doc.get("cell_count", 0)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_multi_file_export(self, tmp_path):
        slk_dir = _REPO / "samples" / "by-format" / "sylk" / "valid"
        records = []
        for f in sorted(slk_dir.glob("*.slk")):
            doc = parse_sylk(str(f))
            records.append({
                "file": f.name,
                "rows": doc.get("rows", 0),
                "cols": doc.get("cols", 0),
            })
        dest = tmp_path / "multi-file.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        assert all(r["file"].endswith(".slk") for r in loaded)
