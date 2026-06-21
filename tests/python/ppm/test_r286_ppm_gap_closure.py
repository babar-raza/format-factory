"""
Tests for PPM gap closure (2 FOSS functions).
Closes: GAP-PPM-FOSS-PPM_WARM_PIX-001, GAP-PPM-FOSS-PPM_COOL_PIX-001

Known sample values:
  1x1-red.ppm: warm=1, cool=0
  2x2-rgbw.ppm: warm=1, cool=1
  3x1-gradient.ppm: warm=0, cool=0
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ppm.ppm_parser import ppm_warm_pixel_count, ppm_cool_pixel_count

_PPM = _REPO / "samples" / "by-format" / "ppm" / "valid"
_RED = _PPM / "1x1-red.ppm"
_RGBW = _PPM / "2x2-rgbw.ppm"
_GRADIENT = _PPM / "3x1-gradient.ppm"


class TestPpmWarmPixelCount:
    def test_returns_int(self):
        assert isinstance(ppm_warm_pixel_count(_RED), int)

    def test_nonnegative(self):
        for p in [_RED, _RGBW, _GRADIENT]:
            assert ppm_warm_pixel_count(p) >= 0

    def test_red_is_warm(self):
        # 1x1-red: single red pixel → warm
        assert ppm_warm_pixel_count(_RED) == 1

    def test_rgbw_has_warm(self):
        # 2x2-rgbw has 1 warm pixel
        assert ppm_warm_pixel_count(_RGBW) == 1

    def test_gradient_no_warm(self):
        # 3x1-gradient: no warm pixels
        assert ppm_warm_pixel_count(_GRADIENT) == 0

    def test_all_return_int(self):
        for p in [_RED, _RGBW, _GRADIENT]:
            assert isinstance(ppm_warm_pixel_count(p), int)


class TestPpmCoolPixelCount:
    def test_returns_int(self):
        assert isinstance(ppm_cool_pixel_count(_RED), int)

    def test_nonnegative(self):
        for p in [_RED, _RGBW, _GRADIENT]:
            assert ppm_cool_pixel_count(p) >= 0

    def test_red_no_cool(self):
        # 1x1-red: red pixel is not cool
        assert ppm_cool_pixel_count(_RED) == 0

    def test_rgbw_has_cool(self):
        # 2x2-rgbw has 1 cool pixel (blue)
        assert ppm_cool_pixel_count(_RGBW) == 1

    def test_gradient_no_cool(self):
        assert ppm_cool_pixel_count(_GRADIENT) == 0

    def test_all_return_int(self):
        for p in [_RED, _RGBW, _GRADIENT]:
            assert isinstance(ppm_cool_pixel_count(p), int)
