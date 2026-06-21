"""Tests for QOI Sprint 74 gap closure.

Closes:
  GAP-QOI-FOSS-QOI_TOTAL_CH-001   (Qoi Total Channel Sum)
  GAP-QOI-FOSS-QOI_IS_RGB_O-001   (Qoi Is Rgb Only)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.qoi import qoi_total_channel_sum, qoi_is_rgb_only

_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"
_RED = str(_DIR / "1x1-red.qoi")
_BLACK = str(_DIR / "2x2-black.qoi")
_GRAD = str(_DIR / "4x1-gradient.qoi")


class TestQoiTotalChannelSum:
    def test_return_type(self):
        assert isinstance(qoi_total_channel_sum(_RED), int)

    def test_exact_510_for_1x1_red(self):
        assert qoi_total_channel_sum(_RED) == 510

    def test_exact_1020_for_2x2_black(self):
        assert qoi_total_channel_sum(_BLACK) == 1020

    def test_exact_1530_for_gradient(self):
        assert qoi_total_channel_sum(_GRAD) == 1530

    def test_positive(self):
        assert qoi_total_channel_sum(_RED) > 0

    def test_consistent_across_calls(self):
        assert qoi_total_channel_sum(_RED) == qoi_total_channel_sum(_RED)


class TestQoiIsRgbOnly:
    def test_return_type(self):
        assert isinstance(qoi_is_rgb_only(_RED), bool)

    def test_false_for_1x1_red(self):
        assert qoi_is_rgb_only(_RED) is False

    def test_false_for_2x2_black(self):
        assert qoi_is_rgb_only(_BLACK) is False

    def test_true_for_gradient(self):
        assert qoi_is_rgb_only(_GRAD) is True

    def test_is_boolean(self):
        assert qoi_is_rgb_only(_RED) in (True, False)

    def test_consistent_across_calls(self):
        assert qoi_is_rgb_only(_RED) == qoi_is_rgb_only(_RED)
