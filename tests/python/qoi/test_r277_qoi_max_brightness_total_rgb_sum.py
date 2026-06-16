"""Tests for qoi_max_brightness and qoi_total_rgb_sum (Sprint 67)."""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src" / "python"))

from qoi.qoi_parser import qoi_max_brightness, qoi_total_rgb_sum

QOI = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "qoi" / "valid"


class TestQoiMaxBrightness:
    def test_red(self):
        assert abs(qoi_max_brightness(QOI / "1x1-red.qoi") - 85.0) < 0.01

    def test_black(self):
        assert abs(qoi_max_brightness(QOI / "2x2-black.qoi") - 0.0) < 0.01

    def test_gradient(self):
        assert abs(qoi_max_brightness(QOI / "4x1-gradient.qoi") - 255.0) < 0.01

    def test_returns_float(self):
        assert isinstance(qoi_max_brightness(QOI / "1x1-red.qoi"), float)

    def test_nonnegative(self):
        for f in ["1x1-red.qoi", "2x2-black.qoi", "4x1-gradient.qoi"]:
            assert qoi_max_brightness(QOI / f) >= 0.0


class TestQoiTotalRgbSum:
    def test_red(self):
        assert qoi_total_rgb_sum(QOI / "1x1-red.qoi") == 255

    def test_black(self):
        assert qoi_total_rgb_sum(QOI / "2x2-black.qoi") == 0

    def test_gradient(self):
        assert qoi_total_rgb_sum(QOI / "4x1-gradient.qoi") == 1530

    def test_returns_int(self):
        assert isinstance(qoi_total_rgb_sum(QOI / "1x1-red.qoi"), int)

    def test_nonnegative(self):
        for f in ["1x1-red.qoi", "2x2-black.qoi", "4x1-gradient.qoi"]:
            assert qoi_total_rgb_sum(QOI / f) >= 0
