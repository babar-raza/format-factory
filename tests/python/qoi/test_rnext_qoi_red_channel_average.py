"""Tests for qoi_red_channel_average function."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from qoi.qoi_parser import qoi_red_channel_average, QoiImage
from qoi.qoi_encoder import encode_qoi_to_file


def _make_qoi(tmp_path, pixels, width, height, channels=3):
    """Create a QOI file from pixel tuples."""
    img = QoiImage(
        width=width, height=height, channels=channels,
        colorspace=0, pixels=list(pixels), path="",
    )
    p = tmp_path / "test.qoi"
    encode_qoi_to_file(img, str(p))
    return str(p)


class TestQoiRedChannelAverage:
    def test_all_red(self, tmp_path):
        pixels = [(255, 0, 0)] * 4
        path = _make_qoi(tmp_path, pixels, 2, 2)
        assert qoi_red_channel_average(path) == pytest.approx(255.0)

    def test_all_green(self, tmp_path):
        pixels = [(0, 255, 0)] * 4
        path = _make_qoi(tmp_path, pixels, 2, 2)
        assert qoi_red_channel_average(path) == pytest.approx(0.0)

    def test_all_blue(self, tmp_path):
        pixels = [(0, 0, 255)] * 4
        path = _make_qoi(tmp_path, pixels, 2, 2)
        assert qoi_red_channel_average(path) == pytest.approx(0.0)

    def test_mixed_colors(self, tmp_path):
        pixels = [(100, 0, 0), (200, 0, 0)]
        path = _make_qoi(tmp_path, pixels, 2, 1)
        assert qoi_red_channel_average(path) == pytest.approx(150.0)

    def test_white_pixels(self, tmp_path):
        pixels = [(255, 255, 255)] * 3
        path = _make_qoi(tmp_path, pixels, 3, 1)
        assert qoi_red_channel_average(path) == pytest.approx(255.0)

    def test_black_pixels(self, tmp_path):
        pixels = [(0, 0, 0)] * 2
        path = _make_qoi(tmp_path, pixels, 2, 1)
        assert qoi_red_channel_average(path) == pytest.approx(0.0)

    def test_single_pixel(self, tmp_path):
        pixels = [(42, 100, 200)]
        path = _make_qoi(tmp_path, pixels, 1, 1)
        assert qoi_red_channel_average(path) == pytest.approx(42.0)

    def test_importable_from_package(self):
        from qoi import qoi_red_channel_average as fn
        assert callable(fn)
