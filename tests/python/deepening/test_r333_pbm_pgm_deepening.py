"""Sprint 123 — PBM (pbm_bytes_per_pixel, pbm_edge_pixel_count)
and PGM (pgm_bytes_per_pixel, pgm_avg_pixel_value).
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pbm.pbm_parser import pbm_bytes_per_pixel, pbm_edge_pixel_count
from src.python.pgm.pgm_parser import pgm_bytes_per_pixel, pgm_avg_pixel_value

PBM = _REPO / "samples" / "by-format" / "pbm" / "valid"
PGM = _REPO / "samples" / "by-format" / "pgm" / "valid"


class TestPbmBytesPerPixel:
    def test_1x1_value(self):
        assert abs(pbm_bytes_per_pixel(PBM / "1x1-black.pbm") - 12.0) < 0.01

    def test_checker_value(self):
        assert abs(pbm_bytes_per_pixel(PBM / "2x2-checker.pbm") - 4.75) < 0.01

    def test_pattern_value(self):
        assert abs(pbm_bytes_per_pixel(PBM / "3x2-pattern.pbm") - 3.833) < 0.01

    def test_returns_float(self):
        assert isinstance(pbm_bytes_per_pixel(PBM / "1x1-black.pbm"), float)

    def test_positive(self):
        assert pbm_bytes_per_pixel(PBM / "2x2-checker.pbm") > 0.0


class TestPbmEdgePixelCount:
    def test_1x1_value(self):
        assert pbm_edge_pixel_count(PBM / "1x1-black.pbm") == 1

    def test_checker_value(self):
        assert pbm_edge_pixel_count(PBM / "2x2-checker.pbm") == 2

    def test_pattern_value(self):
        assert pbm_edge_pixel_count(PBM / "3x2-pattern.pbm") == 3

    def test_returns_int(self):
        assert isinstance(pbm_edge_pixel_count(PBM / "1x1-black.pbm"), int)

    def test_non_negative(self):
        assert pbm_edge_pixel_count(PBM / "2x2-checker.pbm") >= 0


class TestPgmBytesPerPixel:
    def test_white_value(self):
        assert abs(pgm_bytes_per_pixel(PGM / "1x1-white.pgm") - 19.0) < 0.01

    def test_gradient_value(self):
        assert abs(pgm_bytes_per_pixel(PGM / "2x2-gradient.pgm") - 7.25) < 0.01

    def test_ramp_value(self):
        assert abs(pgm_bytes_per_pixel(PGM / "3x1-ramp.pgm") - 8.333) < 0.01

    def test_returns_float(self):
        assert isinstance(pgm_bytes_per_pixel(PGM / "1x1-white.pgm"), float)

    def test_positive(self):
        assert pgm_bytes_per_pixel(PGM / "2x2-gradient.pgm") > 0.0


class TestPgmAvgPixelValue:
    def test_white_value(self):
        assert abs(pgm_avg_pixel_value(PGM / "1x1-white.pgm") - 255.0) < 0.01

    def test_gradient_value(self):
        assert abs(pgm_avg_pixel_value(PGM / "2x2-gradient.pgm") - 127.5) < 0.01

    def test_ramp_value(self):
        assert abs(pgm_avg_pixel_value(PGM / "3x1-ramp.pgm") - 127.667) < 0.01

    def test_returns_float(self):
        assert isinstance(pgm_avg_pixel_value(PGM / "1x1-white.pgm"), float)

    def test_non_negative(self):
        assert pgm_avg_pixel_value(PGM / "2x2-gradient.pgm") >= 0.0
