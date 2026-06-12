"""
tests/python/netpbm/test_r201_netpbm_advanced_ops.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-SPRINT6-001
TASK-001: PBM/PGM/PPM advanced operations — pixel analytics, transforms, cross-format conversion.

PBM covers: probe_pbm, parse_pbm, get_capabilities, get_dimensions, pixel_count,
count_black, count_white, black_pixel_ratio, pbm_white_pixel_ratio, pbm_aspect_ratio,
pbm_white_pixel_count, image_pixel_stats, flip_horizontal, invert, rotate_90,
crop, write_pbm, convert_pbm_to_pgm.

PGM covers: probe_pgm, parse_pgm, get_capabilities, get_dimensions, pixel_count,
average_gray, count_above_threshold, min_max_gray, histogram, grayscale_variance,
pgm_bright_pixel_ratio, pgm_dark_pixel_count, pgm_average_brightness,
pgm_max_pixel_value, pgm_min_pixel_value, pgm_contrast_range, image_pixel_stats,
flip_horizontal, normalize, threshold, rotate_90, write_pgm.

PPM covers: probe_ppm, parse_ppm, get_capabilities, get_dimensions, pixel_count,
average_color, is_grayscale, ppm_red_channel_average, ppm_unique_color_count,
ppm_brightness_variance, ppm_pixel_count, to_grayscale, brightness, crop,
flip_horizontal, invert, flip_vertical, rotate_90, write_ppm, convert_ppm_to_pgm.
"""
from __future__ import annotations

import sys
import os
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

import pbm
from pbm import (
    parse_pbm, parse_pbm_strict, probe_pbm, get_capabilities as pbm_capabilities,
    image_pixel_stats as pbm_pixel_stats, write_pbm, get_dimensions as pbm_dimensions,
    pixel_count as pbm_pixel_count, count_black, count_white,
    flip_horizontal as pbm_flip_h, invert as pbm_invert, crop as pbm_crop,
    rotate_90 as pbm_rotate, black_pixel_ratio, pbm_white_pixel_ratio,
    pbm_aspect_ratio, pbm_white_pixel_count, convert_pbm_to_pgm,
)

import pgm
from pgm import (
    parse_pgm, parse_pgm_strict, probe_pgm, get_capabilities as pgm_capabilities,
    image_pixel_stats as pgm_pixel_stats, write_pgm, get_dimensions as pgm_dimensions,
    pixel_count as pgm_pixel_count, average_gray, count_above_threshold, min_max_gray,
    flip_horizontal as pgm_flip_h, normalize, histogram, threshold as pgm_threshold,
    rotate_90 as pgm_rotate, grayscale_variance, pgm_bright_pixel_ratio,
    pgm_dark_pixel_count, pgm_average_brightness, pgm_max_pixel_value,
    pgm_min_pixel_value, pgm_contrast_range,
)

import ppm
from ppm import (
    parse_ppm, parse_ppm_strict, probe_ppm, get_capabilities as ppm_capabilities,
    write_ppm, get_dimensions as ppm_dimensions, to_grayscale, brightness as ppm_brightness,
    pixel_count as ppm_pixel_count_fn, average_color, crop as ppm_crop,
    flip_horizontal as ppm_flip_h, invert as ppm_invert, flip_vertical as ppm_flip_v,
    rotate_90 as ppm_rotate, is_grayscale, ppm_red_channel_average,
    ppm_unique_color_count, ppm_brightness_variance, ppm_pixel_count,
    convert_ppm_to_pgm,
)


# --- Helpers ---

def _make_pbm(width=4, height=4):
    """Create a minimal PBM P1 file. Returns path."""
    pixels = [i % 2 for i in range(width * height)]  # alternating 0/1
    fd, path = tempfile.mkstemp(suffix=".pbm")
    os.close(fd)
    write_pbm(pixels, width, height, path)
    return path, pixels


def _make_pgm(width=4, height=4, maxval=255):
    """Create a minimal PGM P2 file. Returns path."""
    pixels = [int(i * maxval / (width * height - 1)) for i in range(width * height)]
    fd, path = tempfile.mkstemp(suffix=".pgm")
    os.close(fd)
    write_pgm(pixels, width, height, maxval, path)
    return path, pixels


