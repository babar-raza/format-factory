"""
tests/python/qoi/test_r220_qoi_is_opaque.py

Sprint: PRODUCT-DEEPENING-CONTINUATION-20260613
Tests for qoi_is_opaque() — check if all pixels have alpha == 255.
"""
from __future__ import annotations

import struct
import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.qoi.qoi_parser import (
    qoi_is_opaque,
    QOI_MAGIC,
    QOI_HEADER_SIZE,
    QOI_END_MARKER,
)

SAMPLES = _REPO / "samples" / "by-format" / "qoi" / "valid"


def _make_qoi_header(width: int, height: int, channels: int = 4, colorspace: int = 0) -> bytes:
    """Build a minimal QOI header."""
    return QOI_MAGIC + struct.pack(">II", width, height) + bytes([channels, colorspace])


def _make_opaque_1x1_rgba() -> bytes:
    """1x1 RGBA pixel (255, 0, 0, 255) — fully opaque red."""
    header = _make_qoi_header(1, 1, 4)
    # QOI_OP_RGBA = 0xFF followed by r, g, b, a
    pixel_data = bytes([0xFF, 255, 0, 0, 255])
    return header + pixel_data + QOI_END_MARKER


def _make_transparent_1x1_rgba() -> bytes:
    """1x1 RGBA pixel (255, 0, 0, 128) — semi-transparent red."""
    header = _make_qoi_header(1, 1, 4)
    pixel_data = bytes([0xFF, 255, 0, 0, 128])
    return header + pixel_data + QOI_END_MARKER


def _make_opaque_1x1_rgb() -> bytes:
    """1x1 RGB pixel (0, 128, 255) — 3-channel, always opaque."""
    header = _make_qoi_header(1, 1, 3)
    # QOI_OP_RGB = 0xFE followed by r, g, b
    pixel_data = bytes([0xFE, 0, 128, 255])
    return header + pixel_data + QOI_END_MARKER


def _write_temp_qoi(data: bytes) -> Path:
    """Write QOI data to a temporary file and return the path."""
    f = tempfile.NamedTemporaryFile(suffix=".qoi", delete=False)
    f.write(data)
    f.close()
    return Path(f.name)


class TestQoiIsOpaqueFromSamples:
    """Test qoi_is_opaque with on-disk QOI samples."""

    def test_1x1_red_is_opaque(self):
        assert qoi_is_opaque(SAMPLES / "1x1-red.qoi") is True

    def test_2x2_black_is_opaque(self):
        assert qoi_is_opaque(SAMPLES / "2x2-black.qoi") is True

    def test_4x1_gradient_is_opaque(self):
        # 3-channel RGB → always opaque
        assert qoi_is_opaque(SAMPLES / "4x1-gradient.qoi") is True

    def test_return_type_is_bool(self):
        result = qoi_is_opaque(SAMPLES / "1x1-red.qoi")
        assert isinstance(result, bool)


class TestQoiIsOpaqueSynthetic:
    """Test qoi_is_opaque with synthetic QOI data."""

    def test_opaque_rgba_returns_true(self):
        path = _write_temp_qoi(_make_opaque_1x1_rgba())
        try:
            assert qoi_is_opaque(path) is True
        finally:
            path.unlink(missing_ok=True)

    def test_transparent_rgba_returns_false(self):
        path = _write_temp_qoi(_make_transparent_1x1_rgba())
        try:
            assert qoi_is_opaque(path) is False
        finally:
            path.unlink(missing_ok=True)

    def test_rgb_always_opaque(self):
        path = _write_temp_qoi(_make_opaque_1x1_rgb())
        try:
            assert qoi_is_opaque(path) is True
        finally:
            path.unlink(missing_ok=True)

    def test_zero_alpha_is_not_opaque(self):
        """Fully transparent pixel (alpha=0) should return False."""
        header = _make_qoi_header(1, 1, 4)
        pixel_data = bytes([0xFF, 0, 0, 0, 0])  # RGBA with alpha=0
        data = header + pixel_data + QOI_END_MARKER
        path = _write_temp_qoi(data)
        try:
            assert qoi_is_opaque(path) is False
        finally:
            path.unlink(missing_ok=True)

    def test_mixed_alpha_is_not_opaque(self):
        """2x1 image: first pixel opaque, second transparent → not opaque."""
        header = _make_qoi_header(2, 1, 4)
        # pixel 1: opaque red (RGBA 255,0,0,255)
        p1 = bytes([0xFF, 255, 0, 0, 255])
        # pixel 2: transparent blue (RGBA 0,0,255,100)
        p2 = bytes([0xFF, 0, 0, 255, 100])
        data = header + p1 + p2 + QOI_END_MARKER
        path = _write_temp_qoi(data)
        try:
            assert qoi_is_opaque(path) is False
        finally:
            path.unlink(missing_ok=True)

    def test_all_pixels_opaque_multi_pixel(self):
        """2x1 image: both pixels fully opaque → True."""
        header = _make_qoi_header(2, 1, 4)
        p1 = bytes([0xFF, 255, 0, 0, 255])
        p2 = bytes([0xFF, 0, 255, 0, 255])
        data = header + p1 + p2 + QOI_END_MARKER
        path = _write_temp_qoi(data)
        try:
            assert qoi_is_opaque(path) is True
        finally:
            path.unlink(missing_ok=True)
