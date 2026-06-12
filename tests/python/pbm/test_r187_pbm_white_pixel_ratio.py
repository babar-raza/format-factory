"""
tests/python/pbm/test_r187_pbm_white_pixel_ratio.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT55-001
Tests for pbm_white_pixel_ratio() — fraction of white (0) pixels.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pbm.pbm_parser import pbm_white_pixel_ratio

SAMPLES = _REPO / "samples" / "by-format" / "pbm" / "valid"


class TestPbmWhitePixelRatio:
    def test_all_black_image_is_zero(self):
        result = pbm_white_pixel_ratio(SAMPLES / "1x1-black.pbm")
        assert result == 0.0

    def test_checker_pattern_is_half(self):
        result = pbm_white_pixel_ratio(SAMPLES / "2x2-checker.pbm")
        assert result == 0.5

    def test_in_range_zero_to_one(self):
        result = pbm_white_pixel_ratio(SAMPLES / "2x2-checker.pbm")
        assert 0.0 <= result <= 1.0

    def test_returns_float(self):
        result = pbm_white_pixel_ratio(SAMPLES / "1x1-black.pbm")
        assert isinstance(result, float)

    def test_pattern_3x2_half_white(self):
        result = pbm_white_pixel_ratio(SAMPLES / "3x2-pattern.pbm")
        assert result == 0.5

    def test_exported_from_init(self):
        from src.python.pbm import pbm_white_pixel_ratio as fn
        result = fn(SAMPLES / "1x1-black.pbm")
        assert result == 0.0
