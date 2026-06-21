"""test_dogfood_ppm_analytics_gaps_ndjson_export.py

Dogfood export path: PPM analytics gap functions -> NDJSON.

Covers: ppm_blue_ratio, ppm_is_bright, ppm_maxval,
ppm_normalized_brightness, ppm_area.

Concrete values (1x1-red.ppm):
  blue_ratio            = 0.000
  is_bright             = False
  maxval                = 255
  normalized_brightness = 0.333
  area                  = 1

Concrete values (2x2-rgbw.ppm):
  blue_ratio            = 0.333
  area                  = 4

Sprint: product-deepening-ppm-qoi-analytics-gaps-dogfood-20260617
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ppm.ppm_parser import (
    ppm_blue_ratio,
    ppm_is_bright,
    ppm_maxval,
    ppm_normalized_brightness,
    ppm_area,
)
from src.python.ndjson.ndjson_codec import write_ndjson

SAMPLES_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"
RED_1X1 = SAMPLES_DIR / "1x1-red.ppm"
RGBW_2X2 = SAMPLES_DIR / "2x2-rgbw.ppm"
GRADIENT_3X1 = SAMPLES_DIR / "3x1-gradient.ppm"


def _export_ppm_gaps_record(path: Path) -> dict:
    return {
        "file": path.name,
        "blue_ratio": ppm_blue_ratio(path),
        "is_bright": ppm_is_bright(path),
        "maxval": ppm_maxval(path),
        "normalized_brightness": ppm_normalized_brightness(path),
        "area": ppm_area(path),
    }


class TestPpmAnalyticsGapsNdjsonExport:

    def test_red_blue_ratio_is_zero(self):
        rec = _export_ppm_gaps_record(RED_1X1)
        assert abs(rec["blue_ratio"]) < 0.001

    def test_rgbw_blue_ratio_nonzero(self):
        rec = _export_ppm_gaps_record(RGBW_2X2)
        assert rec["blue_ratio"] > 0.0

    def test_red_is_not_bright(self):
        rec = _export_ppm_gaps_record(RED_1X1)
        assert rec["is_bright"] is False

    def test_rgbw_is_not_bright(self):
        rec = _export_ppm_gaps_record(RGBW_2X2)
        assert rec["is_bright"] is False

    def test_red_maxval_is_255(self):
        rec = _export_ppm_gaps_record(RED_1X1)
        assert rec["maxval"] == 255

    def test_rgbw_maxval_is_255(self):
        rec = _export_ppm_gaps_record(RGBW_2X2)
        assert rec["maxval"] == 255

    def test_red_normalized_brightness(self):
        rec = _export_ppm_gaps_record(RED_1X1)
        assert abs(rec["normalized_brightness"] - 0.333) < 0.01

    def test_rgbw_normalized_brightness(self):
        rec = _export_ppm_gaps_record(RGBW_2X2)
        assert abs(rec["normalized_brightness"] - 0.5) < 0.01

    def test_red_area_is_one(self):
        rec = _export_ppm_gaps_record(RED_1X1)
        assert rec["area"] == 1

    def test_rgbw_area_is_four(self):
        rec = _export_ppm_gaps_record(RGBW_2X2)
        assert rec["area"] == 4

    def test_record_has_all_keys(self):
        rec = _export_ppm_gaps_record(RED_1X1)
        for key in ["file", "blue_ratio", "is_bright", "maxval",
                    "normalized_brightness", "area"]:
            assert key in rec

    def test_ndjson_export_two_files(self, tmp_path):
        records = [_export_ppm_gaps_record(RED_1X1), _export_ppm_gaps_record(RGBW_2X2)]
        out = tmp_path / "ppm_gap_analytics.ndjson"
        write_ndjson(records, str(out))
        lines = out.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 2
        for line in lines:
            parsed = json.loads(line)
            assert "normalized_brightness" in parsed
