"""Tests for pgm_has_any_zero and pgm_is_all_bright (Sprint 42)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pgm import pgm_has_any_zero, pgm_is_all_bright

_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"
_WHITE = str(_DIR / "1x1-white.pgm")      # 1x1 [255]: no zeros, all bright
_GRAD = str(_DIR / "2x2-gradient.pgm")    # 2x2 [0,85,170,255]: has zero, not all bright
_RAMP = str(_DIR / "3x1-ramp.pgm")        # 3x1 [0,128,255]: has zero, not all bright


class TestPgmHasAnyZero:
    def test_return_type(self):
        assert isinstance(pgm_has_any_zero(_WHITE), bool)

    def test_false_for_all_bright(self):
        # 1x1-white.pgm: pixel=[255], no zeros
        assert pgm_has_any_zero(_WHITE) is False

    def test_true_for_gradient(self):
        # 2x2-gradient: pixels=[0,85,170,255] — has a zero
        assert pgm_has_any_zero(_GRAD) is True

    def test_true_for_ramp(self):
        # 3x1-ramp: pixels=[0,128,255] — has a zero
        assert pgm_has_any_zero(_RAMP) is True

    def test_consistent_across_calls(self):
        assert pgm_has_any_zero(_GRAD) == pgm_has_any_zero(_GRAD)

    def test_false_is_not_none(self):
        result = pgm_has_any_zero(_WHITE)
        assert result is False
        assert result is not None


class TestPgmIsAllBright:
    def test_return_type(self):
        assert isinstance(pgm_is_all_bright(_WHITE), bool)

    def test_true_for_all_white(self):
        # 1x1-white.pgm: [255] >= 255//2=127 -> all bright -> True
        assert pgm_is_all_bright(_WHITE) is True

    def test_false_for_gradient(self):
        # 2x2-gradient: [0,85,170,255] — 0 < 127 -> not all bright -> False
        assert pgm_is_all_bright(_GRAD) is False

    def test_false_for_ramp(self):
        # 3x1-ramp: [0,128,255] — 0 < 127 -> not all bright -> False
        assert pgm_is_all_bright(_RAMP) is False

    def test_consistent_across_calls(self):
        assert pgm_is_all_bright(_WHITE) == pgm_is_all_bright(_WHITE)

    def test_true_is_not_none(self):
        result = pgm_is_all_bright(_WHITE)
        assert result is True
        assert result is not None