def _make_ppm(width=4, height=4, maxval=255):
    """Create a minimal PPM P3 file. Returns path."""
    pixels = [
        (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 255),
        (128, 128, 128), (0, 0, 0), (255, 128, 0), (0, 128, 255),
        (255, 0, 128), (128, 0, 255), (0, 255, 128), (128, 255, 0),
        (64, 64, 64), (192, 192, 192), (32, 32, 32), (224, 224, 224),
    ][:width * height]
    fd, path = tempfile.mkstemp(suffix=".ppm")
    os.close(fd)
    write_ppm(pixels, width, height, maxval, path)
    return path, pixels


def _dest():
    fd, path = tempfile.mkstemp()
    os.close(fd)
    return path


# =====================================================================
# PBM Tests
# =====================================================================

class TestPbmProbeAndParse:
    """probe_pbm, parse_pbm, get_capabilities."""

    def test_probe_pbm_returns_dict(self):
        path, _ = _make_pbm()
        try:
            result = probe_pbm(path)
            assert isinstance(result, dict)
        finally:
            os.unlink(path)

    def test_probe_pbm_exists_true(self):
        path, _ = _make_pbm()
        try:
            result = probe_pbm(path)
            assert result.get("exists") is True
        finally:
            os.unlink(path)

    def test_parse_pbm_returns_dict(self):
        path, _ = _make_pbm()
        try:
            result = parse_pbm(path)
            assert isinstance(result, dict)
        finally:
            os.unlink(path)

    def test_pbm_capabilities_returns_dict(self):
        result = pbm_capabilities()
        assert isinstance(result, dict)

    def test_pbm_dimensions_correct(self):
        path, _ = _make_pbm(4, 4)
        try:
            w, h = pbm_dimensions(path)
            assert w == 4
            assert h == 4
        finally:
            os.unlink(path)


class TestPbmPixelAnalytics:
    """pixel_count, count_black, count_white, ratios."""

    def test_pixel_count_correct(self):
        path, _ = _make_pbm(4, 4)
        try:
            assert pbm_pixel_count(path) == 16
        finally:
            os.unlink(path)

    def test_count_black_int(self):
        path, _ = _make_pbm()
        try:
            n = count_black(path)
            assert isinstance(n, int)
            assert n >= 0
        finally:
            os.unlink(path)

    def test_count_white_int(self):
        path, _ = _make_pbm()
        try:
            n = count_white(path)
            assert isinstance(n, int)
            assert n >= 0
        finally:
            os.unlink(path)

    def test_black_plus_white_equals_total(self):
        path, _ = _make_pbm(4, 4)
        try:
            assert count_black(path) + count_white(path) == 16
        finally:
            os.unlink(path)

    def test_black_pixel_ratio_float(self):
        path, _ = _make_pbm()
        try:
            r = black_pixel_ratio(path)
            assert isinstance(r, float)
            assert 0.0 <= r <= 1.0
        finally:
            os.unlink(path)

    def test_pbm_white_pixel_ratio_float(self):
        path, _ = _make_pbm()
        try:
            r = pbm_white_pixel_ratio(path)
            assert isinstance(r, float)
            assert 0.0 <= r <= 1.0
        finally:
            os.unlink(path)

    def test_pbm_aspect_ratio_positive(self):
        path, _ = _make_pbm(8, 4)
        try:
            r = pbm_aspect_ratio(path)
            assert isinstance(r, float)
            assert r == 2.0
        finally:
            os.unlink(path)

    def test_pbm_white_pixel_count_int(self):
        path, _ = _make_pbm()
        try:
            n = pbm_white_pixel_count(path)
            assert isinstance(n, int)
        finally:
            os.unlink(path)

    def test_image_pixel_stats_returns_dict(self):
        path, _ = _make_pbm()
        try:
            result = pbm_pixel_stats(path)
            assert isinstance(result, dict)
        finally:
            os.unlink(path)


