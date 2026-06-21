"""test_dogfood_qoi_analytics_gaps_ndjson_export.py

Dogfood export path: QOI analytics gap functions -> NDJSON.

Covers: qoi_normalized_brightness, qoi_min_brightness, qoi_above_mean_ratio,
qoi_green_blue_ratio, qoi_is_wide, qoi_max_brightness, qoi_total_rgb_sum.

Concrete values (1x1-red.qoi):
  normalized_brightness = 0.3333
  min_brightness        = 85.0
  above_mean_ratio      = 0.0
  green_blue_ratio      = 0.0
  is_wide               = False
  max_brightness        = 85.0
  total_rgb_sum         = 255

Concrete values (4x1-gradient.qoi):
  normalized_brightness = 0.5
  is_wide               = True
  max_brightness        = 255.0
  total_rgb_sum         = 1530

Sprint: product-deepening-ppm-qoi-analytics-gaps-dogfood-20260617
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.qoi.qoi_parser import (
    qoi_normalized_brightness,
    qoi_min_brightness,
    qoi_above_mean_ratio,
    qoi_green_blue_ratio,
    qoi_is_wide,
    qoi_max_brightness,
    qoi_total_rgb_sum,
)
from src.python.ndjson.ndjson_codec import write_ndjson

SAMPLES_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"
RED_1X1 = SAMPLES_DIR / "1x1-red.qoi"
BLACK_2X2 = SAMPLES_DIR / "2x2-black.qoi"
GRADIENT_4X1 = SAMPLES_DIR / "4x1-gradient.qoi"


def _export_qoi_gaps_record(path: Path) -> dict:
    return {
        "file": path.name,
        "normalized_brightness": qoi_normalized_brightness(path),
        "min_brightness": qoi_min_brightness(path),
        "above_mean_ratio": qoi_above_mean_ratio(path),
        "green_blue_ratio": qoi_green_blue_ratio(path),
        "is_wide": qoi_is_wide(path),
        "max_brightness": qoi_max_brightness(path),
        "total_rgb_sum": qoi_total_rgb_sum(path),
    }


class TestQoiAnalyticsGapsNdjsonExport:

    def test_red_normalized_brightness(self):
        rec = _export_qoi_gaps_record(RED_1X1)
        assert abs(rec["normalized_brightness"] - 0.3333) < 0.001

    def test_black_normalized_brightness_zero(self):
        rec = _export_qoi_gaps_record(BLACK_2X2)
        assert abs(rec["normalized_brightness"]) < 0.001

    def test_gradient_normalized_brightness_half(self):
        rec = _export_qoi_gaps_record(GRADIENT_4X1)
        assert abs(rec["normalized_brightness"] - 0.5) < 0.01

    def test_red_min_brightness(self):
        rec = _export_qoi_gaps_record(RED_1X1)
        assert abs(rec["min_brightness"] - 85.0) < 1.0

    def test_black_min_brightness_zero(self):
        rec = _export_qoi_gaps_record(BLACK_2X2)
        assert rec["min_brightness"] == 0.0

    def test_gradient_is_wide(self):
        rec = _export_qoi_gaps_record(GRADIENT_4X1)
        assert rec["is_wide"] is True

    def test_red_not_wide(self):
        rec = _export_qoi_gaps_record(RED_1X1)
        assert rec["is_wide"] is False

    def test_gradient_max_brightness(self):
        rec = _export_qoi_gaps_record(GRADIENT_4X1)
        assert abs(rec["max_brightness"] - 255.0) < 1.0

    def test_black_total_rgb_sum_zero(self):
        rec = _export_qoi_gaps_record(BLACK_2X2)
        assert rec["total_rgb_sum"] == 0

    def test_red_total_rgb_sum(self):
        rec = _export_qoi_gaps_record(RED_1X1)
        assert rec["total_rgb_sum"] == 255

    def test_record_has_all_keys(self):
        rec = _export_qoi_gaps_record(RED_1X1)
        for key in ["file", "normalized_brightness", "min_brightness",
                    "above_mean_ratio", "green_blue_ratio", "is_wide",
                    "max_brightness", "total_rgb_sum"]:
            assert key in rec

    def test_ndjson_export_two_files(self, tmp_path):
        records = [_export_qoi_gaps_record(RED_1X1), _export_qoi_gaps_record(GRADIENT_4X1)]
        out = tmp_path / "qoi_gap_analytics.ndjson"
        write_ndjson(records, str(out))
        lines = out.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 2
        for line in lines:
            parsed = json.loads(line)
            assert "total_rgb_sum" in parsed
