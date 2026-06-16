"""
tests/python/dogfood/test_dogfood_fodg_stats_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-19
Dogfood export: FODG parse -> extract drawing stats -> write as NDJSON -> verify.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg import (
    load as fodg_load,
    get_page_count,
    get_shape_count,
    page_names,
    fodg_total_shape_count,
    fodg_text_shape_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_FODG_DIR = _REPO / "samples" / "by-format" / "fodg"


class TestFodgStatsNdjsonExport:
    """FODG -> drawing stats extraction -> NDJSON export -> roundtrip verification."""

    def test_load_fodg_sample(self):
        sample = str(_FODG_DIR / "minimal-drawing.fodg")
        doc = fodg_load(sample)
        assert doc is not None

    def test_extract_page_count(self):
        sample = str(_FODG_DIR / "shapes-basic.fodg")
        doc = fodg_load(sample)
        pages = get_page_count(doc)
        assert pages >= 1

    def test_stats_to_ndjson(self, tmp_path):
        records = []
        for f in sorted(_FODG_DIR.glob("*.fodg")):
            doc = fodg_load(str(f))
            records.append({
                "file": f.name,
                "page_count": get_page_count(doc),
                "shape_count": get_shape_count(str(f)),
                "pages": page_names(doc),
                "total_shapes": fodg_total_shape_count(str(f)),
                "text_shapes": fodg_text_shape_count(str(f)),
                "source_format": "fodg",
            })
        dest = tmp_path / "fodg-stats.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in sorted(_FODG_DIR.glob("*.fodg")):
            doc = fodg_load(str(f))
            records.append({
                "file": f.name,
                "page_count": get_page_count(doc),
                "shape_count": get_shape_count(str(f)),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["page_count"] == back["page_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(_FODG_DIR / "empty-page.fodg")
        doc = fodg_load(sample)
        records = [{"file": "empty-page.fodg", "pages": get_page_count(doc)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_shapes_per_page_in_export(self, tmp_path):
        records = []
        for f in sorted(_FODG_DIR.glob("*.fodg")):
            doc = fodg_load(str(f))
            pages = get_page_count(doc)
            shapes = get_shape_count(str(f))
            records.append({
                "file": f.name,
                "shapes_per_page": shapes / pages if pages > 0 else 0.0,
                "format": "fodg",
            })
        dest = tmp_path / "spp.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "fodg" for r in loaded)
