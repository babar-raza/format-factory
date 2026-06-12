"""
Tests for ppm_brightness_variance — sprint product-deepening-rnext72.

Sprint: FORMAT-FACTORY-ABW-ZST-DEEPENING-001
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
PPM_SAMPLES = REPO / "samples" / "by-format" / "ppm" / "valid"

sys.path.insert(0, str(REPO / "src" / "python"))

from ppm.ppm_parser import ppm_brightness_variance


def test_import():
    assert callable(ppm_brightness_variance)


def test_single_color_variance_is_zero():
    result = ppm_brightness_variance(PPM_SAMPLES / "1x1-red.ppm")
    assert result == 0.0


def test_rgbw_variance_positive():
    result = ppm_brightness_variance(PPM_SAMPLES / "2x2-rgbw.ppm")
    assert abs(result - 5418.75) < 0.01


def test_gradient_variance_positive():
    result = ppm_brightness_variance(PPM_SAMPLES / "3x1-gradient.ppm")
    assert result > 0.0


def test_returns_float():
    result = ppm_brightness_variance(PPM_SAMPLES / "1x1-red.ppm")
    assert isinstance(result, float)


def test_result_nonnegative():
    result = ppm_brightness_variance(PPM_SAMPLES / "2x2-rgbw.ppm")
    assert result >= 0.0
