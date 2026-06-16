"""
tests/python/dogfood/test_dogfood_xcf_layer_geometry_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-26
Dogfood export: XCF parse -> layer geometry analytics -> write as NDJSON -> verify.
Uses deeper XCF analytics: layer-to-canvas ratio, total layer area, megapixels, etc.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from xcf import (
    xcf_layer_count,
    xcf_layer_to_canvas_ratio,
    xcf_total_layers_area,
    xcf_average_layer_size,
    xcf_megapixels,
    xcf_is_landscape,
    xcf_canvas_size_bytes,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_XCF_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"


class TestXcfLayerGeometryNdjsonExport:
    """XCF -> layer geometry analytics -> NDJSON export -> roundtrip verification."""

    def test_layer_count(self):
        sample = os.path.abspath(str(_XCF_DIR / "2x2-gray.xcf"))
        count = xcf_layer_count(sample)
        assert isinstance(count, int)
        assert count >= 1

    def test_megapixels(self):
        sample = os.path.abspath(str(_XCF_DIR / "1x1-red-rgb.xcf"))
        mp = xcf_megapixels(sample)
        assert isinstance(mp, (int, float))
        assert mp >= 0

    def test_layer_geometry_to_ndjson(self, tmp_path):
        records = []
        for f in sorted(_XCF_DIR.glob("*.xcf")):
            p = os.path.abspath(str(f))
            records.append({
                "file": f.name,
                "layer_count": xcf_layer_count(p),
                "layer_to_canvas_ratio": xcf_layer_to_canvas_ratio(p),
                "total_layers_area": xcf_total_layers_area(p),
                "avg_layer_size": xcf_average_layer_size(p),
                "megapixels": xcf_megapixels(p),
                "is_landscape": xcf_is_landscape(p),
                "canvas_bytes": xcf_canvas_size_bytes(p),
                "source_format": "xcf",
            })
        dest = tmp_path / "xcf-layer-geometry.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in sorted(_XCF_DIR.glob("*.xcf")):
            p = os.path.abspath(str(f))
            records.append({
                "file": f.name,
                "layer_count": xcf_layer_count(p),
                "megapixels": xcf_megapixels(p),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["layer_count"] == back["layer_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = os.path.abspath(str(_XCF_DIR / "2x2-gray.xcf"))
        records = [{"file": "2x2-gray.xcf", "layers": xcf_layer_count(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_landscape_ratio_export(self, tmp_path):
        records = []
        for f in sorted(_XCF_DIR.glob("*.xcf")):
            p = os.path.abspath(str(f))
            records.append({
                "file": f.name,
                "is_landscape": xcf_is_landscape(p),
                "layer_ratio": xcf_layer_to_canvas_ratio(p),
                "format": "xcf",
            })
        dest = tmp_path / "landscape.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "xcf" for r in loaded)
