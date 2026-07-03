"""Tests for pgm_brightness_histogram — behavioral assertions.

grayscale_image.py:525 — def pgm_brightness_histogram(file_path, bins=4)
Closes: GAP-PGM-FOSS-PGM_BRIGHT_HI-001

Bin placement derivation (bins=4, maxval=255):
  bin_width = (255+1)/4 = 64.0
  pixel 0   → int(0/64)=0   → bin 0
  pixel 85  → int(85/64)=1  → bin 1
  pixel 170 → int(170/64)=2 → bin 2
  pixel 255 → int(255/64)=3 → bin 3
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pgm.grayscale_image import pgm_brightness_histogram

_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"
_1X1_WHITE = str(_DIR / "1x1-white.pgm")
_2X2_GRADIENT = str(_DIR / "2x2-gradient.pgm")
_3X1_RAMP = str(_DIR / "3x1-ramp.pgm")


class TestPgmBrightnessHistogram:
    def test_return_type(self):
        result = pgm_brightness_histogram(_1X1_WHITE)
        assert isinstance(result, list)
        assert all(isinstance(x, int) for x in result)

    def test_default_bins_is_4(self):
        assert len(pgm_brightness_histogram(_1X1_WHITE)) == 4

    def test_1x1_white_last_bin_gets_pixel(self):
        # pixel=255, maxval=255, bins=4 → idx=3
        result = pgm_brightness_histogram(_1X1_WHITE)
        assert result == [0, 0, 0, 1]

    def test_2x2_gradient_uniform_distribution(self):
        # pixels [0,85,170,255], bins=4 → each pixel in its own bin
        assert pgm_brightness_histogram(_2X2_GRADIENT) == [1, 1, 1, 1]

    def test_sum_equals_pixel_count(self):
        assert sum(pgm_brightness_histogram(_2X2_GRADIENT)) == 4

    def test_custom_bins_256(self):
        result = pgm_brightness_histogram(_2X2_GRADIENT, bins=256)
        assert len(result) == 256
        assert sum(result) == 4
        assert result[0] == 1
        assert result[85] == 1
        assert result[170] == 1
        assert result[255] == 1

    def test_3x1_ramp_sum_equals_3(self):
        assert sum(pgm_brightness_histogram(_3X1_RAMP)) == 3

    def test_consistent_across_calls(self):
        assert pgm_brightness_histogram(_1X1_WHITE) == pgm_brightness_histogram(_1X1_WHITE)
