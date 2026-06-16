"""Tests for qoi_has_any_black and qoi_max_channel_average (Sprint 43)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.qoi import qoi_has_any_black, qoi_max_channel_average

_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"
_RED = str(_DIR / "1x1-red.qoi")       # (255,0,0,255): no black, max_avg=255.0
_BLACK = str(_DIR / "2x2-black.qoi")   # all (0,0,0,255): has black, max_avg=0.0
_GRAD = str(_DIR / "4x1-gradient.qoi") # grayscale ramp: has black, max_avg=127.5


class TestQoiHasAnyBlack:
    def test_return_type(self):
        assert isinstance(qoi_has_any_black(_RED), bool)

    def test_false_for_red(self):
        # 1x1-red: (255,0,0) — R is max, not black
        assert qoi_has_any_black(_RED) is False

    def test_true_for_black(self):
        # 2x2-black: all (0,0,0) — pure black pixels
        assert qoi_has_any_black(_BLACK) is True

    def test_true_for_gradient(self):
        # 4x1-gradient: first pixel is (0,0,0) — pure black
        assert qoi_has_any_black(_GRAD) is True

    def test_consistent_across_calls(self):
        assert qoi_has_any_black(_BLACK) == qoi_has_any_black(_BLACK)

    def test_false_is_not_none(self):
        result = qoi_has_any_black(_RED)
        assert result is False
        assert result is not None


class TestQoiMaxChannelAverage:
    def test_return_type(self):
        assert isinstance(qoi_max_channel_average(_RED), float)

    def test_exact_255_for_red(self):
        # 1x1-red: R=255, G=0, B=0 -> max(255.0, 0.0, 0.0) = 255.0
        assert qoi_max_channel_average(_RED) == 255.0

    def test_exact_0_for_black(self):
        # 2x2-black: all R=G=B=0 -> max(0.0, 0.0, 0.0) = 0.0
        assert qoi_max_channel_average(_BLACK) == 0.0

    def test_exact_127_5_for_gradient(self):
        # 4x1-gradient: (0,0,0),(85,85,85),(170,170,170),(255,255,255)
        # avg_R = avg_G = avg_B = (0+85+170+255)/4 = 127.5
        assert qoi_max_channel_average(_GRAD) == 127.5

    def test_nonnegative(self):
        assert qoi_max_channel_average(_RED) >= 0.0

    def test_consistent_across_calls(self):
        assert qoi_max_channel_average(_GRAD) == qoi_max_channel_average(_GRAD)
