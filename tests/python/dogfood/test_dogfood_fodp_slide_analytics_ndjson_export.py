"""
tests/python/dogfood/test_dogfood_fodp_slide_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-74
Dogfood export: FODP parse -> slide analytics -> write as NDJSON -> verify.
Uses: fodp_all_slides_have_text, fodp_max_title_length, fodp_notes_to_slide_ratio,
fodp_image_to_slide_ratio, fodp_has_empty_slides, fodp_title_coverage.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodp import (
    fodp_all_slides_have_text,
    fodp_max_title_length,
    fodp_notes_to_slide_ratio,
    fodp_image_to_slide_ratio,
    fodp_has_empty_slides,
    fodp_title_coverage,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_FODP_DIR = _REPO / "samples" / "by-format" / "fodp"


def _valid_fodp_files():
    return sorted(_FODP_DIR.glob("*.fodp"))


class TestFodpSlideAnalyticsNdjsonExport:
    """FODP -> slide analytics -> NDJSON export -> roundtrip verification."""

    def test_slide_text_basics(self):
        sample = str(next(_FODP_DIR.glob("*.fodp")))
        all_have_text = fodp_all_slides_have_text(sample)
        has_empty = fodp_has_empty_slides(sample)
        assert isinstance(all_have_text, bool)
        assert isinstance(has_empty, bool)

    def test_title_and_ratio_basics(self):
        sample = str(next(_FODP_DIR.glob("*.fodp")))
        max_title = fodp_max_title_length(sample)
        notes_ratio = fodp_notes_to_slide_ratio(sample)
        img_ratio = fodp_image_to_slide_ratio(sample)
        coverage = fodp_title_coverage(sample)
        assert max_title >= 0
        assert isinstance(notes_ratio, float)
        assert isinstance(img_ratio, float)
        assert isinstance(coverage, float)

    def test_slide_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_fodp_files():
            path = str(f)
            all_have_text = fodp_all_slides_have_text(path)
            max_title = fodp_max_title_length(path)
            notes_ratio = fodp_notes_to_slide_ratio(path)
            img_ratio = fodp_image_to_slide_ratio(path)
            has_empty = fodp_has_empty_slides(path)
            coverage = fodp_title_coverage(path)
            assert isinstance(all_have_text, bool), f"fodp_all_slides_have_text must be bool for {f.name}"
            assert max_title >= 0, f"fodp_max_title_length must be >= 0 for {f.name}"
            assert isinstance(notes_ratio, float), f"fodp_notes_to_slide_ratio must be float for {f.name}"
            assert isinstance(img_ratio, float), f"fodp_image_to_slide_ratio must be float for {f.name}"
            assert isinstance(has_empty, bool), f"fodp_has_empty_slides must be bool for {f.name}"
            assert isinstance(coverage, float), f"fodp_title_coverage must be float for {f.name}"
            records.append({
                "file": f.name,
                "all_slides_have_text": all_have_text,
                "max_title_length": max_title,
                "notes_to_slide_ratio": notes_ratio,
                "image_to_slide_ratio": img_ratio,
                "has_empty_slides": has_empty,
                "title_coverage": coverage,
                "source_format": "fodp",
            })
        dest = tmp_path / "fodp-slide.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_fodp_files():
            path = str(f)
            all_have_text = fodp_all_slides_have_text(path)
            coverage = fodp_title_coverage(path)
            records.append({
                "file": f.name,
                "all_slides_have_text": all_have_text,
                "title_coverage": coverage,
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["all_slides_have_text"] == back["all_slides_have_text"]
            assert orig["title_coverage"] == back["title_coverage"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(next(_FODP_DIR.glob("*.fodp")))
        has_empty = fodp_has_empty_slides(sample)
        coverage = fodp_title_coverage(sample)
        records = [{"file": "sample.fodp", "has_empty_slides": has_empty, "title_coverage": coverage}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_slide_title_export(self, tmp_path):
        records = []
        for f in _valid_fodp_files():
            path = str(f)
            all_have_text = fodp_all_slides_have_text(path)
            max_title = fodp_max_title_length(path)
            has_empty = fodp_has_empty_slides(path)
            coverage = fodp_title_coverage(path)
            assert isinstance(all_have_text, bool)
            assert max_title >= 0
            assert isinstance(has_empty, bool)
            assert isinstance(coverage, float)
            records.append({
                "file": f.name,
                "all_slides_have_text": all_have_text,
                "max_title_length": max_title,
                "has_empty_slides": has_empty,
                "title_coverage": coverage,
                "format": "fodp",
            })
        dest = tmp_path / "slide-title.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "fodp" for r in loaded)
        assert all(isinstance(r["all_slides_have_text"], bool) for r in loaded)
