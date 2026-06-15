"""Tests for qoi_has_alpha and qoi_average_brightness."""

from __future__ import annotations

import struct
import sys
import tempfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from qoi.qoi_parser import qoi_has_alpha, qoi_average_brightness  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers — minimal QOI file builder
# ---------------------------------------------------------------------------

def _make_qoi(width: int, height: int, channels: int, pixels: list[tuple]) -> Path:
    """Build a minimal QOI file with raw QOI_OP_RGBA/QOI_OP_RGB chunks."""
    header = b"qoif" + struct.pack(">II", width, height) + bytes([channels, 0])
    chunks = bytearray()
    for px in pixels:
        if channels == 4:
            chunks.append(0xFF)  # QOI_OP_RGBA
            chunks.extend(bytes(px[:4]))
        else:
            chunks.append(0xFE)  # QOI_OP_RGB
            chunks.extend(bytes(px[:3]))
    end_marker = bytes([0, 0, 0, 0, 0, 0, 0, 1])
    data = header + bytes(chunks) + end_marker
    tmp = tempfile.NamedTemporaryFile(suffix=".qoi", delete=False)
    tmp.write(data)
    tmp.close()
    return Path(tmp.name)


# ---------------------------------------------------------------------------
# Tests: qoi_has_alpha
# ---------------------------------------------------------------------------

class TestQoiHasAlpha:
    """Test the qoi_has_alpha function."""

    def test_rgba_image_has_alpha(self):
        path = _make_qoi(1, 1, 4, [(128, 64, 32, 255)])
        assert qoi_has_alpha(path) is True

    def test_rgb_image_no_alpha(self):
        path = _make_qoi(1, 1, 3, [(128, 64, 32)])
        assert qoi_has_alpha(path) is False

    def test_returns_bool(self):
        path = _make_qoi(1, 1, 3, [(0, 0, 0)])
        assert isinstance(qoi_has_alpha(path), bool)

    def test_larger_rgba_image(self):
        pixels = [(i, i, i, 200) for i in range(4)]
        path = _make_qoi(2, 2, 4, pixels)
        assert qoi_has_alpha(path) is True

    def test_larger_rgb_image(self):
        pixels = [(i, i, i) for i in range(4)]
        path = _make_qoi(2, 2, 3, pixels)
        assert qoi_has_alpha(path) is False


# ---------------------------------------------------------------------------
# Tests: qoi_average_brightness
# ---------------------------------------------------------------------------

class TestQoiAverageBrightness:
    """Test the qoi_average_brightness function."""

    def test_black_pixel(self):
        path = _make_qoi(1, 1, 3, [(0, 0, 0)])
        assert qoi_average_brightness(path) == pytest.approx(0.0)

    def test_white_pixel(self):
        path = _make_qoi(1, 1, 3, [(255, 255, 255)])
        expected = 0.299 * 255 + 0.587 * 255 + 0.114 * 255
        assert qoi_average_brightness(path) == pytest.approx(expected, abs=0.01)

    def test_pure_red(self):
        path = _make_qoi(1, 1, 3, [(255, 0, 0)])
        assert qoi_average_brightness(path) == pytest.approx(0.299 * 255, abs=0.01)

    def test_pure_green(self):
        path = _make_qoi(1, 1, 3, [(0, 255, 0)])
        assert qoi_average_brightness(path) == pytest.approx(0.587 * 255, abs=0.01)

    def test_returns_float(self):
        path = _make_qoi(1, 1, 3, [(128, 128, 128)])
        result = qoi_average_brightness(path)
        assert isinstance(result, float)

    def test_multiple_pixels_averaged(self):
        # 2 pixels: black (0) and white (255)
        pixels = [(0, 0, 0), (255, 255, 255)]
        path = _make_qoi(2, 1, 3, pixels)
        white_brightness = 0.299 * 255 + 0.587 * 255 + 0.114 * 255
        expected_avg = white_brightness / 2.0
        assert qoi_average_brightness(path) == pytest.approx(expected_avg, abs=0.01)

    def test_rgba_ignores_alpha(self):
        path = _make_qoi(1, 1, 4, [(128, 128, 128, 0)])
        expected = 0.299 * 128 + 0.587 * 128 + 0.114 * 128
        assert qoi_average_brightness(path) == pytest.approx(expected, abs=0.01)

    def test_brightness_range(self):
        path = _make_qoi(1, 1, 3, [(100, 150, 200)])
        result = qoi_average_brightness(path)
        assert 0.0 <= result <= 255.0