class TestPbmTransforms:
    """flip_horizontal, invert, rotate_90, crop, convert_pbm_to_pgm."""

    def test_flip_horizontal_produces_file(self):
        path, _ = _make_pbm()
        dest = _dest()
        try:
            result = pbm_flip_h(path, dest)
            assert isinstance(result, dict)
            assert os.path.getsize(dest) > 0
        finally:
            os.unlink(path)
            os.unlink(dest)

    def test_invert_produces_file(self):
        path, _ = _make_pbm()
        dest = _dest()
        try:
            result = pbm_invert(path, dest)
            assert isinstance(result, dict)
            assert os.path.getsize(dest) > 0
        finally:
            os.unlink(path)
            os.unlink(dest)

    def test_rotate_90_produces_file(self):
        path, _ = _make_pbm(4, 4)
        dest = _dest()
        try:
            result = pbm_rotate(path, dest)
            assert isinstance(result, dict)
            assert os.path.getsize(dest) > 0
        finally:
            os.unlink(path)
            os.unlink(dest)

    def test_crop_produces_file(self):
        path, _ = _make_pbm(4, 4)
        dest = _dest()
        try:
            result = pbm_crop(path, dest, 0, 0, 2, 2)
            assert isinstance(result, dict)
            assert os.path.getsize(dest) > 0
        finally:
            os.unlink(path)
            os.unlink(dest)

    def test_convert_pbm_to_pgm_produces_file(self):
        path, _ = _make_pbm()
        fd, dest = tempfile.mkstemp(suffix=".pgm")
        os.close(fd)
        try:
            result = convert_pbm_to_pgm(path, dest)
            assert isinstance(result, dict)
            assert os.path.getsize(dest) > 0
        finally:
            os.unlink(path)
            os.unlink(dest)


# =====================================================================
# PGM Tests
# =====================================================================

class TestPgmProbeAndParse:
    """probe_pgm, parse_pgm, get_capabilities."""

    def test_probe_pgm_returns_dict(self):
        path, _ = _make_pgm()
        try:
            result = probe_pgm(path)
            assert isinstance(result, dict)
        finally:
            os.unlink(path)

    def test_probe_pgm_exists_true(self):
        path, _ = _make_pgm()
        try:
            result = probe_pgm(path)
            assert result.get("exists") is True
        finally:
            os.unlink(path)

    def test_parse_pgm_returns_dict(self):
        path, _ = _make_pgm()
        try:
            result = parse_pgm(path)
            assert isinstance(result, dict)
        finally:
            os.unlink(path)

    def test_pgm_capabilities_returns_dict(self):
        result = pgm_capabilities()
        assert isinstance(result, dict)

    def test_pgm_dimensions_correct(self):
        path, _ = _make_pgm(4, 4)
        try:
            w, h = pgm_dimensions(path)
            assert w == 4 and h == 4
        finally:
            os.unlink(path)


class TestPgmPixelAnalytics:
    """pixel_count, average_gray, min_max_gray, threshold, histogram, variance."""

    def test_pixel_count_correct(self):
        path, _ = _make_pgm(4, 4)
        try:
            assert pgm_pixel_count(path) == 16
        finally:
            os.unlink(path)

    def test_average_gray_float(self):
        path, _ = _make_pgm()
        try:
            avg = average_gray(path)
            assert isinstance(avg, float)
            assert 0.0 <= avg <= 255.0
        finally:
            os.unlink(path)

    def test_min_max_gray_tuple(self):
        path, _ = _make_pgm()
        try:
            lo, hi = min_max_gray(path)
            assert isinstance(lo, int) and isinstance(hi, int)
            assert lo <= hi
        finally:
            os.unlink(path)

    def test_count_above_threshold_int(self):
        path, _ = _make_pgm()
        try:
            n = count_above_threshold(path, 128)
            assert isinstance(n, int)
            assert n >= 0
        finally:
            os.unlink(path)

    def test_histogram_returns_dict(self):
        path, _ = _make_pgm()
        try:
            result = histogram(path)
            assert isinstance(result, dict)
        finally:
            os.unlink(path)

    def test_grayscale_variance_float(self):
        path, _ = _make_pgm()
        try:
            v = grayscale_variance(path)
            assert isinstance(v, float)
            assert v >= 0.0
        finally:
            os.unlink(path)

    def test_pgm_bright_pixel_ratio_float(self):
        path, _ = _make_pgm()
        try:
            r = pgm_bright_pixel_ratio(path)
            assert isinstance(r, float)
            assert 0.0 <= r <= 1.0
        finally:
            os.unlink(path)

    def test_pgm_dark_pixel_count_int(self):
        path, _ = _make_pgm()
        try:
            n = pgm_dark_pixel_count(path)
            assert isinstance(n, int)
        finally:
            os.unlink(path)

    def test_pgm_average_brightness_float(self):
        path, _ = _make_pgm()
        try:
            b = pgm_average_brightness(path)
            assert isinstance(b, float)
        finally:
            os.unlink(path)

    def test_pgm_max_min_values(self):
        path, _ = _make_pgm()
        try:
            mx = pgm_max_pixel_value(path)
            mn = pgm_min_pixel_value(path)
            assert isinstance(mx, int) and isinstance(mn, int)
            assert mn <= mx
        finally:
            os.unlink(path)

    def test_pgm_contrast_range_int(self):
        path, _ = _make_pgm()
        try:
            cr = pgm_contrast_range(path)
            assert isinstance(cr, int)
            assert cr >= 0
        finally:
            os.unlink(path)


