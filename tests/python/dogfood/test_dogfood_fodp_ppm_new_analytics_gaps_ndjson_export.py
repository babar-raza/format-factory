"""test_dogfood_fodp_ppm_new_analytics_gaps_ndjson_export.py

Dogfood export path: FODP + PPM new analytics gap functions -> NDJSON.

Covers FODP: fodp_avg_sentence_length, fodp_avg_text_length, fodp_avg_title_words,
fodp_has_multi_slide, fodp_has_numeric_content, fodp_is_nonempty.

Covers PPM: ppm_border_brightness, ppm_color_variance, ppm_red_ratio,
ppm_green_ratio, ppm_pixel_brightness_range.

Concrete FODP values (minimal-presentation.fodp):
  avg_sentence_length = 5.0
  has_multi_slide     = False
  is_nonempty         = True

Concrete PPM values (1x1-red.ppm):
  border_brightness    = 85.0
  color_variance       = 0.0
  red_ratio            = 1.0
  green_ratio          = 0.0
  pixel_brightness_range = 0.0

Sprint: product-deepening-fodp-ppm-new-analytics-gaps-dogfood-20260617
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodp.fodp_codec import (
    fodp_avg_sentence_length,
    fodp_avg_text_length,
    fodp_avg_title_words,
    fodp_has_multi_slide,
    fodp_has_numeric_content,
    fodp_is_nonempty,
)
from src.python.ppm.ppm_parser import (
    ppm_border_brightness,
    ppm_color_variance,
    ppm_red_ratio,
    ppm_green_ratio,
    ppm_pixel_brightness_range,
)
from src.python.ndjson.ndjson_codec import write_ndjson

FODP_DIR = _REPO / "samples" / "by-format" / "fodp"
PPM_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"

FODP_MINIMAL = FODP_DIR / "minimal-presentation.fodp"
FODP_TWO_SLIDES = FODP_DIR / "two-slides-basic.fodp"
FODP_TITLE_ONLY = FODP_DIR / "title-only.fodp"
PPM_RED = PPM_DIR / "1x1-red.ppm"
PPM_RGBW = PPM_DIR / "2x2-rgbw.ppm"


def _export_fodp_ppm_record(fodp_path: Path, ppm_path: Path) -> dict:
    return {
        "fodp_file": fodp_path.name,
        "ppm_file": ppm_path.name,
        "avg_sentence_length": fodp_avg_sentence_length(fodp_path),
        "avg_text_length": fodp_avg_text_length(fodp_path),
        "has_multi_slide": fodp_has_multi_slide(fodp_path),
        "is_nonempty": fodp_is_nonempty(fodp_path),
        "ppm_border_brightness": ppm_border_brightness(ppm_path),
        "ppm_color_variance": ppm_color_variance(ppm_path),
        "ppm_red_ratio": ppm_red_ratio(ppm_path),
        "ppm_green_ratio": ppm_green_ratio(ppm_path),
        "ppm_pixel_brightness_range": ppm_pixel_brightness_range(ppm_path),
    }


class TestFodpPpmNewAnalyticsGapsNdjsonExport:

    def test_fodp_minimal_avg_sentence_length(self):
        assert abs(fodp_avg_sentence_length(FODP_MINIMAL) - 5.0) < 0.1

    def test_fodp_minimal_not_multi_slide(self):
        assert fodp_has_multi_slide(FODP_MINIMAL) is False

    def test_fodp_two_slides_is_multi_slide(self):
        assert fodp_has_multi_slide(FODP_TWO_SLIDES) is True

    def test_fodp_minimal_is_nonempty(self):
        assert fodp_is_nonempty(FODP_MINIMAL) is True

    def test_fodp_title_only_not_nonempty(self):
        assert fodp_is_nonempty(FODP_TITLE_ONLY) is False

    def test_ppm_red_border_brightness(self):
        assert abs(ppm_border_brightness(PPM_RED) - 85.0) < 1.0

    def test_ppm_red_color_variance_zero(self):
        assert abs(ppm_color_variance(PPM_RED)) < 0.01

    def test_ppm_red_ratio_is_one(self):
        assert abs(ppm_red_ratio(PPM_RED) - 1.0) < 0.001

    def test_ppm_red_green_ratio_zero(self):
        assert abs(ppm_green_ratio(PPM_RED)) < 0.001

    def test_ppm_red_pixel_brightness_range_zero(self):
        assert abs(ppm_pixel_brightness_range(PPM_RED)) < 0.001

    def test_ppm_rgbw_red_ratio_third(self):
        assert abs(ppm_red_ratio(PPM_RGBW) - 0.333) < 0.01

    def test_ndjson_export_combined_record(self, tmp_path):
        records = [_export_fodp_ppm_record(FODP_MINIMAL, PPM_RED)]
        out = tmp_path / "fodp_ppm_analytics.ndjson"
        write_ndjson(records, str(out))
        parsed = json.loads(out.read_text(encoding="utf-8").strip())
        assert "has_multi_slide" in parsed
        assert "ppm_red_ratio" in parsed
