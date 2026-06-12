"""
tests/python/pbm/test_r202_pbm_advanced_ops.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-SPRINT18-001
TASK-001 (part A): PBM advanced operations.

Covers: parse_pbm, parse_pbm_strict, probe_pbm, get_capabilities,
get_dimensions, pixel_count, count_black, count_white, black_pixel_ratio,
pbm_white_pixel_count, pbm_white_pixel_ratio, pbm_aspect_ratio,
image_pixel_stats, PbmImage.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pbm import (
    parse_pbm, parse_pbm_strict, probe_pbm, get_capabilities,
    get_dimensions, pixel_count, count_black, count_white,
    black_pixel_ratio, pbm_white_pixel_count, pbm_white_pixel_ratio,
    pbm_aspect_ratio, image_pixel_stats, PbmImage,
)

_SAMPLES = _REPO / "samples" / "by-format" / "pbm" / "valid"
_1X1 = str(_SAMPLES / "1x1-black.pbm")
_2X2 = str(_SAMPLES / "2x2-checker.pbm")
_3X2 = str(_SAMPLES / "3x2-pattern.pbm")


class TestPbmParseAndProbe:
    """parse_pbm, parse_pbm_strict, probe_pbm, get_capabilities."""

    def test_parse_pbm_returns_dict(self):
        result = parse_pbm(_2X2)
        assert isinstance(result, dict)

    def test_parse_pbm_ok_true(self):
        result = parse_pbm(_2X2)
        assert result.get("ok") is True

    def test_parse_pbm_width(self):
        result = parse_pbm(_2X2)
        assert result.get("width") == 2

    def test_parse_pbm_height(self):
        result = parse_pbm(_2X2)
        assert result.get("height") == 2

    def test_parse_pbm_pixel_count(self):
        result = parse_pbm(_2X2)
        assert result.get("pixel_count") == 4

    def test_parse_pbm_magic_p1(self):
        result = parse_pbm(_2X2)
        assert result.get("magic") == "P1"

    def test_parse_pbm_strict_returns_pbmimage(self):
        img = parse_pbm_strict(_2X2)
        assert isinstance(img, PbmImage)

    def test_probe_pbm_returns_dict(self):
        result = probe_pbm(_2X2)
        assert isinstance(result, dict)

    def test_probe_pbm_exists(self):
        result = probe_pbm(_2X2)
        assert result.get("exists") is True

    def test_probe_pbm_valid_header(self):
        result = probe_pbm(_2X2)
        assert result.get("valid_header") is True

    def test_probe_pbm_dimensions(self):
        result = probe_pbm(_2X2)
        assert result.get("width") == 2
        assert result.get("height") == 2

    def test_get_capabilities_dict(self):
        caps = get_capabilities()
        assert isinstance(caps, dict)
        assert caps.get("format") == "pbm"

    def test_get_capabilities_has_supported(self):
        caps = get_capabilities()
        assert isinstance(caps.get("supported"), list)
        assert len(caps["supported"]) > 0


class TestPbmDimensions:
    """get_dimensions, pixel_count."""

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

    def test_pixel_count_1x1(self):
        assert pixel_count(_1X1) == 1

    def test_pixel_count_3x2(self):
        assert pixel_count(_3X2) == 6


class TestPbmAnalytics:
    """count_black, count_white, black_pixel_ratio, pbm_white_pixel_count,
    pbm_white_pixel_ratio, pbm_aspect_ratio, image_pixel_stats."""

    def test_count_black_2x2_checker(self):
        # 2x2 checker: 2 black, 2 white
        n = count_black(_2X2)
        assert isinstance(n, int)
        assert n == 2

    def test_count_white_2x2_checker(self):
        n = count_white(_2X2)
        assert isinstance(n, int)
        assert n == 2

    def test_black_pixel_ratio_2x2(self):
        r = black_pixel_ratio(_2X2)
        assert isinstance(r, float)
        assert r == 0.5

    def test_pbm_white_pixel_count(self):
        n = pbm_white_pixel_count(_2X2)
        assert isinstance(n, int)
        assert n == 2

    def test_pbm_white_pixel_ratio(self):
        r = pbm_white_pixel_ratio(_2X2)
        assert isinstance(r, float)
        assert r == 0.5

    def test_pbm_aspect_ratio_square(self):
        r = pbm_aspect_ratio(_2X2)
        assert isinstance(r, float)
        assert r == 1.0

    def test_image_pixel_stats_dict(self):
        stats = image_pixel_stats(_2X2)
        assert isinstance(stats, dict)
        assert stats.get("ok") is True

    def test_image_pixel_stats_counts(self):
        stats = image_pixel_stats(_2X2)
        assert stats.get("black_count") == 2
        assert stats.get("white_count") == 2
        assert stats.get("total_pixels") == 4

    def test_image_pixel_stats_density(self):
        stats = image_pixel_stats(_2X2)
        assert stats.get("black_density") == 0.5

    def test_count_black_1x1(self):
        # 1x1 all-black
        n = count_black(_1X1)
        assert n == 1

    def test_count_white_1x1(self):
        n = count_white(_1X1)
        assert n == 0