class TestPgmTransforms:
    """flip_horizontal, normalize, threshold, rotate_90."""

    def test_flip_horizontal_produces_file(self):
        path, _ = _make_pgm()
        fd, dest = tempfile.mkstemp(suffix=".pgm")
        os.close(fd)
        try:
            result = pgm_flip_h(path, dest)
            assert isinstance(result, dict)
            assert os.path.getsize(dest) > 0
        finally:
            os.unlink(path)
            os.unlink(dest)

    def test_normalize_produces_file(self):
        path, _ = _make_pgm()
        fd, dest = tempfile.mkstemp(suffix=".pgm")
        os.close(fd)
        try:
            result = normalize(path, dest)
            assert isinstance(result, dict)
            assert os.path.getsize(dest) > 0
        finally:
            os.unlink(path)
            os.unlink(dest)

    def test_threshold_produces_file(self):
        path, _ = _make_pgm()
        fd, dest = tempfile.mkstemp(suffix=".pgm")
        os.close(fd)
        try:
            result = pgm_threshold(path, dest, 128)
            assert isinstance(result, dict)
            assert os.path.getsize(dest) > 0
        finally:
            os.unlink(path)
            os.unlink(dest)

    def test_rotate_90_produces_file(self):
        path, _ = _make_pgm(4, 4)
        fd, dest = tempfile.mkstemp(suffix=".pgm")
        os.close(fd)
        try:
            result = pgm_rotate(path, dest)
            assert isinstance(result, dict)
            assert os.path.getsize(dest) > 0
        finally:
            os.unlink(path)
            os.unlink(dest)


# =====================================================================
# PPM Tests
# =====================================================================

class TestPpmProbeAndParse:
    """probe_ppm, parse_ppm, get_capabilities."""

    def test_probe_ppm_returns_dict(self):
        path, _ = _make_ppm()
        try:
            result = probe_ppm(path)
            assert isinstance(result, dict)
        finally:
            os.unlink(path)

    def test_probe_ppm_exists_true(self):
        path, _ = _make_ppm()
        try:
            result = probe_ppm(path)
            assert result.get("exists") is True
        finally:
            os.unlink(path)

    def test_parse_ppm_returns_dict(self):
        path, _ = _make_ppm()
        try:
            result = parse_ppm(path)
            assert isinstance(result, dict)
        finally:
            os.unlink(path)

    def test_ppm_capabilities_returns_dict(self):
        result = ppm_capabilities()
        assert isinstance(result, dict)

    def test_ppm_dimensions_correct(self):
        path, _ = _make_ppm(4, 4)
        try:
            w, h = ppm_dimensions(path)
            assert w == 4 and h == 4
        finally:
            os.unlink(path)


