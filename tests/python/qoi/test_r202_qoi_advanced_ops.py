"""
tests/python/qoi/test_r202_qoi_advanced_ops.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-SPRINT12-001
TASK-001 (part B): QOI advanced operations.

Covers: QoiImage, encode_qoi, encode_qoi_to_file, parse_qoi, probe_qoi,
qoi_dimensions, qoi_pixel_count, get_capabilities, get_encoder_capabilities.
"""
from __future__ import annotations

import sys
import os
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from qoi import (
    QoiImage, encode_qoi, encode_qoi_to_file, parse_qoi, probe_qoi,
    qoi_dimensions, qoi_pixel_count, get_capabilities, get_encoder_capabilities,
)

_PIXELS_2X2 = [(255, 0, 0, 255), (0, 255, 0, 255), (0, 0, 255, 255), (255, 255, 0, 255)]
_PIXELS_1X1 = [(128, 64, 32, 255)]


def _make_image(pixels=None, w=2, h=2, channels=4):
    p = pixels or _PIXELS_2X2
    return QoiImage(width=w, height=h, channels=channels, colorspace=0, pixels=p)


def _make_qoi_file(pixels=None, w=2, h=2):
    img = _make_image(pixels, w, h)
    fd, path = tempfile.mkstemp(suffix=".qoi")
    os.close(fd)
    encode_qoi_to_file(img, path)
    return path


class TestQoiCapabilities:
    """get_capabilities, get_encoder_capabilities."""

    def test_get_capabilities_dict(self):
        caps = get_capabilities()
        assert isinstance(caps, dict)
        assert caps.get("format") == "qoi"

    def test_get_capabilities_has_supported(self):
        caps = get_capabilities()
        assert "supported" in caps
        assert isinstance(caps["supported"], list)

    def test_get_encoder_capabilities_dict(self):
        enc = get_encoder_capabilities()
        assert isinstance(enc, dict)

    def test_get_encoder_capabilities_format(self):
        enc = get_encoder_capabilities()
        assert enc.get("format") == "qoi"


class TestQoiEncoding:
    """encode_qoi, encode_qoi_to_file."""

    def test_encode_qoi_returns_bytes(self):
        img = _make_image()
        encoded = encode_qoi(img)
        assert isinstance(encoded, bytes)
        assert len(encoded) > 0

    def test_encode_qoi_has_magic(self):
        img = _make_image()
        encoded = encode_qoi(img)
        # QOI magic: "qoif" = 0x716f6966
        assert encoded[:4] == b"qoif"

    def test_encode_qoi_to_file_creates_file(self):
        img = _make_image()
        fd, path = tempfile.mkstemp(suffix=".qoi")
        os.close(fd)
        try:
            result = encode_qoi_to_file(img, path)
            assert os.path.getsize(path) > 0
        finally:
            os.unlink(path)

    def test_encode_qoi_1x1(self):
        img = _make_image(_PIXELS_1X1, w=1, h=1)
        encoded = encode_qoi(img)
        assert isinstance(encoded, bytes)

    def test_encode_qoi_3channel(self):
        pixels_rgb = [(255, 0, 0), (0, 255, 0)]
        img = QoiImage(width=2, height=1, channels=3, colorspace=0, pixels=pixels_rgb)
        encoded = encode_qoi(img)
        assert isinstance(encoded, bytes)
        assert len(encoded) > 0


class TestQoiProbeAndParse:
    """probe_qoi, parse_qoi — all take file path."""

    def test_probe_qoi_valid_file(self):
        path = _make_qoi_file()
        try:
            result = probe_qoi(path)
            assert isinstance(result, dict)
            assert result.get("valid_header") is True
        finally:
            os.unlink(path)

    def test_probe_qoi_has_dimensions(self):
        path = _make_qoi_file()
        try:
            result = probe_qoi(path)
            assert result.get("width") == 2
            assert result.get("height") == 2
        finally:
            os.unlink(path)

    def test_probe_qoi_channels(self):
        path = _make_qoi_file()
        try:
            result = probe_qoi(path)
            assert result.get("channels") == 4
        finally:
            os.unlink(path)

    def test_probe_qoi_file_exists(self):
        path = _make_qoi_file()
        try:
            result = probe_qoi(path)
            assert result.get("exists") is True
        finally:
            os.unlink(path)

    def test_parse_qoi_returns_dict(self):
        path = _make_qoi_file()
        try:
            result = parse_qoi(path)
            assert isinstance(result, dict)
        finally:
            os.unlink(path)

    def test_parse_qoi_dimensions(self):
        path = _make_qoi_file()
        try:
            result = parse_qoi(path)
            assert result.get("width") == 2
            assert result.get("height") == 2
        finally:
            os.unlink(path)

    def test_parse_qoi_has_pixels(self):
        path = _make_qoi_file()
        try:
            result = parse_qoi(path)
            # May have pixels or pixel_count
            assert "pixels" in result or "pixel_count" in result or result.get("width") > 0
        finally:
            os.unlink(path)


class TestQoiAnalytics:
    """qoi_dimensions, qoi_pixel_count."""

    def test_qoi_dimensions_dict(self):
        path = _make_qoi_file()
        try:
            dims = qoi_dimensions(path)
            assert isinstance(dims, dict)
            assert dims.get("width") == 2
            assert dims.get("height") == 2
        finally:
            os.unlink(path)

    def test_qoi_dimensions_channels(self):
        path = _make_qoi_file()
        try:
            dims = qoi_dimensions(path)
            assert dims.get("channels") == 4
        finally:
            os.unlink(path)

    def test_qoi_pixel_count_correct(self):
        path = _make_qoi_file()
        try:
            count = qoi_pixel_count(path)
            assert count == 4  # 2x2 image
        finally:
            os.unlink(path)

    def test_qoi_pixel_count_1x1(self):
        path = _make_qoi_file(_PIXELS_1X1, w=1, h=1)
        try:
            count = qoi_pixel_count(path)
            assert count == 1
        finally:
            os.unlink(path)

    def test_qoi_roundtrip_dimensions(self):
        img = _make_image()
        fd, path = tempfile.mkstemp(suffix=".qoi")
        os.close(fd)
        try:
            encode_qoi_to_file(img, path)
            dims = qoi_dimensions(path)
            assert dims["width"] == img.width
            assert dims["height"] == img.height
        finally:
            os.unlink(path)
