"""
Tests for ppm_pixel_count — sprint product-deepening-rnext78.

Sprint: FORMAT-FACTORY-ABW-ZST-DEEPENING-001
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
PPM_SAMPLES = REPO / "samples" / "by-format" / "ppm" / "valid"

sys.path.insert(0, str(REPO / "src" / "python"))

from ppm.ppm_parser import ppm_pixel_count


def test_import():
    assert callable(ppm_pixel_count)


def test_1x1_red_has_one_pixel():
    result = ppm_pixel_count(PPM_SAMPLES / "1x1-red.ppm")
    assert result == 1


def test_2x2_rgbw_has_four_pixels():
    result = ppm_pixel_count(PPM_SAMPLES / "2x2-rgbw.ppm")
    assert result == 4


def test_3x1_gradient_has_three_pixels():
    result = ppm_pixel_count(PPM_SAMPLES / "3x1-gradient.ppm")
    assert result == 3


def test_returns_int():
    result = ppm_pixel_count(PPM_SAMPLES / "1x1-red.ppm")
    assert isinstance(result, int)


def test_result_nonnegative():
    result = ppm_pixel_count(PPM_SAMPLES / "2x2-rgbw.ppm")
    assert result >= 0
