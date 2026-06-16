"""Tests for pgm_min_brightness and pgm_is_bright (Sprint 62)."""
import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src" / "python"))

from pgm.pgm_parser import pgm_min_brightness, pgm_is_bright

PGM = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "pgm" / "valid"


class TestPgmMinBrightness:
    def test_1x1_white(self):
        assert pgm_min_brightness(PGM / "1x1-white.pgm") == 255

    def test_2x2_gradient(self):
        assert pgm_min_brightness(PGM / "2x2-gradient.pgm") == 0

    def test_3x1_ramp(self):
        assert pgm_min_brightness(PGM / "3x1-ramp.pgm") == 0

    def test_returns_int(self):
        assert isinstance(pgm_min_brightness(PGM / "1x1-white.pgm"), int)

    def test_nonnegative(self):
        for f in ["1x1-white.pgm", "2x2-gradient.pgm", "3x1-ramp.pgm"]:
            assert pgm_min_brightness(PGM / f) >= 0


class TestPgmIsBright:
    def test_1x1_white_is_bright(self):
        assert pgm_is_bright(PGM / "1x1-white.pgm") is True

    def test_2x2_gradient_not_bright(self):
        assert pgm_is_bright(PGM / "2x2-gradient.pgm") is False

    def test_3x1_ramp_not_bright(self):
        assert pgm_is_bright(PGM / "3x1-ramp.pgm") is False

    def test_returns_bool(self):
        assert isinstance(pgm_is_bright(PGM / "1x1-white.pgm"), bool)

    def test_true_for_all_white(self):
        assert pgm_is_bright(PGM / "1x1-white.pgm") is True
