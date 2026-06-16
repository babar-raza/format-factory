"""Tests for qoi_avg_rgb_value and qoi_red_dominance_ratio (Sprint 26)."""
import sys
from pathlib import Path
import struct

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from qoi import qoi_avg_rgb_value, qoi_red_dominance_ratio


def _make_qoi(tmp_path, name, pixels, width, height):
    """Write a minimal QOI file."""
    p = tmp_path / f"{name}.qoi"
    # QOI header: magic, width, height, channels, colorspace
    header = b"qoif"
    header += struct.pack(">II", width, height)
    header += bytes([3, 0])  # channels=3 (RGB), colorspace=0
    # Encode pixels using QOI_OP_RGB for each
    data = bytearray()
    for pixel in pixels:
        data += bytes([0xFE, pixel[0], pixel[1], pixel[2]])  # QOI_OP_RGB
    # End marker
    end = bytes([0, 0, 0, 0, 0, 0, 0, 1])
    p.write_bytes(header + bytes(data) + end)
    return str(p)


class TestQoiAvgRgbValue:
    def test_return_type(self, tmp_path):
        p = _make_qoi(tmp_path, "rt", [(100, 150, 200)], 1, 1)
        assert isinstance(qoi_avg_rgb_value(p), float)

    def test_single_pixel_exact(self, tmp_path):
        # avg of (90, 180, 270 clipped to 255 -> 90, 180, 255) — use clean values
        # (120, 120, 120) → (120+120+120)/3 = 120.0
        p = _make_qoi(tmp_path, "sp", [(120, 120, 120)], 1, 1)
        assert qoi_avg_rgb_value(p) == 120.0

    def test_nonnegative(self, tmp_path):
        p = _make_qoi(tmp_path, "nn", [(50, 100, 150)], 1, 1)
        assert qoi_avg_rgb_value(p) >= 0.0

    def test_two_pixels(self, tmp_path):
        # (0, 0, 0) + (255, 255, 255) → total=1530, count=6 → 255.0
        p = _make_qoi(tmp_path, "tp", [(0, 0, 0), (255, 255, 255)], 2, 1)
        assert qoi_avg_rgb_value(p) == 127.5

    def test_pure_red(self, tmp_path):
        # (255, 0, 0) → avg = 255/3 = 85.0
        p = _make_qoi(tmp_path, "pr", [(255, 0, 0)], 1, 1)
        assert qoi_avg_rgb_value(p) == 85.0


class TestQoiRedDominanceRatio:
    def test_return_type(self, tmp_path):
        p = _make_qoi(tmp_path, "rt2", [(100, 100, 100)], 1, 1)
        assert isinstance(qoi_red_dominance_ratio(p), float)

    def test_pure_red_is_one_third(self, tmp_path):
        # (255, 0, 0): red=255, total=255 → ratio = 255/255 = 1.0
        p = _make_qoi(tmp_path, "pr2", [(255, 0, 0)], 1, 1)
        assert qoi_red_dominance_ratio(p) == 1.0

    def test_equal_channels_is_one_third(self, tmp_path):
        # (100, 100, 100): red=100, total=300 → ratio = 100/300 ≈ 0.333
        p = _make_qoi(tmp_path, "ec", [(100, 100, 100)], 1, 1)
        result = qoi_red_dominance_ratio(p)
        assert abs(result - 1/3) < 0.001

    def test_range_0_to_1(self, tmp_path):
        p = _make_qoi(tmp_path, "r01", [(50, 100, 150)], 1, 1)
        r = qoi_red_dominance_ratio(p)
        assert 0.0 <= r <= 1.0

    def test_no_red_returns_zero(self, tmp_path):
        # (0, 100, 200): red=0 → ratio = 0.0
        p = _make_qoi(tmp_path, "nr2", [(0, 100, 200)], 1, 1)
        assert qoi_red_dominance_ratio(p) == 0.0
