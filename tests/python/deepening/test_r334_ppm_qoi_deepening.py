"""Sprint 124 — PPM (ppm_bytes_per_pixel, ppm_avg_pixel_brightness)
and QOI (qoi_bytes_per_pixel, qoi_avg_pixel_brightness).
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ppm.ppm_parser import ppm_bytes_per_pixel, ppm_avg_pixel_brightness
from src.python.qoi.qoi_parser import qoi_bytes_per_pixel, qoi_avg_pixel_brightness

PPM = _REPO / "samples" / "by-format" / "ppm" / "valid"
QOI = _REPO / "samples" / "by-format" / "qoi" / "valid"


class TestPpmBytesPerPixel:
    def test_red_value(self):
        assert abs(ppm_bytes_per_pixel(PPM / "1x1-red.ppm") - 19.0) < 0.01

    def test_rgbw_value(self):
        assert abs(ppm_bytes_per_pixel(PPM / "2x2-rgbw.ppm") - 11.75) < 0.01

    def test_gradient_value(self):
        assert abs(ppm_bytes_per_pixel(PPM / "3x1-gradient.ppm") - 13.667) < 0.01

    def test_returns_float(self):
        assert isinstance(ppm_bytes_per_pixel(PPM / "1x1-red.ppm"), float)

    def test_positive(self):
        assert ppm_bytes_per_pixel(PPM / "2x2-rgbw.ppm") > 0.0


class TestPpmAvgPixelBrightness:
    def test_red_value(self):
        assert abs(ppm_avg_pixel_brightness(PPM / "1x1-red.ppm") - 85.0) < 0.01

    def test_rgbw_value(self):
        assert abs(ppm_avg_pixel_brightness(PPM / "2x2-rgbw.ppm") - 127.5) < 0.01

    def test_gradient_value(self):
        assert abs(ppm_avg_pixel_brightness(PPM / "3x1-gradient.ppm") - 127.667) < 0.01

    def test_returns_float(self):
        assert isinstance(ppm_avg_pixel_brightness(PPM / "1x1-red.ppm"), float)

    def test_non_negative(self):
        assert ppm_avg_pixel_brightness(PPM / "2x2-rgbw.ppm") >= 0.0


class TestQoiBytesPerPixel:
    def test_red_value(self):
        assert abs(qoi_bytes_per_pixel(QOI / "1x1-red.qoi") - 27.0) < 0.01

    def test_black_value(self):
        assert abs(qoi_bytes_per_pixel(QOI / "2x2-black.qoi") - 5.75) < 0.01

    def test_gradient_value(self):
        assert abs(qoi_bytes_per_pixel(QOI / "4x1-gradient.qoi") - 9.5) < 0.01

    def test_returns_float(self):
        assert isinstance(qoi_bytes_per_pixel(QOI / "1x1-red.qoi"), float)

    def test_positive(self):
        assert qoi_bytes_per_pixel(QOI / "2x2-black.qoi") > 0.0


class TestQoiAvgPixelBrightness:
    def test_red_value(self):
        assert abs(qoi_avg_pixel_brightness(QOI / "1x1-red.qoi") - 85.0) < 0.01

    def test_black_value(self):
        assert abs(qoi_avg_pixel_brightness(QOI / "2x2-black.qoi") - 0.0) < 0.01

    def test_gradient_value(self):
        assert abs(qoi_avg_pixel_brightness(QOI / "4x1-gradient.qoi") - 127.5) < 0.01

    def test_returns_float(self):
        assert isinstance(qoi_avg_pixel_brightness(QOI / "1x1-red.qoi"), float)

    def test_non_negative(self):
        assert qoi_avg_pixel_brightness(QOI / "2x2-black.qoi") >= 0.0
