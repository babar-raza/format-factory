"""test_dogfood_pbm_pgm_xcf_remaining_gaps_ndjson_export.py

Dogfood export path: PBM + PGM + XCF remaining analytics gap functions -> NDJSON.

Covers PBM: pbm_corner_black_count, pbm_is_wider_than_tall, pbm_row_black_variance,
            pbm_row_uniformity
Covers PGM: pgm_brightness_variance, pgm_entropy, pgm_median_brightness, pgm_min_brightness,
            pgm_brightness_histogram
Covers XCF: xcf_bytes_per_pixel, xcf_is_high_res, xcf_layers_per_pixel

Concrete values:
  PBM 1x1-black: corner_black_count=4, is_wider_than_tall=False, row_uniformity=1.0
  PBM 2x2-checker: corner_black_count=2, is_wider_than_tall=False, row_black_variance=0.0
  PBM 3x2-pattern: is_wider_than_tall=True, row_black_variance=0.25
  PGM 1x1-white: brightness_variance=0.0, entropy=0.0, median=255.0, min=255
  PGM 2x2-gradient: brightness_variance=9031.25, entropy=2.0, median=127.5, min=0
  XCF 1x1-red-rgb: bytes_per_pixel=177.0, is_high_res=False, layers_per_pixel=1.0
  XCF 2x2-gray: bytes_per_pixel=44.5, layers_per_pixel=0.25

Sprint: product-deepening-pbm-pgm-xcf-remaining-gaps-dogfood-20260617
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pbm.pbm_parser import (
    pbm_corner_black_count,
    pbm_is_wider_than_tall,
    pbm_row_black_variance,
    pbm_row_uniformity,
)
from src.python.pgm.pgm_parser import (
    pgm_brightness_variance,
    pgm_brightness_histogram,
    pgm_entropy,
    pgm_median_brightness,
    pgm_min_brightness,
)
from src.python.xcf.xcf_parser import (
    xcf_bytes_per_pixel,
    xcf_is_high_res,
    xcf_layers_per_pixel,
)
from src.python.ndjson.ndjson_codec import write_ndjson

PBM_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"
PGM_DIR = (_REPO / "samples" / "by-format" / "pgm" / "valid").resolve()
XCF_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"

PBM_BLACK = PBM_DIR / "1x1-black.pbm"
PBM_CHECKER = PBM_DIR / "2x2-checker.pbm"
PBM_PATTERN = PBM_DIR / "3x2-pattern.pbm"
PGM_WHITE = (PGM_DIR / "1x1-white.pgm").resolve()
PGM_GRADIENT = (PGM_DIR / "2x2-gradient.pgm").resolve()
PGM_RAMP = (PGM_DIR / "3x1-ramp.pgm").resolve()
XCF_RED = XCF_DIR / "1x1-red-rgb.xcf"
XCF_GRAY = XCF_DIR / "2x2-gray.xcf"


class TestPbmPgmXcfRemainingGapsNdjsonExport:

    # PBM tests
    def test_pbm_black_corner_count_four(self):
        assert pbm_corner_black_count(PBM_BLACK) == 4

    def test_pbm_checker_corner_count_two(self):
        assert pbm_corner_black_count(PBM_CHECKER) == 2

    def test_pbm_black_not_wider_than_tall(self):
        assert pbm_is_wider_than_tall(PBM_BLACK) is False

    def test_pbm_pattern_is_wider_than_tall(self):
        assert pbm_is_wider_than_tall(PBM_PATTERN) is True

    def test_pbm_checker_row_black_variance_zero(self):
        assert abs(pbm_row_black_variance(PBM_CHECKER)) < 0.01

    def test_pbm_pattern_row_black_variance_positive(self):
        assert pbm_row_black_variance(PBM_PATTERN) > 0.0

    def test_pbm_black_row_uniformity_one(self):
        assert abs(pbm_row_uniformity(PBM_BLACK) - 1.0) < 0.01

    def test_pbm_checker_row_uniformity_zero(self):
        assert abs(pbm_row_uniformity(PBM_CHECKER)) < 0.01

    # PGM tests
    def test_pgm_white_brightness_variance_zero(self):
        assert abs(pgm_brightness_variance(PGM_WHITE)) < 0.01

    def test_pgm_gradient_brightness_variance_positive(self):
        assert pgm_brightness_variance(PGM_GRADIENT) > 1000.0

    def test_pgm_white_entropy_zero(self):
        assert abs(pgm_entropy(PGM_WHITE)) < 0.01

    def test_pgm_gradient_entropy_two(self):
        assert abs(pgm_entropy(PGM_GRADIENT) - 2.0) < 0.01

    def test_pgm_white_median_brightness(self):
        assert abs(pgm_median_brightness(PGM_WHITE) - 255.0) < 1.0

    def test_pgm_gradient_median_brightness(self):
        val = pgm_median_brightness(PGM_GRADIENT)
        assert 100.0 < val < 200.0

    def test_pgm_white_min_brightness(self):
        assert pgm_min_brightness(PGM_WHITE) == 255

    def test_pgm_gradient_min_brightness_zero(self):
        assert pgm_min_brightness(PGM_GRADIENT) == 0

    def test_pgm_white_brightness_histogram_is_list(self):
        hist = pgm_brightness_histogram(PGM_WHITE)
        assert isinstance(hist, list)
        assert len(hist) > 0

    def test_pgm_gradient_brightness_histogram_is_list(self):
        hist = pgm_brightness_histogram(PGM_GRADIENT)
        assert isinstance(hist, list)
        assert len(hist) > 0

    # XCF tests
    def test_xcf_red_bytes_per_pixel(self):
        assert xcf_bytes_per_pixel(XCF_RED) > 0.0

    def test_xcf_gray_bytes_per_pixel_less(self):
        assert xcf_bytes_per_pixel(XCF_GRAY) < xcf_bytes_per_pixel(XCF_RED)

    def test_xcf_red_not_high_res(self):
        assert xcf_is_high_res(XCF_RED) is False

    def test_xcf_red_layers_per_pixel_one(self):
        assert abs(xcf_layers_per_pixel(XCF_RED) - 1.0) < 0.01

    def test_xcf_gray_layers_per_pixel_quarter(self):
        assert abs(xcf_layers_per_pixel(XCF_GRAY) - 0.25) < 0.01

    def test_ndjson_export_pgm_record(self, tmp_path):
        records = [{
            "file": PGM_GRADIENT.name,
            "min_brightness": pgm_min_brightness(PGM_GRADIENT),
            "entropy": pgm_entropy(PGM_GRADIENT),
            "brightness_variance": pgm_brightness_variance(PGM_GRADIENT),
        }]
        out = tmp_path / "pgm_remaining.ndjson"
        write_ndjson(records, str(out))
        parsed = json.loads(out.read_text(encoding="utf-8").strip())
        assert parsed["min_brightness"] == 0

    def test_ndjson_export_pbm_xcf_records(self, tmp_path):
        records = [
            {"file": PBM_PATTERN.name, "is_wider_than_tall": pbm_is_wider_than_tall(PBM_PATTERN)},
            {"file": XCF_RED.name, "is_high_res": xcf_is_high_res(XCF_RED)},
        ]
        out = tmp_path / "pbm_xcf_remaining.ndjson"
        write_ndjson(records, str(out))
        lines = out.read_text(encoding="utf-8").strip().splitlines()
        assert json.loads(lines[0])["is_wider_than_tall"] is True
        assert json.loads(lines[1])["is_high_res"] is False
