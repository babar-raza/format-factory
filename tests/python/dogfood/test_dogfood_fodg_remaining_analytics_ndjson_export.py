"""
tests/python/dogfood/test_dogfood_fodg_remaining_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-75
Dogfood export: FODG parse -> remaining analytics -> write as NDJSON -> verify.
Uses: fodg_all_pages_have_shapes, fodg_text_to_shape_ratio, fodg_max_shapes_per_page,
fodg_min_shapes_per_page, fodg_shape_density, fodg_page_count.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg import (
    fodg_all_pages_have_shapes,
    fodg_text_to_shape_ratio,
    fodg_max_shapes_per_page,
    fodg_min_shapes_per_page,
    fodg_shape_density,
    fodg_page_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_FODG_DIR = _REPO / "samples" / "by-format" / "fodg"


def _valid_fodg_files():
    return sorted(_FODG_DIR.glob("*.fodg"))


class TestFodgRemainingAnalyticsNdjsonExport:
    """FODG -> remaining analytics -> NDJSON export -> roundtrip verification."""

    def test_shape_analytics_basics(self):
        sample = str(next(_FODG_DIR.glob("*.fodg")))
        all_have = fodg_all_pages_have_shapes(sample)
        ratio = fodg_text_to_shape_ratio(sample)
        max_s = fodg_max_shapes_per_page(sample)
        assert isinstance(all_have, bool)
        assert isinstance(ratio, float)
        assert max_s >= 0

    def test_density_and_count_basics(self):
        sample = str(next(_FODG_DIR.glob("*.fodg")))
        density = fodg_shape_density(sample)
        min_s = fodg_min_shapes_per_page(sample)
        page_count = fodg_page_count(sample)
        assert isinstance(density, float)
        assert min_s >= 0
        assert page_count >= 0

    def test_remaining_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_fodg_files():
            path = str(f)
            all_have = fodg_all_pages_have_shapes(path)
            ratio = fodg_text_to_shape_ratio(path)
            max_s = fodg_max_shapes_per_page(path)
            min_s = fodg_min_shapes_per_page(path)
            density = fodg_shape_density(path)
            page_count = fodg_page_count(path)
            assert isinstance(all_have, bool), f"fodg_all_pages_have_shapes must be bool for {f.name}"
            assert isinstance(ratio, float), f"fodg_text_to_shape_ratio must be float for {f.name}"
            assert max_s >= 0, f"fodg_max_shapes_per_page must be >= 0 for {f.name}"
            assert min_s >= 0, f"fodg_min_shapes_per_page must be >= 0 for {f.name}"
            assert isinstance(density, float), f"fodg_shape_density must be float for {f.name}"
            assert page_count >= 0, f"fodg_page_count must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "all_pages_have_shapes": all_have,
                "text_to_shape_ratio": ratio,
                "max_shapes_per_page": max_s,
                "min_shapes_per_page": min_s,
                "shape_density": density,
                "page_count": page_count,
                "source_format": "fodg",
            })
        dest = tmp_path / "fodg-remaining.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_fodg_files():
            path = str(f)
            ratio = fodg_text_to_shape_ratio(path)
            page_count = fodg_page_count(path)
            records.append({
                "file": f.name,
                "text_to_shape_ratio": ratio,
                "page_count": page_count,
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["text_to_shape_ratio"] == back["text_to_shape_ratio"]
            assert orig["page_count"] == back["page_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(next(_FODG_DIR.glob("*.fodg")))
        density = fodg_shape_density(sample)
        page_count = fodg_page_count(sample)
        records = [{"file": "sample.fodg", "shape_density": density, "page_count": page_count}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_shape_density_export(self, tmp_path):
        records = []
        for f in _valid_fodg_files():
            path = str(f)
            density = fodg_shape_density(path)
            all_have = fodg_all_pages_have_shapes(path)
            max_s = fodg_max_shapes_per_page(path)
            min_s = fodg_min_shapes_per_page(path)
            assert isinstance(density, float)
            assert isinstance(all_have, bool)
            assert max_s >= 0
            assert min_s >= 0
            records.append({
                "file": f.name,
                "shape_density": density,
                "all_pages_have_shapes": all_have,
                "max_shapes_per_page": max_s,
                "min_shapes_per_page": min_s,
                "format": "fodg",
            })
        dest = tmp_path / "shape-density.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "fodg" for r in loaded)
        assert all(isinstance(r["shape_density"], float) for r in loaded)
