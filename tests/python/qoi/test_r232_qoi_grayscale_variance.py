"""Tests for qoi_is_grayscale and qoi_brightness_variance.

Product deepening: QOI analytics — TC-H3-002-QOI / PDC-QOI-GRAY-VARIANCE-001.
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from qoi.qoi_parser import qoi_is_grayscale, qoi_brightness_variance, QoiImage
from qoi.qoi_encoder import encode_qoi_to_file


def _make_qoi(tmp_path, name, pixels, width, height, channels=3):
    img = QoiImage(
        width=width, height=height, channels=channels,
        colorspace=0, pixels=list(pixels), path="",
    )
    p = tmp_path / f"{name}.qoi"
    encode_qoi_to_file(img, str(p))
    return str(p)


class TestQoiIsGrayscale:
    def test_grayscale_pixels(self, tmp_path):
        pixels = [(100, 100, 100), (200, 200, 200)]
        p = _make_qoi(tmp_path, "gray", pixels, 2, 1)
        assert qoi_is_grayscale(p) is True

    def test_not_grayscale(self, tmp_path):
        pixels = [(255, 0, 0), (0, 255, 0)]
        p = _make_qoi(tmp_path, "color", pixels, 2, 1)
        assert qoi_is_grayscale(p) is False

    def test_returns_bool(self, tmp_path):
        pixels = [(50, 50, 50)]
        p = _make_qoi(tmp_path, "bool_t", pixels, 1, 1)
        assert isinstance(qoi_is_grayscale(p), bool)

    def test_single_pixel_gray(self, tmp_path):
        pixels = [(128, 128, 128)]
        p = _make_qoi(tmp_path, "one_gray", pixels, 1, 1)
        assert qoi_is_grayscale(p) is True

    def test_almost_gray(self, tmp_path):
        pixels = [(100, 100, 101)]
        p = _make_qoi(tmp_path, "almost", pixels, 1, 1)
        assert qoi_is_grayscale(p) is False


class TestQoiBrightnessVariance:
    def test_uniform_pixels(self, tmp_path):
        pixels = [(100, 100, 100)] * 4
        p = _make_qoi(tmp_path, "uniform", pixels, 2, 2)
        assert qoi_brightness_variance(p) == pytest.approx(0.0)

    def test_varied_pixels(self, tmp_path):
        pixels = [(0, 0, 0), (255, 255, 255)]
        p = _make_qoi(tmp_path, "varied", pixels, 2, 1)
        result = qoi_brightness_variance(p)
        assert result > 0

    def test_returns_float(self, tmp_path):
        pixels = [(10, 20, 30)]
        p = _make_qoi(tmp_path, "ft", pixels, 1, 1)
        assert isinstance(qoi_brightness_variance(p), float)

    def test_non_negative(self, tmp_path):
        pixels = [(0, 0, 0)]
        p = _make_qoi(tmp_path, "nn", pixels, 1, 1)
        assert qoi_brightness_variance(p) >= 0.0

    def test_single_pixel_zero_variance(self, tmp_path):
        pixels = [(42, 42, 42)]
        p = _make_qoi(tmp_path, "single", pixels, 1, 1)
        assert qoi_brightness_variance(p) == pytest.approx(0.0)