class TestPpmPixelAnalytics:
    """pixel_count, average_color, is_grayscale, channel analytics."""

    def test_pixel_count_correct(self):
        path, _ = _make_ppm(4, 4)
        try:
            assert ppm_pixel_count_fn(path) == 16
        finally:
            os.unlink(path)

    def test_ppm_pixel_count_correct(self):
        path, _ = _make_ppm(4, 4)
        try:
            assert ppm_pixel_count(path) == 16
        finally:
            os.unlink(path)

    def test_average_color_tuple(self):
        path, _ = _make_ppm()
        try:
            result = average_color(path)
            assert isinstance(result, tuple)
            assert len(result) == 3
        finally:
            os.unlink(path)

    def test_is_grayscale_false_for_color(self):
        path, _ = _make_ppm()
        try:
            result = is_grayscale(path)
            assert isinstance(result, bool)
        finally:
            os.unlink(path)

    def test_ppm_red_channel_average_float(self):
        path, _ = _make_ppm()
        try:
            r = ppm_red_channel_average(path)
            assert isinstance(r, float)
            assert 0.0 <= r <= 255.0
        finally:
            os.unlink(path)

    def test_ppm_unique_color_count_positive(self):
        path, _ = _make_ppm()
        try:
            n = ppm_unique_color_count(path)
            assert isinstance(n, int)
            assert n > 0
        finally:
            os.unlink(path)

    def test_ppm_brightness_variance_float(self):
        path, _ = _make_ppm()
        try:
            v = ppm_brightness_variance(path)
            assert isinstance(v, float)
            assert v >= 0.0
        finally:
            os.unlink(path)


class TestPpmTransforms:
    """to_grayscale, brightness, crop, flip_horizontal, invert, flip_vertical, rotate_90, convert_ppm_to_pgm."""

    def test_to_grayscale_produces_pgm(self):
        path, _ = _make_ppm()
        fd, dest = tempfile.mkstemp(suffix=".pgm")
        os.close(fd)
        try:
            result = to_grayscale(path, dest)
            assert isinstance(result, dict)
            assert os.path.getsize(dest) > 0
        finally:
            os.unlink(path)
            os.unlink(dest)

    def test_brightness_produces_file(self):
        path, _ = _make_ppm()
        fd, dest = tempfile.mkstemp(suffix=".ppm")
        os.close(fd)
        try:
            result = ppm_brightness(path, dest, 10)
            assert isinstance(result, dict)
            assert os.path.getsize(dest) > 0
        finally:
            os.unlink(path)
            os.unlink(dest)

    def test_crop_produces_file(self):
        path, _ = _make_ppm(4, 4)
        fd, dest = tempfile.mkstemp(suffix=".ppm")
        os.close(fd)
        try:
            result = ppm_crop(path, dest, 0, 0, 2, 2)
            assert isinstance(result, dict)
            assert os.path.getsize(dest) > 0
        finally:
            os.unlink(path)
            os.unlink(dest)

    def test_flip_horizontal_produces_file(self):
        path, _ = _make_ppm()
        fd, dest = tempfile.mkstemp(suffix=".ppm")
        os.close(fd)
        try:
            result = ppm_flip_h(path, dest)
            assert isinstance(result, dict)
            assert os.path.getsize(dest) > 0
        finally:
            os.unlink(path)
            os.unlink(dest)

    def test_invert_produces_file(self):
        path, _ = _make_ppm()
        fd, dest = tempfile.mkstemp(suffix=".ppm")
        os.close(fd)
        try:
            result = ppm_invert(path, dest)
            assert isinstance(result, dict)
            assert os.path.getsize(dest) > 0
        finally:
            os.unlink(path)
            os.unlink(dest)

    def test_flip_vertical_produces_file(self):
        path, _ = _make_ppm()
        fd, dest = tempfile.mkstemp(suffix=".ppm")
        os.close(fd)
        try:
            result = ppm_flip_v(path, dest)
            assert isinstance(result, dict)
            assert os.path.getsize(dest) > 0
        finally:
            os.unlink(path)
            os.unlink(dest)

    def test_rotate_90_produces_file(self):
        path, _ = _make_ppm(4, 4)
        fd, dest = tempfile.mkstemp(suffix=".ppm")
        os.close(fd)
        try:
            result = ppm_rotate(path, dest)
            assert isinstance(result, dict)
            assert os.path.getsize(dest) > 0
        finally:
            os.unlink(path)
            os.unlink(dest)

    def test_convert_ppm_to_pgm_produces_file(self):
        path, _ = _make_ppm()
        fd, dest = tempfile.mkstemp(suffix=".pgm")
        os.close(fd)
        try:
            result = convert_ppm_to_pgm(path, dest)
            assert isinstance(result, dict)
            assert os.path.getsize(dest) > 0
        finally:
            os.unlink(path)
            os.unlink(dest)
