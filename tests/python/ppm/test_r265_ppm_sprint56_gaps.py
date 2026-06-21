"""Tests for PPM Sprint 56 gap closure.

Closes:
  GAP-PPM-FOSS-PPM_WIDTH-001   (Ppm Width)
  GAP-PPM-FOSS-PPM_HEIGHT-001  (Ppm Height)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ppm import ppm_width, ppm_height

_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"
_RED = str(_DIR / "1x1-red.ppm")
_RGBW = str(_DIR / "2x2-rgbw.ppm")


class TestPpmWidth:
    def test_return_type(self):
        assert isinstance(ppm_width(_RED), int)

    def test_exact_1_for_1x1(self):
        assert ppm_width(_RED) == 1

    def test_exact_2_for_2x2(self):
        assert ppm_width(_RGBW) == 2

    def test_positive(self):
        assert ppm_width(_RED) > 0

    def test_consistent_across_calls(self):
        assert ppm_width(_RED) == ppm_width(_RED)


class TestPpmHeight:
    def test_return_type(self):
        assert isinstance(ppm_height(_RED), int)

    def test_exact_1_for_1x1(self):
        assert ppm_height(_RED) == 1

    def test_exact_2_for_2x2(self):
        assert ppm_height(_RGBW) == 2

    def test_positive(self):
        assert ppm_height(_RED) > 0

    def test_consistent_across_calls(self):
        assert ppm_height(_RED) == ppm_height(_RED)
