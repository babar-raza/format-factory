"""
test_r331_ppm_new_analytics.py
Sprint 67 — 5 new PPM analytics functions.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ppm.ppm_parser import (
    ppm_aspect_ratio,
    ppm_total_blue_sum,
    ppm_max_red_value,
    ppm_min_brightness,
    ppm_grayscale_pixel_count,
)

_SAMPLES = _REPO / "samples" / "by-format" / "ppm" / "valid"
_RED = str(_SAMPLES / "1x1-red.ppm")
_RGBW = str(_SAMPLES / "2x2-rgbw.ppm")
_GRADIENT = str(_SAMPLES / "3x1-gradient.ppm")


# --- ppm_aspect_ratio ---

class TestPpmAspectRatio:
    def test_returns_float(self):
        assert isinstance(ppm_aspect_ratio(_RGBW), float)

    def test_red_square(self):
        # 1x1 image
        assert ppm_aspect_ratio(_RED) == 1.0

    def test_rgbw_square(self):
        # 2x2 image
        assert ppm_aspect_ratio(_RGBW) == 1.0

    def test_gradient_wide(self):
        # 3x1 image: width=3, height=1 => 3.0
        assert ppm_aspect_ratio(_GRADIENT) == 3.0

    def test_non_negative(self):
        assert ppm_aspect_ratio(_RGBW) >= 0.0


# --- ppm_total_blue_sum ---

class TestPpmTotalBlueSum:
    def test_returns_int(self):
        assert isinstance(ppm_total_blue_sum(_RGBW), int)

    def test_non_negative(self):
        assert ppm_total_blue_sum(_RGBW) >= 0

    def test_red_has_no_blue(self):
        # pure red pixel: R=255, G=0, B=0
        assert ppm_total_blue_sum(_RED) == 0

    def test_rgbw_non_negative(self):
        assert ppm_total_blue_sum(_RGBW) >= 0

    def test_gradient_non_negative(self):
        assert ppm_total_blue_sum(_GRADIENT) >= 0


# --- ppm_max_red_value ---

class TestPpmMaxRedValue:
    def test_returns_int(self):
        assert isinstance(ppm_max_red_value(_RED), int)

    def test_non_negative(self):
        assert ppm_max_red_value(_RED) >= 0

    def test_red_has_max_red(self):
        # pure red pixel has max red
        assert ppm_max_red_value(_RED) >= 1

    def test_rgbw_non_negative(self):
        assert ppm_max_red_value(_RGBW) >= 0

    def test_gradient_non_negative(self):
        assert ppm_max_red_value(_GRADIENT) >= 0


# --- ppm_min_brightness ---

class TestPpmMinBrightness:
    def test_returns_float(self):
        assert isinstance(ppm_min_brightness(_RGBW), float)

    def test_non_negative(self):
        assert ppm_min_brightness(_RGBW) >= 0.0

    def test_red_positive(self):
        # pure red pixel has brightness 255/3 > 0
        assert ppm_min_brightness(_RED) > 0.0

    def test_rgbw_non_negative(self):
        assert ppm_min_brightness(_RGBW) >= 0.0

    def test_gradient_non_negative(self):
        assert ppm_min_brightness(_GRADIENT) >= 0.0


# --- ppm_grayscale_pixel_count ---

class TestPpmGrayscalePixelCount:
    def test_returns_int(self):
        assert isinstance(ppm_grayscale_pixel_count(_RGBW), int)

    def test_non_negative(self):
        assert ppm_grayscale_pixel_count(_RGBW) >= 0

    def test_red_not_grayscale(self):
        # pure red: R=255, G=0, B=0 — not grayscale
        assert ppm_grayscale_pixel_count(_RED) == 0

    def test_rgbw_non_negative(self):
        assert ppm_grayscale_pixel_count(_RGBW) >= 0

    def test_gradient_non_negative(self):
        assert ppm_grayscale_pixel_count(_GRADIENT) >= 0
