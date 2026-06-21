"""
test_r332_qoi_new_analytics.py
Sprint 68 — 5 new QOI analytics functions.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.qoi.qoi_parser import (
    qoi_aspect_ratio,
    qoi_max_red_value,
    qoi_min_brightness,
    qoi_grayscale_pixel_count,
    qoi_file_size_bytes,
)

_SAMPLES = _REPO / "samples" / "by-format" / "qoi" / "valid"
_RED = str(_SAMPLES / "1x1-red.qoi")
_BLACK = str(_SAMPLES / "2x2-black.qoi")
_GRADIENT = str(_SAMPLES / "4x1-gradient.qoi")


# --- qoi_aspect_ratio ---

class TestQoiAspectRatio:
    def test_returns_float(self):
        assert isinstance(qoi_aspect_ratio(_BLACK), float)

    def test_red_square(self):
        # 1x1 image
        assert qoi_aspect_ratio(_RED) == 1.0

    def test_black_square(self):
        # 2x2 image
        assert qoi_aspect_ratio(_BLACK) == 1.0

    def test_gradient_wide(self):
        # 4x1 image: width=4, height=1 => 4.0
        assert qoi_aspect_ratio(_GRADIENT) == 4.0

    def test_non_negative(self):
        assert qoi_aspect_ratio(_BLACK) >= 0.0


# --- qoi_max_red_value ---

class TestQoiMaxRedValue:
    def test_returns_int(self):
        assert isinstance(qoi_max_red_value(_RED), int)

    def test_non_negative(self):
        assert qoi_max_red_value(_RED) >= 0

    def test_red_has_red(self):
        assert qoi_max_red_value(_RED) >= 1

    def test_black_non_negative(self):
        assert qoi_max_red_value(_BLACK) >= 0

    def test_gradient_non_negative(self):
        assert qoi_max_red_value(_GRADIENT) >= 0


# --- qoi_min_brightness ---

class TestQoiMinBrightness:
    def test_returns_float(self):
        assert isinstance(qoi_min_brightness(_RED), float)

    def test_non_negative(self):
        assert qoi_min_brightness(_RED) >= 0.0

    def test_black_zero(self):
        # pure black: R=0, G=0, B=0 => brightness 0.0
        assert qoi_min_brightness(_BLACK) == 0.0

    def test_red_positive(self):
        assert qoi_min_brightness(_RED) > 0.0

    def test_gradient_non_negative(self):
        assert qoi_min_brightness(_GRADIENT) >= 0.0


# --- qoi_grayscale_pixel_count ---

class TestQoiGrayscalePixelCount:
    def test_returns_int(self):
        assert isinstance(qoi_grayscale_pixel_count(_BLACK), int)

    def test_non_negative(self):
        assert qoi_grayscale_pixel_count(_BLACK) >= 0

    def test_black_is_grayscale(self):
        # R=G=B=0 => grayscale
        assert qoi_grayscale_pixel_count(_BLACK) >= 1

    def test_red_not_grayscale(self):
        # R=255, G=0, B=0 => not grayscale
        assert qoi_grayscale_pixel_count(_RED) == 0

    def test_gradient_non_negative(self):
        assert qoi_grayscale_pixel_count(_GRADIENT) >= 0


# --- qoi_file_size_bytes ---

class TestQoiFileSizeBytes:
    def test_returns_int(self):
        assert isinstance(qoi_file_size_bytes(_RED), int)

    def test_positive(self):
        assert qoi_file_size_bytes(_RED) > 0

    def test_black_positive(self):
        assert qoi_file_size_bytes(_BLACK) > 0

    def test_gradient_positive(self):
        assert qoi_file_size_bytes(_GRADIENT) > 0

    def test_at_least_magic_bytes(self):
        # QOI files have at least 14 byte header + 8 byte end marker
        assert qoi_file_size_bytes(_RED) >= 22
