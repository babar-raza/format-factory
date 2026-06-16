"""Tests for qoi_total_brightness (Sprint 22)."""
import pytest, struct
from src.python.qoi import qoi_total_brightness


def _make_qoi(tmp_path, pixels, width, height, channels=3):
    """Create a minimal QOI file with given pixels."""
    p = tmp_path / "test.qoi"
    data = bytearray()
    data += b"qoif"
    data += struct.pack(">II", width, height)
    data += bytes([channels, 0])
    prev = (0, 0, 0, 255)
    for px in pixels:
        r, g, b = px[0], px[1], px[2]
        a = px[3] if len(px) > 3 else 255
        if (r, g, b, a) == prev:
            data += bytes([0xFE - 0xFE + 0xC0])
        else:
            data += bytes([0xFE, r, g, b])
        prev = (r, g, b, a)
    data += b"\x00" * 7 + b"\x01"
    p.write_bytes(bytes(data))
    return str(p)


class TestQoiTotalBrightness:
    def test_black_pixels(self, tmp_path):
        path = _make_qoi(tmp_path, [(0, 0, 0)], 1, 1)
        assert qoi_total_brightness(path) == 0.0

    def test_white_pixel(self, tmp_path):
        path = _make_qoi(tmp_path, [(255, 255, 255)], 1, 1)
        assert qoi_total_brightness(path) == 255.0

    def test_return_type(self, tmp_path):
        path = _make_qoi(tmp_path, [(100, 100, 100)], 1, 1)
        assert isinstance(qoi_total_brightness(path), float)

    def test_non_negative(self, tmp_path):
        path = _make_qoi(tmp_path, [(50, 50, 50)], 1, 1)
        assert qoi_total_brightness(path) >= 0.0

    def test_multiple_pixels(self, tmp_path):
        path = _make_qoi(tmp_path, [(60, 60, 60), (120, 120, 120)], 2, 1)
        tb = qoi_total_brightness(path)
        assert tb > 0.0
