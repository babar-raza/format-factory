"""
tests/python/dogfood/test_dogfood_ppm_dark_red_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-63
Dogfood export: PPM parse -> dark/red analytics -> write as NDJSON -> verify.
Uses: ppm_is_dark, ppm_red_channel_sum, ppm_pixel_count, ppm_aspect_ratio,
ppm_brightness_variance, ppm_is_grayscale.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ppm import (
    ppm_is_dark,
    ppm_red_channel_sum,
    ppm_pixel_count,
    ppm_aspect_ratio,
    ppm_brightness_variance,
    ppm_is_grayscale,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_PPM_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"


def _valid_ppm_files():
    return sorted(_PPM_DIR.glob("*.ppm"))


class TestPpmDarkRedAnalyticsNdjsonExport:
    """PPM -> dark/red analytics -> NDJSON export -> roundtrip verification."""

    def test_is_dark_and_red_channel_sum(self):
        sample = str(next(_PPM_DIR.glob("*.ppm")))
        dark = ppm_is_dark(sample)
        red_sum = ppm_red_channel_sum(sample)
        assert isinstance(dark, bool)
        assert red_sum >= 0

    def test_brightness_and_grayscale(self):
        sample = str(next(_PPM_DIR.glob("*.ppm")))
        px_count = ppm_pixel_count(sample)
        aspect = ppm_aspect_ratio(sample)
        variance = ppm_brightness_variance(sample)
        grayscale = ppm_is_grayscale(sample)
        assert px_count >= 0
        assert isinstance(aspect, float)
        assert isinstance(variance, float)
        assert isinstance(grayscale, bool)

    def test_dark_red_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_ppm_files():
            path = str(f)
            dark = ppm_is_dark(path)
            red_sum = ppm_red_channel_sum(path)
            px_count = ppm_pixel_count(path)
            aspect = ppm_aspect_ratio(path)
            variance = ppm_brightness_variance(path)
            grayscale = ppm_is_grayscale(path)
            assert isinstance(dark, bool), f"ppm_is_dark must be bool for {f.name}"
            assert red_sum >= 0, f"ppm_red_channel_sum must be >= 0 for {f.name}"
            assert px_count >= 0, f"ppm_pixel_count must be >= 0 for {f.name}"
            assert isinstance(aspect, float), f"ppm_aspect_ratio must be float for {f.name}"
            assert isinstance(variance, float), f"ppm_brightness_variance must be float for {f.name}"
            assert isinstance(grayscale, bool), f"ppm_is_grayscale must be bool for {f.name}"
            records.append({
                "file": f.name,
                "is_dark": dark,
                "red_channel_sum": red_sum,
                "pixel_count": px_count,
                "aspect_ratio": aspect,
                "brightness_variance": variance,
                "is_grayscale": grayscale,
                "source_format": "ppm",
            })
        dest = tmp_path / "ppm-dark-red.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_ppm_files():
            path = str(f)
            dark = ppm_is_dark(path)
            red_sum = ppm_red_channel_sum(path)
            records.append({
                "file": f.name,
                "is_dark": dark,
                "red_channel_sum": red_sum,
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["is_dark"] == back["is_dark"]
            assert orig["red_channel_sum"] == back["red_channel_sum"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(next(_PPM_DIR.glob("*.ppm")))
        dark = ppm_is_dark(sample)
        records = [{"file": "sample.ppm", "is_dark": dark}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_dark_variance_export(self, tmp_path):
        records = []
        for f in _valid_ppm_files():
            path = str(f)
            dark = ppm_is_dark(path)
            red_sum = ppm_red_channel_sum(path)
            variance = ppm_brightness_variance(path)
            assert isinstance(dark, bool)
            assert red_sum >= 0
            assert isinstance(variance, float)
            records.append({
                "file": f.name,
                "is_dark": dark,
                "red_channel_sum": red_sum,
                "brightness_variance": variance,
                "format": "ppm",
            })
        dest = tmp_path / "dark-variance.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "ppm" for r in loaded)
        assert all(r["red_channel_sum"] >= 0 for r in loaded)
