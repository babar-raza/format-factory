"""
tests/python/dogfood/test_dogfood_qoi_grayscale_variance_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-32
Dogfood export: QOI parse -> grayscale/variance/channel analytics -> write as NDJSON -> verify.
Uses deeper QOI analytics: brightness_variance, total_brightness, min_max_brightness,
dominant_channel, red/green/blue channel averages, is_grayscale.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.qoi.qoi_parser import (
    qoi_brightness_variance,
    qoi_total_brightness,
    qoi_min_max_brightness,
    qoi_dominant_channel,
    qoi_red_channel_average,
    qoi_green_channel_average,
    qoi_blue_channel_average,
    qoi_is_grayscale,
    qoi_average_brightness,
    qoi_pixel_count,
)
from src.python.ndjson.ndjson_codec import write_ndjson, load_ndjson


_QOI_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"


def _ap(f):
    return os.path.abspath(str(f))


def _valid_qoi_files():
    return sorted(_QOI_DIR.glob("*.qoi"))


class TestQoiGrayscaleVarianceNdjsonExport:
    """QOI -> grayscale/variance analytics -> NDJSON export -> roundtrip verification."""

    def test_brightness_variance(self):
        sample = _ap(_QOI_DIR / "4x1-gradient.qoi")
        variance = qoi_brightness_variance(sample)
        assert isinstance(variance, float)
        assert variance >= 0.0

    def test_total_brightness_and_min_max(self):
        sample = _ap(_QOI_DIR / "4x1-gradient.qoi")
        total = qoi_total_brightness(sample)
        mm = qoi_min_max_brightness(sample)
        pixels = qoi_pixel_count(sample)
        assert total >= 0.0
        assert isinstance(mm, dict)
        assert pixels >= 1

    def test_grayscale_variance_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_qoi_files():
            path = _ap(f)
            variance = qoi_brightness_variance(path)
            total = qoi_total_brightness(path)
            mm = qoi_min_max_brightness(path)
            dom = qoi_dominant_channel(path)
            r = qoi_red_channel_average(path)
            g = qoi_green_channel_average(path)
            b = qoi_blue_channel_average(path)
            is_gray = qoi_is_grayscale(path)
            pixels = qoi_pixel_count(path)
            assert variance >= 0.0, f"brightness_variance must be >= 0 for {f.name}"
            assert total >= 0.0, f"total_brightness must be >= 0 for {f.name}"
            assert 0.0 <= r <= 255.0, f"red_avg out of range for {f.name}"
            assert 0.0 <= g <= 255.0, f"green_avg out of range for {f.name}"
            assert 0.0 <= b <= 255.0, f"blue_avg out of range for {f.name}"
            assert pixels >= 1, f"pixel_count must be >= 1 for {f.name}"
            records.append({
                "file": f.name,
                "brightness_variance": variance,
                "total_brightness": total,
                "min_max_brightness": mm,
                "dominant_channel": dom,
                "red_avg": r,
                "green_avg": g,
                "blue_avg": b,
                "is_grayscale": is_gray,
                "pixel_count": pixels,
                "source_format": "qoi",
            })
        dest = tmp_path / "qoi-grayscale-variance.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_qoi_files():
            path = _ap(f)
            records.append({
                "file": f.name,
                "dominant_channel": qoi_dominant_channel(path),
                "is_grayscale": qoi_is_grayscale(path),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["dominant_channel"] == back["dominant_channel"]
            assert orig["is_grayscale"] == back["is_grayscale"]

    def test_json_lines_valid(self, tmp_path):
        sample = _ap(_QOI_DIR / "4x1-gradient.qoi")
        records = [{"file": "4x1-gradient.qoi", "brightness_variance": qoi_brightness_variance(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_channel_averages_export(self, tmp_path):
        records = []
        for f in _valid_qoi_files():
            path = _ap(f)
            avg = qoi_average_brightness(path)
            r = qoi_red_channel_average(path)
            g = qoi_green_channel_average(path)
            b = qoi_blue_channel_average(path)
            assert avg >= 0.0, f"average_brightness must be >= 0 for {f.name}"
            assert 0.0 <= r <= 255.0, f"red_avg out of range for {f.name}"
            assert 0.0 <= g <= 255.0, f"green_avg out of range for {f.name}"
            assert 0.0 <= b <= 255.0, f"blue_avg out of range for {f.name}"
            records.append({
                "file": f.name,
                "average_brightness": avg,
                "red_avg": r,
                "green_avg": g,
                "blue_avg": b,
                "format": "qoi",
            })
        dest = tmp_path / "channel-avgs.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "qoi" for r in loaded)
        assert all(0.0 <= r["red_avg"] <= 255.0 for r in loaded)
