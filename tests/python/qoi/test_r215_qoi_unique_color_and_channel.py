"""Tests for qoi_unique_color_count() and qoi_channel_count().

Sprint: product-deepening-rnext85
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.qoi.qoi_parser import qoi_unique_color_count, qoi_channel_count

QOI_SAMPLES = _REPO / "samples" / "by-format" / "qoi" / "valid"


class TestQoiUniqueColorCount:
    def test_import(self):
        assert callable(qoi_unique_color_count)

    def test_red_image_has_one_color(self):
        assert qoi_unique_color_count(QOI_SAMPLES / "1x1-red.qoi") == 1

    def test_black_image_has_one_color(self):
        assert qoi_unique_color_count(QOI_SAMPLES / "2x2-black.qoi") == 1

    def test_gradient_has_four_colors(self):
        assert qoi_unique_color_count(QOI_SAMPLES / "4x1-gradient.qoi") == 4

    def test_returns_int(self):
        result = qoi_unique_color_count(QOI_SAMPLES / "1x1-red.qoi")
        assert isinstance(result, int)

    def test_positive(self):
        for sample in QOI_SAMPLES.iterdir():
            if sample.suffix == ".qoi":
                assert qoi_unique_color_count(sample) >= 1


class TestQoiChannelCount:
    def test_import(self):
        assert callable(qoi_channel_count)

    def test_red_image_has_four_channels(self):
        assert qoi_channel_count(QOI_SAMPLES / "1x1-red.qoi") == 4

    def test_black_image_has_four_channels(self):
        assert qoi_channel_count(QOI_SAMPLES / "2x2-black.qoi") == 4

    def test_gradient_has_three_channels(self):
        assert qoi_channel_count(QOI_SAMPLES / "4x1-gradient.qoi") == 3

    def test_returns_int(self):
        result = qoi_channel_count(QOI_SAMPLES / "1x1-red.qoi")
        assert isinstance(result, int)

    def test_valid_channel_values(self):
        for sample in QOI_SAMPLES.iterdir():
            if sample.suffix == ".qoi":
                assert qoi_channel_count(sample) in (3, 4)

    def test_nonnegative(self):
        for sample in QOI_SAMPLES.iterdir():
            if sample.suffix == ".qoi":
                assert qoi_channel_count(sample) > 0
