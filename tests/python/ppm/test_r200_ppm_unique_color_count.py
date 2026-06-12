"""
Tests for ppm_unique_color_count — sprint product-deepening-rnext69.

Sprint: FORMAT-FACTORY-ABW-ZST-DEEPENING-001
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
PPM_SAMPLES = REPO / "samples" / "by-format" / "ppm" / "valid"

sys.path.insert(0, str(REPO / "src" / "python"))

from ppm.ppm_parser import ppm_unique_color_count


def test_import():
    assert callable(ppm_unique_color_count)


def test_single_color_image_returns_one():
    result = ppm_unique_color_count(PPM_SAMPLES / "1x1-red.ppm")
    assert result == 1


def test_rgbw_image_returns_four():
    result = ppm_unique_color_count(PPM_SAMPLES / "2x2-rgbw.ppm")
    assert result == 4


def test_gradient_returns_three():
    result = ppm_unique_color_count(PPM_SAMPLES / "3x1-gradient.ppm")
    assert result == 3


def test_returns_int():
    result = ppm_unique_color_count(PPM_SAMPLES / "1x1-red.ppm")
    assert isinstance(result, int)


def test_result_nonnegative():
    result = ppm_unique_color_count(PPM_SAMPLES / "2x2-rgbw.ppm")
    assert result >= 0
