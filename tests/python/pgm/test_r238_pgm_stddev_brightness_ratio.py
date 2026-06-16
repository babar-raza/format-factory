"""Tests for pgm_standard_deviation and pgm_brightness_ratio.

Product deepening: PGM analytics — R238.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO / "src" / "python"))

from pgm import pgm_standard_deviation, pgm_brightness_ratio

_PGM_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"


def _first_pgm():
    files = sorted(_PGM_DIR.glob("*.pgm"))
    assert files, f"No PGM samples in {_PGM_DIR}"
    return str(files[0])


class TestPgmStandardDeviation:
    def test_returns_float(self):
        assert isinstance(pgm_standard_deviation(_first_pgm()), float)

    def test_nonnegative(self):
        assert pgm_standard_deviation(_first_pgm()) >= 0.0

    def test_reasonable(self):
        assert pgm_standard_deviation(_first_pgm()) < 256.0


class TestPgmBrightnessRatio:
    def test_returns_float(self):
        assert isinstance(pgm_brightness_ratio(_first_pgm()), float)

    def test_range(self):
        result = pgm_brightness_ratio(_first_pgm())
        assert 0.0 <= result <= 1.0

    def test_positive(self):
        assert pgm_brightness_ratio(_first_pgm()) >= 0.0
