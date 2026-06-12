"""
tests/python/qoi/test_r179_qoi_pixel_count.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT47-001
Tests for qoi_pixel_count() — total pixel count (width * height).
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.qoi.qoi_parser import qoi_pixel_count

SAMPLES = _REPO / "samples" / "by-format" / "qoi" / "valid"


class TestQoiPixelCount:
    def test_1x1_red_pixel_count(self):
        result = qoi_pixel_count(SAMPLES / "1x1-red.qoi")
        assert result == 1

    def test_2x2_black_pixel_count(self):
        result = qoi_pixel_count(SAMPLES / "2x2-black.qoi")
        assert result == 4

    def test_4x1_gradient_pixel_count(self):
        result = qoi_pixel_count(SAMPLES / "4x1-gradient.qoi")
        assert result == 4

    def test_returns_int(self):
        result = qoi_pixel_count(SAMPLES / "1x1-red.qoi")
        assert isinstance(result, int)

    def test_positive_pixel_count(self):
        result = qoi_pixel_count(SAMPLES / "2x2-black.qoi")
        assert result > 0

    def test_exported_from_init(self):
        from src.python.qoi import qoi_pixel_count as fn
        result = fn(SAMPLES / "2x2-black.qoi")
        assert result == 4
