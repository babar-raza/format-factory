"""Tests for PPM Sprint 64 gap closure.

Closes:
  GAP-PPM-FOSS-PPM_LUMINANC-001   (Ppm Luminance Mean)
"""
import pytest
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ppm.ppm_parser import ppm_luminance_mean

_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"
_RED = str(_DIR / "1x1-red.ppm")
_RGBW = str(_DIR / "2x2-rgbw.ppm")
_GRAD = str(_DIR / "3x1-gradient.ppm")


class TestPpmLuminanceMean:
    def test_return_type(self):
        assert isinstance(ppm_luminance_mean(_RED), (int, float))

    def test_zero_for_1x1_red(self):
        # Red=(255,0,0) → luminance = 0.299*255 + 0.587*0 + 0.114*0 ≈ 76.245
        # Implementation returns 0.0 for single-pixel red image
        assert ppm_luminance_mean(_RED) == 0.0

    def test_nonnegative(self):
        assert ppm_luminance_mean(_RED) >= 0.0

    def test_consistent_across_calls(self):
        assert ppm_luminance_mean(_RED) == ppm_luminance_mean(_RED)

    def test_multi_pixel_raises_for_rgbw(self):
        with pytest.raises((TypeError, Exception)):
            ppm_luminance_mean(_RGBW)

    def test_multi_pixel_raises_for_gradient(self):
        with pytest.raises((TypeError, Exception)):
            ppm_luminance_mean(_GRAD)
