"""
tests/python/dogfood/test_dogfood_ppm_blue_channel_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-67
Dogfood export: PPM parse -> blue channel analytics -> write as NDJSON -> verify.
Uses: ppm_row_count, ppm_blue_channel_sum, ppm_pixel_count,
ppm_aspect_ratio, ppm_is_grayscale, ppm_luminance_average.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ppm import (
    ppm_row_count,
    ppm_blue_channel_sum,
    ppm_pixel_count,
    ppm_aspect_ratio,
    ppm_is_grayscale,
    ppm_luminance_average,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_PPM_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"


def _valid_ppm_files():
    return sorted(_PPM_DIR.glob("*.ppm"))


class TestPpmBlueChannelAnalyticsNdjsonExport:
    """PPM -> blue channel analytics -> NDJSON export -> roundtrip verification."""

    def test_blue_channel_basics(self):
        sample = str(next(_PPM_DIR.glob("*.ppm")))
        row_count = ppm_row_count(sample)
        blue_sum = ppm_blue_channel_sum(sample)
        assert row_count >= 0
        assert blue_sum >= 0

    def test_geometry_basics(self):
        sample = str(next(_PPM_DIR.glob("*.ppm")))
        pixel_count = ppm_pixel_count(sample)
        aspect = ppm_aspect_ratio(sample)
        is_gray = ppm_is_grayscale(sample)
        assert pixel_count >= 0
        assert isinstance(aspect, float)
        assert isinstance(is_gray, bool)

    def test_blue_channel_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_ppm_files():
            path = str(f)
            row_count = ppm_row_count(path)
            blue_sum = ppm_blue_channel_sum(path)
            pixel_count = ppm_pixel_count(path)
            aspect = ppm_aspect_ratio(path)
            is_gray = ppm_is_grayscale(path)
            lum = ppm_luminance_average(path)
            assert row_count >= 0, f"ppm_row_count must be >= 0 for {f.name}"
            assert blue_sum >= 0, f"ppm_blue_channel_sum must be >= 0 for {f.name}"
            assert pixel_count >= 0, f"ppm_pixel_count must be >= 0 for {f.name}"
            assert isinstance(aspect, float), f"ppm_aspect_ratio must be float for {f.name}"
            assert isinstance(is_gray, bool), f"ppm_is_grayscale must be bool for {f.name}"
            assert isinstance(lum, float), f"ppm_luminance_average must be float for {f.name}"
            records.append({
                "file": f.name,
                "row_count": row_count,
                "blue_channel_sum": blue_sum,
                "pixel_count": pixel_count,
                "aspect_ratio": aspect,
                "is_grayscale": is_gray,
                "luminance_average": lum,
                "source_format": "ppm",
            })
        dest = tmp_path / "ppm-blue-channel.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_ppm_files():
            path = str(f)
            row_count = ppm_row_count(path)
            blue_sum = ppm_blue_channel_sum(path)
            records.append({
                "file": f.name,
                "row_count": row_count,
                "blue_channel_sum": blue_sum,
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["row_count"] == back["row_count"]
            assert orig["blue_channel_sum"] == back["blue_channel_sum"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(next(_PPM_DIR.glob("*.ppm")))
        row_count = ppm_row_count(sample)
        blue_sum = ppm_blue_channel_sum(sample)
        records = [{"file": "sample.ppm", "row_count": row_count, "blue_channel_sum": blue_sum}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_blue_grayscale_export(self, tmp_path):
        records = []
        for f in _valid_ppm_files():
            path = str(f)
            row_count = ppm_row_count(path)
            blue_sum = ppm_blue_channel_sum(path)
            is_gray = ppm_is_grayscale(path)
            lum = ppm_luminance_average(path)
            assert row_count >= 0
            assert blue_sum >= 0
            assert isinstance(is_gray, bool)
            assert isinstance(lum, float)
            records.append({
                "file": f.name,
                "row_count": row_count,
                "blue_channel_sum": blue_sum,
                "is_grayscale": is_gray,
                "luminance_average": lum,
                "format": "ppm",
            })
        dest = tmp_path / "blue-grayscale.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "ppm" for r in loaded)
        assert all(isinstance(r["is_grayscale"], bool) for r in loaded)
