"""
test_r185_qoi_probe_deepening.py — QOI probe + dimensions deepening tests

Sprint: PRODUCT-DEEPENING-RNEXT185-20260612-001
Gap closure: GAP-QOI-FOSS-PROBE_QOI-001
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.qoi.qoi_parser import (
    probe_qoi,
    qoi_dimensions,
    qoi_pixel_count,
    parse_qoi,
    parse_qoi_strict,
    QoiImage,
)

_SAMPLES = _REPO / "samples" / "by-format" / "qoi" / "valid"
_RED_1X1 = _SAMPLES / "1x1-red.qoi"
_BLACK_2X2 = _SAMPLES / "2x2-black.qoi"
_GRAD_4X1 = _SAMPLES / "4x1-gradient.qoi"


class TestQoiProbe:
    def test_probe_returns_dict(self):
        result = probe_qoi(str(_RED_1X1))
        assert isinstance(result, dict)

    def test_probe_exists_true(self):
        result = probe_qoi(str(_RED_1X1))
        assert result["exists"] is True

    def test_probe_valid_header_true(self):
        result = probe_qoi(str(_RED_1X1))
        assert result["valid_header"] is True

    def test_probe_width_height_1x1(self):
        result = probe_qoi(str(_RED_1X1))
        assert result["width"] == 1
        assert result["height"] == 1

    def test_probe_channels_rgba(self):
        result = probe_qoi(str(_RED_1X1))
        assert result["channels"] == 4

    def test_probe_size_bytes_positive(self):
        result = probe_qoi(str(_RED_1X1))
        assert result["file_size"] > 0


class TestQoiDimensions:
    def test_dimensions_1x1(self):
        d = qoi_dimensions(str(_RED_1X1))
        assert d["width"] == 1
        assert d["height"] == 1

    def test_pixel_count_1x1(self):
        assert qoi_pixel_count(str(_RED_1X1)) == 1

    def test_pixel_count_2x2(self):
        assert qoi_pixel_count(str(_BLACK_2X2)) == 4

    def test_pixel_count_4x1(self):
        assert qoi_pixel_count(str(_GRAD_4X1)) == 4

    def test_parse_qoi_strict_returns_image(self):
        img = parse_qoi_strict(str(_RED_1X1))
        assert isinstance(img, QoiImage)

    def test_parse_qoi_image_has_pixels(self):
        img = parse_qoi_strict(str(_RED_1X1))
        assert len(img.pixels) == 1

    def test_dimensions_channels_2x2(self):
        d = qoi_dimensions(str(_BLACK_2X2))
        assert d["channels"] >= 3
