"""
tests/python/dogfood/test_dogfood_fodp_shape_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-37
Dogfood export: FODP parse -> shape/layout analytics -> write as NDJSON -> verify.
Uses: fodp_total_shape_count, fodp_slide_shape_counts, fodp_empty_slide_count,
fodp_master_page_count, fodp_has_images, fodp_notes_text, fodp_min_text_per_slide.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodp import (
    fodp_total_shape_count,
    fodp_slide_shape_counts,
    fodp_empty_slide_count,
    fodp_master_page_count,
    fodp_has_images,
    fodp_notes_text,
    fodp_min_text_per_slide,
    fodp_slide_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_FODP_DIR = _REPO / "samples" / "by-format" / "fodp"


def _valid_fodp_files():
    return sorted(_FODP_DIR.glob("*.fodp"))


class TestFodpShapeAnalyticsNdjsonExport:
    """FODP -> shape/layout analytics -> NDJSON export -> roundtrip verification."""

    def test_shape_counts(self):
        sample = str(_FODP_DIR / "two-slides-basic.fodp")
        total = fodp_total_shape_count(sample)
        per_slide = fodp_slide_shape_counts(sample)
        assert total >= 0
        assert isinstance(per_slide, list)

    def test_empty_slides_and_master(self):
        sample = str(_FODP_DIR / "two-slides-basic.fodp")
        empty = fodp_empty_slide_count(sample)
        master = fodp_master_page_count(sample)
        has_images = fodp_has_images(sample)
        assert empty >= 0
        assert master >= 0
        assert isinstance(has_images, bool)

    def test_shape_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_fodp_files():
            path = str(f)
            total = fodp_total_shape_count(path)
            per_slide = fodp_slide_shape_counts(path)
            empty = fodp_empty_slide_count(path)
            master = fodp_master_page_count(path)
            has_images = fodp_has_images(path)
            notes = fodp_notes_text(path)
            min_text = fodp_min_text_per_slide(path)
            slides = fodp_slide_count(path)
            assert total >= 0, f"total_shape_count must be >= 0 for {f.name}"
            assert isinstance(per_slide, list), f"slide_shape_counts must be list for {f.name}"
            assert empty >= 0, f"empty_slide_count must be >= 0 for {f.name}"
            assert master >= 0, f"master_page_count must be >= 0 for {f.name}"
            assert isinstance(has_images, bool), f"has_images must be bool for {f.name}"
            assert isinstance(notes, list), f"notes_text must be list for {f.name}"
            assert min_text >= 0, f"min_text_per_slide must be >= 0 for {f.name}"
            assert slides >= 0, f"slide_count must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "total_shape_count": total,
                "slide_shape_counts": per_slide,
                "empty_slide_count": empty,
                "master_page_count": master,
                "has_images": has_images,
                "notes_slide_count": len(notes),
                "min_text_per_slide": min_text,
                "slide_count": slides,
                "source_format": "fodp",
            })
        dest = tmp_path / "fodp-shapes.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_fodp_files():
            path = str(f)
            records.append({
                "file": f.name,
                "total_shapes": fodp_total_shape_count(path),
                "has_images": fodp_has_images(path),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["total_shapes"] == back["total_shapes"]
            assert orig["has_images"] == back["has_images"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(_FODP_DIR / "two-slides-basic.fodp")
        records = [{"file": "two-slides-basic.fodp", "total_shapes": fodp_total_shape_count(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_master_layout_export(self, tmp_path):
        records = []
        for f in _valid_fodp_files():
            path = str(f)
            master = fodp_master_page_count(path)
            empty = fodp_empty_slide_count(path)
            has_images = fodp_has_images(path)
            assert master >= 0
            assert empty >= 0
            assert isinstance(has_images, bool)
            records.append({
                "file": f.name,
                "master_page_count": master,
                "empty_slide_count": empty,
                "has_images": has_images,
                "format": "fodp",
            })
        dest = tmp_path / "master-layout.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "fodp" for r in loaded)
        assert all(r["master_page_count"] >= 0 for r in loaded)
