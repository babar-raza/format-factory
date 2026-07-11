"""Tests for extended PGM grayscale analytics (pgm_row_intensity_variance)."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

GRADIENT = _REPO / "samples" / "by-format" / "pgm" / "valid" / "2x2-gradient.pgm"

from src.python.pgm.grayscale_image import pgm_row_intensity_variance


class TestPgmRowIntensityVariance:
    def test_returns_float(self):
        assert isinstance(pgm_row_intensity_variance(GRADIENT), float)

    def test_nonnegative(self):
        assert pgm_row_intensity_variance(GRADIENT) >= 0.0

    def test_gradient_has_variance(self):
        # 2x2 gradient has different rows → variance > 0
        assert pgm_row_intensity_variance(GRADIENT) > 0.0

    def test_accepts_string_path(self):
        assert isinstance(pgm_row_intensity_variance(str(GRADIENT)), float)
