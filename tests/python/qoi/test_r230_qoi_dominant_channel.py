"""Tests for qoi_dominant_channel and qoi_min_max_brightness.

Product deepening: QOI analytics — TC-H3-001 / PDC-QOI-DOMINANT-CHANNEL-001.
"""
import struct
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.qoi import (
    qoi_dominant_channel,
    qoi_min_max_brightness,
    qoi_average_brightness,
)

SAMPLES = _REPO / "samples" / "by-format" / "qoi" / "valid"


def _make_qoi_bytes(width, height, channels, pixels):
    """Build a minimal QOI file in memory."""
    header = b"qoif"
    header += struct.pack(">II", width, height)
    header += bytes([channels, 0])  # channels + colorspace
    # Encode all pixels as QOI_OP_RGBA (0xff tag)
    body = b""
    for px in pixels:
        body += b"\xff" + bytes(px[:4] if channels == 4 else list(px[:3]) + [255])
    # End marker: 7 zero bytes + 0x01
    end = b"\x00" * 7 + b"\x01"
    return header + body + end


class TestQoiDominantChannelSynthetic:
    def test_red_dominant(self, tmp_path):
        f = tmp_path / "red.qoi"
        f.write_bytes(_make_qoi_bytes(1, 1, 3, [(255, 0, 0)]))
        assert qoi_dominant_channel(f) == "red"

    def test_green_dominant(self, tmp_path):
        f = tmp_path / "green.qoi"
        f.write_bytes(_make_qoi_bytes(1, 1, 3, [(0, 255, 0)]))
        assert qoi_dominant_channel(f) == "green"

    def test_blue_dominant(self, tmp_path):
        f = tmp_path / "blue.qoi"
        f.write_bytes(_make_qoi_bytes(1, 1, 3, [(0, 0, 255)]))
        assert qoi_dominant_channel(f) == "blue"

    def test_equal_channels_returns_red(self, tmp_path):
        f = tmp_path / "equal.qoi"
        f.write_bytes(_make_qoi_bytes(1, 1, 3, [(128, 128, 128)]))
        assert qoi_dominant_channel(f) == "red"

    def test_mixed_pixels(self, tmp_path):
        f = tmp_path / "mixed.qoi"
        pixels = [(200, 50, 50), (200, 50, 50), (50, 150, 50)]
        f.write_bytes(_make_qoi_bytes(3, 1, 3, pixels))
        result = qoi_dominant_channel(f)
        assert result in ("red", "green", "blue")

    def test_returns_string_type(self, tmp_path):
        f = tmp_path / "t.qoi"
        f.write_bytes(_make_qoi_bytes(1, 1, 3, [(100, 200, 50)]))
        result = qoi_dominant_channel(f)
        assert isinstance(result, str)
        assert result in ("red", "green", "blue")


class TestQoiMinMaxBrightnessSynthetic:
    def test_black_pixel(self, tmp_path):
        f = tmp_path / "black.qoi"
        f.write_bytes(_make_qoi_bytes(1, 1, 3, [(0, 0, 0)]))
        result = qoi_min_max_brightness(f)
        assert result["min"] == 0.0
        assert result["max"] == 0.0

    def test_white_pixel(self, tmp_path):
        f = tmp_path / "white.qoi"
        f.write_bytes(_make_qoi_bytes(1, 1, 3, [(255, 255, 255)]))
        result = qoi_min_max_brightness(f)
        assert result["min"] > 254.0
        assert result["max"] > 254.0

    def test_mixed_brightness(self, tmp_path):
        f = tmp_path / "mixed.qoi"
        pixels = [(0, 0, 0), (255, 255, 255)]
        f.write_bytes(_make_qoi_bytes(2, 1, 3, pixels))
        result = qoi_min_max_brightness(f)
        assert result["min"] == 0.0
        assert result["max"] > 254.0
        assert result["min"] < result["max"]

    def test_returns_dict_with_min_max(self, tmp_path):
        f = tmp_path / "t.qoi"
        f.write_bytes(_make_qoi_bytes(1, 1, 3, [(128, 128, 128)]))
        result = qoi_min_max_brightness(f)
        assert isinstance(result, dict)
        assert "min" in result
        assert "max" in result
        assert isinstance(result["min"], float)
        assert isinstance(result["max"], float)

    def test_single_pixel_min_equals_max(self, tmp_path):
        f = tmp_path / "single.qoi"
        f.write_bytes(_make_qoi_bytes(1, 1, 3, [(100, 150, 200)]))
        result = qoi_min_max_brightness(f)
        assert abs(result["min"] - result["max"]) < 0.001


class TestQoiFromSamples:
    def test_1x1_red_dominant_channel(self):
        path = SAMPLES / "1x1-red.qoi"
        if path.exists():
            assert qoi_dominant_channel(path) == "red"

    def test_2x2_black_brightness_zero(self):
        path = SAMPLES / "2x2-black.qoi"
        if path.exists():
            result = qoi_min_max_brightness(path)
            assert result["min"] == 0.0
            assert result["max"] == 0.0
