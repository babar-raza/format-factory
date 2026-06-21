"""test_dogfood_ppm_remaining_gaps_ndjson_export.py

Dogfood export path: PPM remaining analytics gap functions -> NDJSON.

Covers: ppm_cool_pixel_count, ppm_dark_pixel_ratio, ppm_is_dark, ppm_warm_pixel_count,
        ppm_min_channel_avg, ppm_max_pixel_brightness, ppm_pure_color_count,
        ppm_max_channel_avg, ppm_luminance_sum, ppm_grayscale_pixel_count,
        ppm_neutral_pixel_count, ppm_is_monochrome, ppm_is_square, ppm_is_landscape,
        ppm_max_dimension

Concrete values:
  1x1-red.ppm: cool_pixel_count=0, dark_pixel_ratio=1.0, is_dark=True, warm_pixel_count=1,
               min_channel_avg=0.0, max_pixel_brightness=85.0, pure_color_count=1,
               luminance_sum=54.21, grayscale_pixel_count=0, is_monochrome=True, is_square=True,
               max_dimension=1
  2x2-rgbw.ppm: cool_pixel_count=1, dark_pixel_ratio=0.75, warm_pixel_count=1,
                pure_color_count=3, luminance_sum=510.0, is_monochrome=False, max_dimension=2

Sprint: product-deepening-ppm-remaining-gaps-dogfood-20260617
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ppm.ppm_parser import (
    ppm_cool_pixel_count,
    ppm_dark_pixel_ratio,
    ppm_is_dark,
    ppm_is_landscape,
    ppm_is_monochrome,
    ppm_is_square,
    ppm_grayscale_pixel_count,
    ppm_luminance_sum,
    ppm_max_channel_avg,
    ppm_max_dimension,
    ppm_max_pixel_brightness,
    ppm_min_channel_avg,
    ppm_neutral_pixel_count,
    ppm_pure_color_count,
    ppm_warm_pixel_count,
)
from src.python.ndjson.ndjson_codec import write_ndjson

PPM_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"
PPM_RED = PPM_DIR / "1x1-red.ppm"
PPM_RGBW = PPM_DIR / "2x2-rgbw.ppm"


class TestPpmRemainingGapsNdjsonExport:

    def test_red_cool_pixel_count_zero(self):
        assert ppm_cool_pixel_count(PPM_RED) == 0

    def test_rgbw_cool_pixel_count_one(self):
        assert ppm_cool_pixel_count(PPM_RGBW) == 1

    def test_red_dark_pixel_ratio_one(self):
        assert abs(ppm_dark_pixel_ratio(PPM_RED) - 1.0) < 0.01

    def test_rgbw_dark_pixel_ratio(self):
        assert abs(ppm_dark_pixel_ratio(PPM_RGBW) - 0.75) < 0.01

    def test_red_is_dark(self):
        assert ppm_is_dark(PPM_RED) is True

    def test_red_warm_pixel_count_one(self):
        assert ppm_warm_pixel_count(PPM_RED) == 1

    def test_rgbw_warm_pixel_count_one(self):
        assert ppm_warm_pixel_count(PPM_RGBW) == 1

    def test_red_min_channel_avg_zero(self):
        assert abs(ppm_min_channel_avg(PPM_RED)) < 0.01

    def test_rgbw_min_channel_avg(self):
        val = ppm_min_channel_avg(PPM_RGBW)
        assert val > 0.0

    def test_red_max_pixel_brightness(self):
        assert abs(ppm_max_pixel_brightness(PPM_RED) - 85.0) < 1.0

    def test_rgbw_max_pixel_brightness(self):
        assert abs(ppm_max_pixel_brightness(PPM_RGBW) - 255.0) < 1.0

    def test_red_pure_color_count(self):
        assert ppm_pure_color_count(PPM_RED) == 1

    def test_rgbw_pure_color_count(self):
        assert ppm_pure_color_count(PPM_RGBW) >= 2

    def test_red_max_channel_avg(self):
        assert abs(ppm_max_channel_avg(PPM_RED) - 255.0) < 1.0

    def test_red_luminance_sum_positive(self):
        assert ppm_luminance_sum(PPM_RED) > 0.0

    def test_rgbw_luminance_sum_greater(self):
        assert ppm_luminance_sum(PPM_RGBW) > ppm_luminance_sum(PPM_RED)

    def test_red_grayscale_pixel_count_zero(self):
        assert ppm_grayscale_pixel_count(PPM_RED) == 0

    def test_rgbw_has_grayscale_pixel(self):
        assert ppm_grayscale_pixel_count(PPM_RGBW) >= 1

    def test_red_neutral_pixel_count_zero(self):
        assert ppm_neutral_pixel_count(PPM_RED) == 0

    def test_red_is_monochrome(self):
        assert ppm_is_monochrome(PPM_RED) is True

    def test_rgbw_not_monochrome(self):
        assert ppm_is_monochrome(PPM_RGBW) is False

    def test_red_is_square(self):
        assert ppm_is_square(PPM_RED) is True

    def test_red_not_landscape(self):
        assert ppm_is_landscape(PPM_RED) is False

    def test_red_max_dimension_one(self):
        assert ppm_max_dimension(PPM_RED) == 1

    def test_rgbw_max_dimension_two(self):
        assert ppm_max_dimension(PPM_RGBW) == 2

    def test_ndjson_export_ppm_records(self, tmp_path):
        records = [
            {
                "file": PPM_RED.name,
                "pure_color_count": ppm_pure_color_count(PPM_RED),
                "is_monochrome": ppm_is_monochrome(PPM_RED),
                "max_dimension": ppm_max_dimension(PPM_RED),
            },
            {
                "file": PPM_RGBW.name,
                "pure_color_count": ppm_pure_color_count(PPM_RGBW),
                "is_monochrome": ppm_is_monochrome(PPM_RGBW),
                "max_dimension": ppm_max_dimension(PPM_RGBW),
            },
        ]
        out = tmp_path / "ppm_remaining.ndjson"
        write_ndjson(records, str(out))
        lines = out.read_text(encoding="utf-8").strip().splitlines()
        assert json.loads(lines[0])["is_monochrome"] is True
        assert json.loads(lines[1])["is_monochrome"] is False
        assert json.loads(lines[1])["max_dimension"] == 2
