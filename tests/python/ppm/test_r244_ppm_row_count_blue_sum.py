"""Tests for ppm_row_count and ppm_blue_channel_sum (Sprint 34)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ppm import write_ppm, ppm_row_count, ppm_blue_channel_sum


def _make_ppm(tmp_path, name, w, h, pixels):
    p = tmp_path / f"{name}.ppm"
    write_ppm(pixels, w, h, 255, str(p))
    return p


class TestPpmRowCount:
    def test_return_type(self, tmp_path):
        p = _make_ppm(tmp_path, "rt", 3, 2, [(0, 0, 0)] * 6)
        assert isinstance(ppm_row_count(p), int)

    def test_exact_height(self, tmp_path):
        p = _make_ppm(tmp_path, "eh", 4, 3, [(0, 0, 0)] * 12)
        assert ppm_row_count(p) == 3

    def test_single_row(self, tmp_path):
        p = _make_ppm(tmp_path, "sr", 5, 1, [(0, 0, 0)] * 5)
        assert ppm_row_count(p) == 1

    def test_square_image(self, tmp_path):
        p = _make_ppm(tmp_path, "sq", 4, 4, [(0, 0, 0)] * 16)
        assert ppm_row_count(p) == 4

    def test_nonnegative(self, tmp_path):
        p = _make_ppm(tmp_path, "nn", 2, 2, [(10, 20, 30)] * 4)
        assert ppm_row_count(p) >= 0


class TestPpmBlueChannelSum:
    def test_return_type(self, tmp_path):
        p = _make_ppm(tmp_path, "rt2", 2, 1, [(0, 0, 50), (0, 0, 50)])
        assert isinstance(ppm_blue_channel_sum(p), int)

    def test_zero_blue(self, tmp_path):
        p = _make_ppm(tmp_path, "zb", 2, 1, [(255, 0, 0), (0, 255, 0)])
        assert ppm_blue_channel_sum(p) == 0

    def test_exact_sum(self, tmp_path):
        # blue values: 100 + 200 = 300
        p = _make_ppm(tmp_path, "es", 2, 1, [(0, 0, 100), (0, 0, 200)])
        assert ppm_blue_channel_sum(p) == 300

    def test_all_same_blue(self, tmp_path):
        # 4 pixels with blue=50 -> sum=200
        p = _make_ppm(tmp_path, "asb", 2, 2, [(0, 0, 50)] * 4)
        assert ppm_blue_channel_sum(p) == 200

    def test_nonnegative(self, tmp_path):
        p = _make_ppm(tmp_path, "nn2", 2, 1, [(10, 20, 30), (40, 50, 60)])
        assert ppm_blue_channel_sum(p) >= 0
