"""
tests/python/dogfood/test_dogfood_xcf_layer_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-44
Dogfood export: XCF parse -> layer analytics -> write as NDJSON -> verify.
Uses: xcf_layer_count, xcf_megapixels, xcf_has_alpha, xcf_layer_to_canvas_ratio,
xcf_total_layers_area, xcf_average_layer_size, xcf_is_landscape.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf.xcf_parser import (
    xcf_layer_count,
    xcf_megapixels,
    xcf_has_alpha,
    xcf_layer_to_canvas_ratio,
    xcf_total_layers_area,
    xcf_average_layer_size,
    xcf_is_landscape,
)
from src.python.ndjson.ndjson_codec import write_ndjson, load_ndjson


_XCF_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"


def _ap(f):
    return os.path.abspath(str(f))


def _valid_xcf_files():
    return sorted(_XCF_DIR.glob("*.xcf"))


class TestXcfLayerAnalyticsNdjsonExport:
    """XCF -> layer analytics -> NDJSON export -> roundtrip verification."""

    def test_layer_count_and_alpha(self):
        sample = _ap(next(_XCF_DIR.glob("*.xcf")))
        count = xcf_layer_count(sample)
        has_alpha = xcf_has_alpha(sample)
        assert count >= 0
        assert isinstance(has_alpha, bool)

    def test_megapixels_and_landscape(self):
        sample = _ap(next(_XCF_DIR.glob("*.xcf")))
        mp = xcf_megapixels(sample)
        is_land = xcf_is_landscape(sample)
        assert mp >= 0.0
        assert isinstance(is_land, bool)

    def test_layer_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_xcf_files():
            path = _ap(f)
            count = xcf_layer_count(path)
            mp = xcf_megapixels(path)
            has_alpha = xcf_has_alpha(path)
            ratio = xcf_layer_to_canvas_ratio(path)
            total_area = xcf_total_layers_area(path)
            avg_size = xcf_average_layer_size(path)
            is_land = xcf_is_landscape(path)
            assert count >= 0, f"layer_count must be >= 0 for {f.name}"
            assert mp >= 0.0, f"megapixels must be >= 0 for {f.name}"
            assert isinstance(has_alpha, bool), f"has_alpha must be bool for {f.name}"
            assert ratio >= 0.0, f"layer_to_canvas_ratio must be >= 0 for {f.name}"
            assert total_area >= 0, f"total_layers_area must be >= 0 for {f.name}"
            assert avg_size >= 0.0, f"average_layer_size must be >= 0 for {f.name}"
            assert isinstance(is_land, bool), f"is_landscape must be bool for {f.name}"
            records.append({
                "file": f.name,
                "layer_count": count,
                "megapixels": mp,
                "has_alpha": has_alpha,
                "layer_to_canvas_ratio": ratio,
                "total_layers_area": total_area,
                "average_layer_size": avg_size,
                "is_landscape": is_land,
                "source_format": "xcf",
            })
        dest = tmp_path / "xcf-layer-analytics.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_xcf_files():
            path = _ap(f)
            records.append({
                "file": f.name,
                "layer_count": xcf_layer_count(path),
                "has_alpha": xcf_has_alpha(path),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["layer_count"] == back["layer_count"]
            assert orig["has_alpha"] == back["has_alpha"]

    def test_json_lines_valid(self, tmp_path):
        sample = _ap(next(_XCF_DIR.glob("*.xcf")))
        records = [{"file": "sample.xcf", "layer_count": xcf_layer_count(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_layer_area_export(self, tmp_path):
        records = []
        for f in _valid_xcf_files():
            path = _ap(f)
            total_area = xcf_total_layers_area(path)
            avg_size = xcf_average_layer_size(path)
            ratio = xcf_layer_to_canvas_ratio(path)
            assert total_area >= 0
            assert avg_size >= 0.0
            assert ratio >= 0.0
            records.append({
                "file": f.name,
                "total_layers_area": total_area,
                "average_layer_size": avg_size,
                "layer_to_canvas_ratio": ratio,
                "format": "xcf",
            })
        dest = tmp_path / "layer-area.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "xcf" for r in loaded)
        assert all(r["total_layers_area"] >= 0 for r in loaded)
