"""
tests/python/dogfood/test_dogfood_xcf_canvas_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-52
Dogfood export: XCF parse -> canvas analytics -> write as NDJSON -> verify.
Uses: xcf_compression_ratio, xcf_file_size, xcf_image_dimensions, xcf_is_portrait,
xcf_layer_count_per_megapixel, xcf_layers_per_dimension.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf.xcf_parser import (
    xcf_compression_ratio,
    xcf_file_size,
    xcf_image_dimensions,
    xcf_is_portrait,
    xcf_layer_count_per_megapixel,
    xcf_layers_per_dimension,
)
from src.python.ndjson.ndjson_codec import write_ndjson, load_ndjson


_XCF_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"


def _ap(f):
    return os.path.abspath(str(f))


def _valid_xcf_files():
    return sorted(_XCF_DIR.glob("*.xcf"))


class TestXcfCanvasAnalyticsNdjsonExport:
    """XCF -> canvas analytics -> NDJSON export -> roundtrip verification."""

    def test_compression_and_file_size(self):
        sample = _ap(next(_XCF_DIR.glob("*.xcf")))
        ratio = xcf_compression_ratio(sample)
        size = xcf_file_size(sample)
        assert ratio >= 0.0
        assert size >= 0

    def test_dimensions_portrait_and_layer_density(self):
        sample = _ap(next(_XCF_DIR.glob("*.xcf")))
        dims = xcf_image_dimensions(sample)
        is_portrait = xcf_is_portrait(sample)
        layer_per_mp = xcf_layer_count_per_megapixel(sample)
        layers_per_dim = xcf_layers_per_dimension(sample)
        assert isinstance(dims, dict)
        assert isinstance(is_portrait, bool)
        assert layer_per_mp >= 0.0
        assert layers_per_dim >= 0.0

    def test_canvas_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_xcf_files():
            path = _ap(f)
            ratio = xcf_compression_ratio(path)
            size = xcf_file_size(path)
            dims = xcf_image_dimensions(path)
            is_portrait = xcf_is_portrait(path)
            layer_per_mp = xcf_layer_count_per_megapixel(path)
            layers_per_dim = xcf_layers_per_dimension(path)
            assert ratio >= 0.0, f"compression_ratio must be >= 0 for {f.name}"
            assert size >= 0, f"file_size must be >= 0 for {f.name}"
            assert isinstance(dims, dict), f"image_dimensions must be dict for {f.name}"
            assert isinstance(is_portrait, bool), f"is_portrait must be bool for {f.name}"
            assert layer_per_mp >= 0.0, f"layer_count_per_megapixel must be >= 0 for {f.name}"
            assert layers_per_dim >= 0.0, f"layers_per_dimension must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "compression_ratio": ratio,
                "file_size": size,
                "width": dims.get("width", 0),
                "height": dims.get("height", 0),
                "is_portrait": is_portrait,
                "layer_count_per_megapixel": layer_per_mp,
                "layers_per_dimension": layers_per_dim,
                "source_format": "xcf",
            })
        dest = tmp_path / "xcf-canvas.ndjson"
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
                "compression_ratio": xcf_compression_ratio(path),
                "file_size": xcf_file_size(path),
                "layer_count_per_megapixel": xcf_layer_count_per_megapixel(path),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["file_size"] == back["file_size"]
            assert orig["layer_count_per_megapixel"] == back["layer_count_per_megapixel"]

    def test_json_lines_valid(self, tmp_path):
        sample = _ap(next(_XCF_DIR.glob("*.xcf")))
        records = [{"file": "sample.xcf", "file_size": xcf_file_size(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_portrait_compression_export(self, tmp_path):
        records = []
        for f in _valid_xcf_files():
            path = _ap(f)
            is_portrait = xcf_is_portrait(path)
            ratio = xcf_compression_ratio(path)
            layers_per_dim = xcf_layers_per_dimension(path)
            assert isinstance(is_portrait, bool)
            assert ratio >= 0.0
            assert layers_per_dim >= 0.0
            records.append({
                "file": f.name,
                "is_portrait": is_portrait,
                "compression_ratio": ratio,
                "layers_per_dimension": layers_per_dim,
                "format": "xcf",
            })
        dest = tmp_path / "portrait-compression.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "xcf" for r in loaded)
        assert all(r["compression_ratio"] >= 0.0 for r in loaded)
