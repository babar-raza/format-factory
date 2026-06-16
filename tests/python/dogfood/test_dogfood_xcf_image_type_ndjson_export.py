"""
tests/python/dogfood/test_dogfood_xcf_image_type_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-34
Dogfood export: XCF parse -> image type/color model analytics -> write as NDJSON -> verify.
Uses: xcf_is_rgb, xcf_is_grayscale, xcf_is_indexed, xcf_version, xcf_image_type_name,
xcf_pixel_count, xcf_is_square, xcf_aspect_ratio.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf.xcf_parser import (
    xcf_is_rgb,
    xcf_is_grayscale,
    xcf_is_indexed,
    xcf_version,
    xcf_image_type_name,
    xcf_pixel_count,
    xcf_is_square,
    xcf_aspect_ratio,
    xcf_width,
    xcf_height,
)
from src.python.ndjson.ndjson_codec import write_ndjson, load_ndjson


_XCF_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"


def _ap(f):
    return os.path.abspath(str(f))


def _valid_xcf_files():
    return sorted(_XCF_DIR.glob("*.xcf"))


class TestXcfImageTypeNdjsonExport:
    """XCF -> image type/color model analytics -> NDJSON export -> roundtrip verification."""

    def test_color_model_flags(self):
        sample = _ap(_XCF_DIR / "1x1-red-rgb.xcf")
        is_rgb = xcf_is_rgb(sample)
        is_gray = xcf_is_grayscale(sample)
        is_idx = xcf_is_indexed(sample)
        assert isinstance(is_rgb, bool)
        assert isinstance(is_gray, bool)
        assert isinstance(is_idx, bool)

    def test_image_type_and_version(self):
        sample = _ap(_XCF_DIR / "1x1-red-rgb.xcf")
        ver = xcf_version(sample)
        type_name = xcf_image_type_name(sample)
        pixels = xcf_pixel_count(sample)
        assert isinstance(ver, str)
        assert len(ver) > 0
        assert isinstance(type_name, str)
        assert pixels >= 1

    def test_image_type_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_xcf_files():
            path = _ap(f)
            is_rgb = xcf_is_rgb(path)
            is_gray = xcf_is_grayscale(path)
            is_idx = xcf_is_indexed(path)
            ver = xcf_version(path)
            type_name = xcf_image_type_name(path)
            pixels = xcf_pixel_count(path)
            is_sq = xcf_is_square(path)
            ar = xcf_aspect_ratio(path)
            w = xcf_width(path)
            h = xcf_height(path)
            assert pixels >= 1, f"pixel_count must be >= 1 for {f.name}"
            assert ar > 0.0, f"aspect_ratio must be > 0 for {f.name}"
            assert w >= 1, f"width must be >= 1 for {f.name}"
            assert h >= 1, f"height must be >= 1 for {f.name}"
            # exactly one color model should be True
            model_count = sum([is_rgb, is_gray, is_idx])
            assert model_count <= 1, f"at most one color model true for {f.name}"
            records.append({
                "file": f.name,
                "is_rgb": is_rgb,
                "is_grayscale": is_gray,
                "is_indexed": is_idx,
                "version": ver,
                "image_type": type_name,
                "pixel_count": pixels,
                "is_square": is_sq,
                "aspect_ratio": ar,
                "width": w,
                "height": h,
                "source_format": "xcf",
            })
        dest = tmp_path / "xcf-image-type.ndjson"
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
                "image_type": xcf_image_type_name(path),
                "pixel_count": xcf_pixel_count(path),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["image_type"] == back["image_type"]
            assert orig["pixel_count"] == back["pixel_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = _ap(_XCF_DIR / "1x1-red-rgb.xcf")
        records = [{"file": "1x1-red-rgb.xcf", "version": xcf_version(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_color_model_export(self, tmp_path):
        records = []
        for f in _valid_xcf_files():
            path = _ap(f)
            records.append({
                "file": f.name,
                "is_rgb": xcf_is_rgb(path),
                "is_grayscale": xcf_is_grayscale(path),
                "image_type": xcf_image_type_name(path),
                "format": "xcf",
            })
        dest = tmp_path / "color-model.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "xcf" for r in loaded)
        assert all(isinstance(r["is_rgb"], bool) for r in loaded)
        assert all(isinstance(r["is_grayscale"], bool) for r in loaded)
