"""
tests/python/qoi/test_r176_qoi_dimensions.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT44-001
Tests for qoi_dimensions() — return width/height/channels/colorspace from QOI header.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.qoi.qoi_parser import qoi_dimensions

SAMPLES = _REPO / "samples" / "by-format" / "qoi" / "valid"


class TestQoiDimensions:
    def test_1x1_red_dimensions(self):
        result = qoi_dimensions(SAMPLES / "1x1-red.qoi")
        assert result["width"] == 1
        assert result["height"] == 1
        assert result["channels"] == 4
        assert result["colorspace"] == 0

    def test_2x2_black_dimensions(self):
        result = qoi_dimensions(SAMPLES / "2x2-black.qoi")
        assert result["width"] == 2
        assert result["height"] == 2
        assert result["channels"] == 4

    def test_4x1_gradient_dimensions(self):
        result = qoi_dimensions(SAMPLES / "4x1-gradient.qoi")
        assert result["width"] == 4
        assert result["height"] == 1
        assert result["channels"] == 3

    def test_returns_dict(self):
        result = qoi_dimensions(SAMPLES / "1x1-red.qoi")
        assert isinstance(result, dict)
        assert set(result.keys()) == {"width", "height", "channels", "colorspace"}

    def test_all_values_are_int(self):
        result = qoi_dimensions(SAMPLES / "1x1-red.qoi")
        for k, v in result.items():
            assert isinstance(v, int), f"{k} should be int, got {type(v)}"

    def test_exported_from_init(self):
        from src.python.qoi import qoi_dimensions as fn
        result = fn(SAMPLES / "1x1-red.qoi")
        assert result["width"] == 1
        assert result["height"] == 1
