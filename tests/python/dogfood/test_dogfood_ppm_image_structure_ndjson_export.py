"""
tests/python/dogfood/test_dogfood_ppm_image_structure_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-41
Dogfood export: PPM parse -> image structure analytics -> write as NDJSON -> verify.
Uses: ppm_pixel_count, ppm_is_binary, ppm_min_max_brightness, ppm_is_grayscale,
ppm_channel_range, ppm_unique_color_count.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ppm import (
    ppm_pixel_count,
    ppm_is_binary,
    ppm_min_max_brightness,
    ppm_is_grayscale,
    ppm_channel_range,
    ppm_unique_color_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_PPM_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"


def _valid_ppm_files():
    return sorted(_PPM_DIR.glob("*.ppm"))


class TestPpmImageStructureNdjsonExport:
    """PPM -> image structure analytics -> NDJSON export -> roundtrip verification."""

    def test_pixel_count_and_binary(self):
        sample = str(_PPM_DIR / "1x1-red.ppm")
        count = ppm_pixel_count(sample)
        is_bin = ppm_is_binary(sample)
        assert count >= 0
        assert isinstance(is_bin, bool)

    def test_grayscale_and_brightness(self):
        sample = str(_PPM_DIR / "1x1-red.ppm")
        is_gray = ppm_is_grayscale(sample)
        mm = ppm_min_max_brightness(sample)
        assert isinstance(is_gray, bool)
        assert isinstance(mm, dict)
        assert "min" in mm and "max" in mm
        assert mm["min"] <= mm["max"]

    def test_image_structure_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_ppm_files():
            path = str(f)
            count = ppm_pixel_count(path)
            is_bin = ppm_is_binary(path)
            mm = ppm_min_max_brightness(path)
            is_gray = ppm_is_grayscale(path)
            ch_range = ppm_channel_range(path)
            unique_colors = ppm_unique_color_count(path)
            assert count >= 0, f"pixel_count must be >= 0 for {f.name}"
            assert isinstance(is_bin, bool), f"is_binary must be bool for {f.name}"
            assert isinstance(mm, dict), f"min_max_brightness must be dict for {f.name}"
            assert mm["min"] <= mm["max"], f"min <= max brightness for {f.name}"
            assert isinstance(is_gray, bool), f"is_grayscale must be bool for {f.name}"
            assert isinstance(ch_range, dict), f"channel_range must be dict for {f.name}"
            assert unique_colors >= 0, f"unique_color_count must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "pixel_count": count,
                "is_binary": is_bin,
                "min_brightness": mm["min"],
                "max_brightness": mm["max"],
                "is_grayscale": is_gray,
                "unique_colors": unique_colors,
                "source_format": "ppm",
            })
        dest = tmp_path / "ppm-image-structure.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_ppm_files():
            path = str(f)
            records.append({
                "file": f.name,
                "pixel_count": ppm_pixel_count(path),
                "is_grayscale": ppm_is_grayscale(path),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["pixel_count"] == back["pixel_count"]
            assert orig["is_grayscale"] == back["is_grayscale"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(_PPM_DIR / "1x1-red.ppm")
        records = [{"file": "1x1-red.ppm", "pixel_count": ppm_pixel_count(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_brightness_structure_export(self, tmp_path):
        records = []
        for f in _valid_ppm_files():
            path = str(f)
            mm = ppm_min_max_brightness(path)
            is_gray = ppm_is_grayscale(path)
            count = ppm_pixel_count(path)
            assert isinstance(mm, dict)
            assert mm["min"] <= mm["max"]
            assert isinstance(is_gray, bool)
            assert count >= 0
            records.append({
                "file": f.name,
                "min_brightness": mm["min"],
                "max_brightness": mm["max"],
                "is_grayscale": is_gray,
                "pixel_count": count,
                "format": "ppm",
            })
        dest = tmp_path / "brightness-structure.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "ppm" for r in loaded)
        assert all(r["min_brightness"] <= r["max_brightness"] for r in loaded)
