"""test_dogfood_xcf_analytics_gaps_ndjson_export.py

Dogfood export path: XCF analytics gap functions -> NDJSON.

Covers: xcf_image_type_code, xcf_file_header_overhead, xcf_version_number,
xcf_dimension_sum, xcf_pixel_per_layer_avg, xcf_canvas_aspect_ratio,
xcf_color_mode_name, xcf_total_pixels.

Concrete values (1x1-red-rgb.xcf):
  image_type_code     = 0
  file_header_overhead = 176
  version_number      = 11
  dimension_sum       = 2
  pixel_per_layer_avg = 1.0
  canvas_aspect_ratio = 1.0
  color_mode_name     = "RGB"
  total_pixels        = 1

Concrete values (2x2-gray.xcf):
  image_type_code     = 1
  dimension_sum       = 4
  pixel_per_layer_avg = 4.0
  color_mode_name     = "Grayscale"
  total_pixels        = 4

Sprint: product-deepening-xcf-analytics-gaps-dogfood-20260617
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf.xcf_parser import (
    xcf_image_type_code,
    xcf_file_header_overhead,
    xcf_version_number,
    xcf_dimension_sum,
    xcf_pixel_per_layer_avg,
    xcf_canvas_aspect_ratio,
    xcf_color_mode_name,
    xcf_total_pixels,
)
from src.python.ndjson.ndjson_codec import write_ndjson

SAMPLES_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED_1X1 = SAMPLES_DIR / "1x1-red-rgb.xcf"
BLUE_1X1 = SAMPLES_DIR / "1x1-rgba-blue.xcf"
GRAY_2X2 = SAMPLES_DIR / "2x2-gray.xcf"


def _export_xcf_gaps_record(path: Path) -> dict:
    return {
        "file": path.name,
        "image_type_code": xcf_image_type_code(path),
        "file_header_overhead": xcf_file_header_overhead(path),
        "version_number": xcf_version_number(path),
        "dimension_sum": xcf_dimension_sum(path),
        "pixel_per_layer_avg": xcf_pixel_per_layer_avg(path),
        "canvas_aspect_ratio": xcf_canvas_aspect_ratio(path),
        "color_mode_name": xcf_color_mode_name(path),
        "total_pixels": xcf_total_pixels(path),
    }


class TestXcfAnalyticsGapsNdjsonExport:

    def test_red_image_type_code_is_zero(self):
        rec = _export_xcf_gaps_record(RED_1X1)
        assert rec["image_type_code"] == 0

    def test_gray_image_type_code_is_one(self):
        rec = _export_xcf_gaps_record(GRAY_2X2)
        assert rec["image_type_code"] == 1

    def test_red_file_header_overhead_positive(self):
        rec = _export_xcf_gaps_record(RED_1X1)
        assert rec["file_header_overhead"] > 0

    def test_red_version_number_is_11(self):
        rec = _export_xcf_gaps_record(RED_1X1)
        assert rec["version_number"] == 11

    def test_red_dimension_sum_is_two(self):
        rec = _export_xcf_gaps_record(RED_1X1)
        assert rec["dimension_sum"] == 2

    def test_gray_dimension_sum_is_four(self):
        rec = _export_xcf_gaps_record(GRAY_2X2)
        assert rec["dimension_sum"] == 4

    def test_red_pixel_per_layer_avg_is_one(self):
        rec = _export_xcf_gaps_record(RED_1X1)
        assert abs(rec["pixel_per_layer_avg"] - 1.0) < 0.01

    def test_gray_pixel_per_layer_avg_is_four(self):
        rec = _export_xcf_gaps_record(GRAY_2X2)
        assert abs(rec["pixel_per_layer_avg"] - 4.0) < 0.01

    def test_red_color_mode_name_rgb(self):
        rec = _export_xcf_gaps_record(RED_1X1)
        assert rec["color_mode_name"] == "RGB"

    def test_gray_color_mode_name_grayscale(self):
        rec = _export_xcf_gaps_record(GRAY_2X2)
        assert rec["color_mode_name"] == "Grayscale"

    def test_record_has_all_keys(self):
        rec = _export_xcf_gaps_record(RED_1X1)
        for key in ["file", "image_type_code", "file_header_overhead", "version_number",
                    "dimension_sum", "pixel_per_layer_avg", "canvas_aspect_ratio",
                    "color_mode_name", "total_pixels"]:
            assert key in rec

    def test_ndjson_export_two_files(self, tmp_path):
        records = [_export_xcf_gaps_record(RED_1X1), _export_xcf_gaps_record(GRAY_2X2)]
        out = tmp_path / "xcf_gap_analytics.ndjson"
        write_ndjson(records, str(out))
        lines = out.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 2
        for line in lines:
            parsed = json.loads(line)
            assert "color_mode_name" in parsed
