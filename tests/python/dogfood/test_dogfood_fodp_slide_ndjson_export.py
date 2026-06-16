"""
tests/python/dogfood/test_dogfood_fodp_slide_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-16
Dogfood export: FODP parse -> extract slide metadata -> write as NDJSON -> verify.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodp import fodp_slide_count, fodp_slide_titles, fodp_has_notes, fodp_image_count
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_FODP_DIR = _REPO / "samples" / "by-format" / "fodp"


class TestFodpSlideNdjsonExport:
    """FODP -> slide metadata extraction -> NDJSON export -> roundtrip verification."""

    def test_slide_count(self):
        sample = str(_FODP_DIR / "two-slides-basic.fodp")
        assert fodp_slide_count(sample) == 2

    def test_slide_titles(self):
        sample = str(_FODP_DIR / "two-slides-basic.fodp")
        titles = fodp_slide_titles(sample)
        assert isinstance(titles, list)
        assert len(titles) == 2

    def test_slide_metadata_to_ndjson(self, tmp_path):
        records = []
        for f in sorted(_FODP_DIR.glob("*.fodp")):
            records.append({
                "file": f.name,
                "slide_count": fodp_slide_count(str(f)),
                "titles": fodp_slide_titles(str(f)),
                "has_notes": fodp_has_notes(str(f)),
                "source_format": "fodp",
            })
        dest = tmp_path / "fodp-slides.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 2

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in sorted(_FODP_DIR.glob("*.fodp")):
            records.append({
                "file": f.name,
                "slide_count": fodp_slide_count(str(f)),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["slide_count"] == back["slide_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(_FODP_DIR / "title-only.fodp")
        records = [{"file": "title-only.fodp", "slides": fodp_slide_count(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_image_count_in_export(self, tmp_path):
        records = []
        for f in sorted(_FODP_DIR.glob("*.fodp")):
            records.append({
                "file": f.name,
                "images": fodp_image_count(str(f)),
                "format": "fodp",
            })
        dest = tmp_path / "images.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert all(r["format"] == "fodp" for r in loaded)
