"""Tests for qoi_green_ratio and qoi_blue_ratio (Sprint 57)."""
import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src" / "python"))

from qoi.qoi_parser import qoi_green_ratio, qoi_blue_ratio

QOI = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "qoi" / "valid"


class TestQoiGreenRatio:
    def test_red_image_has_zero_green(self):
        assert qoi_green_ratio(QOI / "1x1-red.qoi") == 0.0

    def test_black_image_has_zero_green(self):
        assert qoi_green_ratio(QOI / "2x2-black.qoi") == 0.0

    def test_gradient_has_equal_green(self):
        result = qoi_green_ratio(QOI / "4x1-gradient.qoi")
        assert abs(result - 1/3) < 1e-6

    def test_returns_float(self):
        result = qoi_green_ratio(QOI / "1x1-red.qoi")
        assert isinstance(result, float)

    def test_nonnegative(self):
        for f in ["1x1-red.qoi", "2x2-black.qoi", "4x1-gradient.qoi"]:
            assert qoi_green_ratio(QOI / f) >= 0.0


class TestQoiBlueRatio:
    def test_red_image_has_zero_blue(self):
        assert qoi_blue_ratio(QOI / "1x1-red.qoi") == 0.0

    def test_black_image_has_zero_blue(self):
        assert qoi_blue_ratio(QOI / "2x2-black.qoi") == 0.0

    def test_gradient_has_equal_blue(self):
        result = qoi_blue_ratio(QOI / "4x1-gradient.qoi")
        assert abs(result - 1/3) < 1e-6

    def test_returns_float(self):
        result = qoi_blue_ratio(QOI / "1x1-red.qoi")
        assert isinstance(result, float)

    def test_nonnegative(self):
        for f in ["1x1-red.qoi", "2x2-black.qoi", "4x1-gradient.qoi"]:
            assert qoi_blue_ratio(QOI / f) >= 0.0
