"""
tests/python/ppm/test_r202_ppm_advanced_ops.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-SPRINT18-001
TASK-001 (part B): PPM advanced operations.

Covers: parse_ppm, parse_ppm_strict, probe_ppm, get_capabilities,
get_dimensions, pixel_count, ppm_pixel_count, average_color,
ppm_brightness_variance, ppm_red_channel_average, ppm_unique_color_count,
is_grayscale, PpmImage.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ppm import (
    parse_ppm, parse_ppm_strict, probe_ppm, get_capabilities,
    get_dimensions, pixel_count, ppm_pixel_count, average_color,
    ppm_brightness_variance, ppm_red_channel_average, ppm_unique_color_count,
    is_grayscale, PpmImage,
)

_SAMPLES = _REPO / "samples" / "by-format" / "ppm" / "valid"
_1X1 = str(_SAMPLES / "1x1-red.ppm")
_2X2 = str(_SAMPLES / "2x2-rgbw.ppm")
_3X1 = str(_SAMPLES / "3x1-gradient.ppm")


class TestPpmParseAndProbe:
    """parse_ppm, parse_ppm_strict, probe_ppm, get_capabilities."""

    def test_parse_ppm_returns_dict(self):
        result = parse_ppm(_2X2)
        assert isinstance(result, dict)

    def test_parse_ppm_ok_true(self):
        result = parse_ppm(_2X2)
        assert result.get("ok") is True

    def test_parse_ppm_width(self):
        result = parse_ppm(_2X2)
        assert result.get("width") == 2

    def test_parse_ppm_height(self):
        result = parse_ppm(_2X2)
        assert result.get("height") == 2

    def test_parse_ppm_pixel_count(self):
        result = parse_ppm(_2X2)
        assert result.get("pixel_count") == 4

    def test_parse_ppm_magic_p3(self):
        result = parse_ppm(_2X2)
        assert result.get("magic") in ("P3", "P6")

    def test_parse_ppm_has_maxval(self):
        result = parse_ppm(_2X2)
        assert "maxval" in result
        assert result["maxval"] == 255

    def test_parse_ppm_strict_returns_ppmimage(self):
        img = parse_ppm_strict(_2X2)
        assert isinstance(img, PpmImage)

    def test_probe_ppm_returns_dict(self):
        result = probe_ppm(_2X2)
        assert isinstance(result, dict)

    def test_probe_ppm_exists(self):
        result = probe_ppm(_2X2)
        assert result.get("exists") is True

    def test_probe_ppm_valid_header(self):
        result = probe_ppm(_2X2)
        assert result.get("valid_header") is True

    def test_probe_ppm_dimensions(self):
        result = probe_ppm(_2X2)
        assert result.get("width") == 2
        assert result.get("height") == 2

    def test_get_capabilities_dict(self):
        caps = get_capabilities()
        assert isinstance(caps, dict)
        assert caps.get("format") == "ppm"

    def test_get_capabilities_has_supported(self):
        caps = get_capabilities()
        assert isinstance(caps.get("supported"), list)
        assert len(caps["supported"]) > 0


class TestPpmDimensions:
    """get_dimensions, pixel_count, ppm_pixel_count."""

    def test_get_dimensions_tuple(self):
        dims = get_dimensions(_2X2)
        assert isinstance(dims, tuple)
        assert len(dims) == 2

    def test_get_dimensions_2x2(self):
        w, h = get_dimensions(_2X2)
        assert w == 2 and h == 2

    def test_get_dimensions_1x1(self):
        w, h = get_dimensions(_1X1)
        assert w == 1 and h == 1

    def test_pixel_count_2x2(self):
        assert pixel_count(_2X2) == 4

    def test_ppm_pixel_count_2x2(self):
        assert ppm_pixel_count(_2X2) == 4

    def test_pixel_count_1x1(self):
        assert pixel_count(_1X1) == 1


class TestPpmAnalytics:
    """average_color, ppm_brightness_variance, ppm_red_channel_average,
    ppm_unique_color_count, is_grayscale."""

    def test_average_color_tuple(self):
        color = average_color(_2X2)
        assert isinstance(color, tuple)
        assert len(color) == 3

    def test_average_color_1x1_red(self):
        # 1x1 red: RGB (255, 0, 0)
        r, g, b = average_color(_1X1)
        assert r == 255.0 and g == 0.0 and b == 0.0

    def test_ppm_brightness_variance_float(self):
        v = ppm_brightness_variance(_2X2)
        assert isinstance(v, (int, float))
        assert v >= 0

    def test_ppm_brightness_variance_uniform_zero(self):
        # 1x1 single color → zero variance
        v = ppm_brightness_variance(_1X1)
        assert v == 0.0

    def test_ppm_red_channel_average_float(self):
        r = ppm_red_channel_average(_2X2)
        assert isinstance(r, (int, float))
        assert 0.0 <= r <= 255.0

    def test_ppm_red_channel_average_1x1_red(self):
        r = ppm_red_channel_average(_1X1)
        assert r == 255.0

    def test_ppm_unique_color_count_int(self):
        n = ppm_unique_color_count(_2X2)
        assert isinstance(n, int)
        assert n > 0

    def test_ppm_unique_color_count_1x1(self):
        # 1x1 has exactly 1 unique color
        n = ppm_unique_color_count(_1X1)
        assert n == 1

    def test_ppm_unique_color_count_2x2_four(self):
        # 2x2-rgbw: 4 distinct colors (R, G, B, W)
        n = ppm_unique_color_count(_2X2)
        assert n == 4

    def test_is_grayscale_false_for_rgb(self):
        # Red-only pixel is not grayscale (R != G == B not all equal)
        result = is_grayscale(_1X1)
        assert isinstance(result, bool)
        # 1x1 red: R=255, G=0, B=0 — not grayscale
        assert result is False

    def test_is_grayscale_bool_type(self):
        result = is_grayscale(_2X2)
        assert isinstance(result, bool)
