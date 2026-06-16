"""Tests for ppm_is_dark and ppm_red_channel_sum (Sprint 26)."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ppm import ppm_is_dark, ppm_red_channel_sum, write_ppm


def _make_ppm(tmp_path, name, pixels, width, height, maxval=255):
    p = tmp_path / f"{name}.ppm"
    write_ppm(pixels, width, height, maxval, str(p))
    return str(p)


class TestPpmIsDark:
    def test_dark_image(self, tmp_path):
        # Average = (10+10+10)/3 = 10 < 128 → dark
        p = _make_ppm(tmp_path, "di", [(10, 10, 10), (20, 20, 20)], 2, 1)
        assert ppm_is_dark(p) is True

    def test_bright_image(self, tmp_path):
        # Average = (200+200+200)/3 = 200 > 128 → not dark
        p = _make_ppm(tmp_path, "bi", [(200, 200, 200), (220, 220, 220)], 2, 1)
        assert ppm_is_dark(p) is False

    def test_return_type(self, tmp_path):
        p = _make_ppm(tmp_path, "rt", [(100, 100, 100)], 1, 1)
        assert isinstance(ppm_is_dark(p), bool)

    def test_threshold_below_128(self, tmp_path):
        # avg = 127 < 128 → dark
        p = _make_ppm(tmp_path, "th", [(127, 127, 127)], 1, 1)
        assert ppm_is_dark(p) is True

    def test_threshold_above_128(self, tmp_path):
        # avg = 129 > 128 → not dark
        p = _make_ppm(tmp_path, "ta", [(129, 129, 129)], 1, 1)
        assert ppm_is_dark(p) is False


class TestPpmRedChannelSum:
    def test_all_red(self, tmp_path):
        # 2 pixels with red=255 → sum = 510
        p = _make_ppm(tmp_path, "ar", [(255, 0, 0), (255, 0, 0)], 2, 1)
        assert ppm_red_channel_sum(p) == 510

    def test_no_red(self, tmp_path):
        # red channel = 0 for all pixels
        p = _make_ppm(tmp_path, "nr", [(0, 100, 200), (0, 50, 150)], 2, 1)
        assert ppm_red_channel_sum(p) == 0

    def test_return_type(self, tmp_path):
        p = _make_ppm(tmp_path, "rt2", [(100, 50, 25)], 1, 1)
        assert isinstance(ppm_red_channel_sum(p), int)

    def test_single_pixel(self, tmp_path):
        p = _make_ppm(tmp_path, "sp", [(42, 0, 0)], 1, 1)
        assert ppm_red_channel_sum(p) == 42

    def test_mixed_pixels(self, tmp_path):
        # 100 + 200 = 300
        p = _make_ppm(tmp_path, "mp", [(100, 50, 25), (200, 150, 75)], 2, 1)
        assert ppm_red_channel_sum(p) == 300
