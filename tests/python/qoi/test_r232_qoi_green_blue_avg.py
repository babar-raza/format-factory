"""Tests for qoi_green_channel_average and qoi_blue_channel_average.

Product deepening: QOI analytics — TC-H3-002-QOI / PDC-QOI-GREEN-BLUE-001.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.qoi import (
    qoi_green_channel_average,
    qoi_blue_channel_average,
    encode_qoi_to_file,
    QoiImage,
)


def _make_qoi(tmp_path, name, pixels, w, h, channels=4):
    img = QoiImage(width=w, height=h, channels=channels, colorspace=0, pixels=pixels)
    path = tmp_path / f"{name}.qoi"
    encode_qoi_to_file(img, str(path))
    return path


class TestQoiGreenChannelAverage:
    def test_pure_green(self, tmp_path):
        pixels = [(0, 255, 0, 255)] * 4
        f = _make_qoi(tmp_path, "green", pixels, 2, 2)
        assert qoi_green_channel_average(f) == 255.0

    def test_no_green(self, tmp_path):
        pixels = [(255, 0, 128, 255)] * 4
        f = _make_qoi(tmp_path, "no_green", pixels, 2, 2)
        assert qoi_green_channel_average(f) == 0.0

    def test_mixed(self, tmp_path):
        pixels = [(0, 100, 0, 255), (0, 200, 0, 255)]
        f = _make_qoi(tmp_path, "mix", pixels, 2, 1)
        assert qoi_green_channel_average(f) == 150.0

    def test_returns_float(self, tmp_path):
        pixels = [(10, 20, 30, 255)]
        f = _make_qoi(tmp_path, "type", pixels, 1, 1)
        assert isinstance(qoi_green_channel_average(f), float)

    def test_range(self, tmp_path):
        pixels = [(50, 128, 200, 255)]
        f = _make_qoi(tmp_path, "range", pixels, 1, 1)
        result = qoi_green_channel_average(f)
        assert 0.0 <= result <= 255.0


class TestQoiBlueChannelAverage:
    def test_pure_blue(self, tmp_path):
        pixels = [(0, 0, 255, 255)] * 4
        f = _make_qoi(tmp_path, "blue", pixels, 2, 2)
        assert qoi_blue_channel_average(f) == 255.0

    def test_no_blue(self, tmp_path):
        pixels = [(255, 128, 0, 255)] * 4
        f = _make_qoi(tmp_path, "no_blue", pixels, 2, 2)
        assert qoi_blue_channel_average(f) == 0.0

    def test_mixed(self, tmp_path):
        pixels = [(0, 0, 50, 255), (0, 0, 150, 255)]
        f = _make_qoi(tmp_path, "mix2", pixels, 2, 1)
        assert qoi_blue_channel_average(f) == 100.0

    def test_returns_float(self, tmp_path):
        pixels = [(10, 20, 30, 255)]
        f = _make_qoi(tmp_path, "type2", pixels, 1, 1)
        assert isinstance(qoi_blue_channel_average(f), float)

    def test_range(self, tmp_path):
        pixels = [(50, 128, 200, 255)]
        f = _make_qoi(tmp_path, "range2", pixels, 1, 1)
        result = qoi_blue_channel_average(f)
        assert 0.0 <= result <= 255.0
