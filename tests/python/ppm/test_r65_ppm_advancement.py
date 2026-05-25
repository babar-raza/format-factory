"""
test_r65_ppm_advancement.py -- R65 Train I: PPM format track advancement.

New capability: ppm_pixel_count(ppm_doc) -- total pixel count (width * height).

R65 Sprint: Train I -- PPM stats module expansion
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.ppm.ppm_stats import ppm_pixel_count


# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------

def _make_ppm(width: int = 0, height: int = 0, maxval: int = 255) -> dict:
    """Build a minimal PPM document dict."""
    return {"width": width, "height": height, "maxval": maxval, "magic": "P3"}


# ---------------------------------------------------------------------------
# ppm_pixel_count tests
# ---------------------------------------------------------------------------

class TestPpmPixelCount:
    """Tests for ppm_pixel_count()."""

    def test_zero_dimensions(self):
        doc = _make_ppm(0, 0)
        assert ppm_pixel_count(doc) == 0

    def test_standard_image(self):
        doc = _make_ppm(640, 480)
        assert ppm_pixel_count(doc) == 640 * 480

    def test_square_image(self):
        doc = _make_ppm(100, 100)
        assert ppm_pixel_count(doc) == 10000

    def test_single_pixel(self):
        doc = _make_ppm(1, 1)
        assert ppm_pixel_count(doc) == 1

    def test_wide_image(self):
        doc = _make_ppm(1920, 1)
        assert ppm_pixel_count(doc) == 1920

    def test_tall_image(self):
        doc = _make_ppm(1, 1080)
        assert ppm_pixel_count(doc) == 1080

    def test_large_image(self):
        doc = _make_ppm(3840, 2160)
        assert ppm_pixel_count(doc) == 3840 * 2160

    def test_returns_int(self):
        doc = _make_ppm(10, 20)
        result = ppm_pixel_count(doc)
        assert isinstance(result, int)
        assert result == 200
