"""
tests/python/dogfood/test_dogfood_ppm_channel_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-25
Dogfood export: PPM parse -> channel/brightness analytics -> write as NDJSON -> verify.
Uses deeper PPM analytics: per-channel averages, dominant channel, brightness variance, etc.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ppm import (
    ppm_red_channel_average,
    ppm_blue_channel_average,
    ppm_green_channel_average,
    ppm_dominant_channel,
    ppm_brightness_variance,
    ppm_saturation_estimate,
    ppm_aspect_ratio,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_PPM_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"


class TestPpmChannelAnalyticsNdjsonExport:
    """PPM -> channel/brightness analytics -> NDJSON export -> roundtrip verification."""

    def test_channel_averages(self):
        sample = str(_PPM_DIR / "2x2-rgbw.ppm")
        r = ppm_red_channel_average(sample)
        g = ppm_green_channel_average(sample)
        b = ppm_blue_channel_average(sample)
        assert isinstance(r, (int, float))
        assert isinstance(g, (int, float))
        assert isinstance(b, (int, float))

    def test_dominant_channel(self):
        sample = str(_PPM_DIR / "1x1-red.ppm")
        dom = ppm_dominant_channel(sample)
        assert isinstance(dom, str)

    def test_channel_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in sorted(_PPM_DIR.glob("*.ppm")):
            records.append({
                "file": f.name,
                "red_avg": ppm_red_channel_average(str(f)),
                "green_avg": ppm_green_channel_average(str(f)),
                "blue_avg": ppm_blue_channel_average(str(f)),
                "dominant": ppm_dominant_channel(str(f)),
                "brightness_var": ppm_brightness_variance(str(f)),
                "saturation": ppm_saturation_estimate(str(f)),
                "aspect_ratio": ppm_aspect_ratio(str(f)),
                "source_format": "ppm",
            })
        dest = tmp_path / "ppm-channels.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in sorted(_PPM_DIR.glob("*.ppm")):
            records.append({
                "file": f.name,
                "red_avg": ppm_red_channel_average(str(f)),
                "dominant": ppm_dominant_channel(str(f)),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["dominant"] == back["dominant"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(_PPM_DIR / "1x1-red.ppm")
        records = [{"file": "1x1-red.ppm", "brightness_var": ppm_brightness_variance(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_saturation_export(self, tmp_path):
        records = []
        for f in sorted(_PPM_DIR.glob("*.ppm")):
            records.append({
                "file": f.name,
                "saturation": ppm_saturation_estimate(str(f)),
                "format": "ppm",
            })
        dest = tmp_path / "saturation.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "ppm" for r in loaded)
