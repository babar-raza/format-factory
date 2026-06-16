"""Tests for xcf_has_alpha and xcf_canvas_size_bytes.

Product deepening: XCF analytics — TC-H3-001 / PDC-XCF-HAS-ALPHA-001.
"""
import struct
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_has_alpha,
    xcf_canvas_size_bytes,
    parse_xcf_strict,
    XcfImage,
)

VALID_SAMPLES = _REPO / "samples" / "by-format" / "xcf" / "valid"


def _make_xcf_bytes(width, height, image_type, num_layers):
    """Build a minimal valid XCF file header + property list + layer offsets."""
    # Header: magic(9) + version(4) + NUL(1) + width(4) + height(4) + type(4)
    header = b"gimp xcf " + b"v011" + b"\x00"
    header += struct.pack(">III", width, height, image_type)
    # Property list: single PROP_END (type=0, length=0)
    props = struct.pack(">II", 0, 0)
    # Layer offsets: one fake offset per layer + zero sentinel
    layers = b""
    for i in range(num_layers):
        layers += struct.pack(">I", 100 + i * 50)
    layers += struct.pack(">I", 0)  # sentinel
    return header + props + layers


class TestXcfHasAlphaFromSamples:
    def test_rgb_single_layer_no_alpha(self):
        path = VALID_SAMPLES / "1x1-red-rgb.xcf"
        if path.exists():
            img = parse_xcf_strict(path)
            if img.num_layers == 1 and img.image_type == 0:
                assert xcf_has_alpha(path) is False

    def test_rgba_multi_layer_has_alpha(self):
        path = VALID_SAMPLES / "1x1-rgba-blue.xcf"
        if path.exists():
            img = parse_xcf_strict(path)
            if img.num_layers > 1:
                assert xcf_has_alpha(path) is True

    def test_grayscale_single_layer(self):
        path = VALID_SAMPLES / "2x2-gray.xcf"
        if path.exists():
            img = parse_xcf_strict(path)
            if img.num_layers == 1:
                assert xcf_has_alpha(path) is False


class TestXcfHasAlphaSynthetic:
    def test_rgb_single_layer(self, tmp_path):
        f = tmp_path / "rgb1.xcf"
        f.write_bytes(_make_xcf_bytes(10, 10, 0, 1))
        assert xcf_has_alpha(f) is False

    def test_rgb_multi_layer(self, tmp_path):
        f = tmp_path / "rgb2.xcf"
        f.write_bytes(_make_xcf_bytes(10, 10, 0, 3))
        assert xcf_has_alpha(f) is True

    def test_grayscale_single_layer(self, tmp_path):
        f = tmp_path / "gray1.xcf"
        f.write_bytes(_make_xcf_bytes(10, 10, 1, 1))
        assert xcf_has_alpha(f) is False

    def test_grayscale_multi_layer(self, tmp_path):
        f = tmp_path / "gray2.xcf"
        f.write_bytes(_make_xcf_bytes(10, 10, 1, 2))
        assert xcf_has_alpha(f) is True

    def test_indexed_always_false(self, tmp_path):
        f = tmp_path / "idx.xcf"
        f.write_bytes(_make_xcf_bytes(10, 10, 2, 5))
        assert xcf_has_alpha(f) is False

    def test_returns_bool(self, tmp_path):
        f = tmp_path / "t.xcf"
        f.write_bytes(_make_xcf_bytes(10, 10, 0, 1))
        assert isinstance(xcf_has_alpha(f), bool)


class TestXcfCanvasSizeBytes:
    def test_rgb_canvas_size(self, tmp_path):
        f = tmp_path / "rgb.xcf"
        f.write_bytes(_make_xcf_bytes(100, 200, 0, 1))
        assert xcf_canvas_size_bytes(f) == 100 * 200 * 4

    def test_grayscale_canvas_size(self, tmp_path):
        f = tmp_path / "gray.xcf"
        f.write_bytes(_make_xcf_bytes(50, 50, 1, 1))
        assert xcf_canvas_size_bytes(f) == 50 * 50 * 2

    def test_indexed_canvas_size(self, tmp_path):
        f = tmp_path / "idx.xcf"
        f.write_bytes(_make_xcf_bytes(30, 40, 2, 1))
        assert xcf_canvas_size_bytes(f) == 30 * 40 * 1

    def test_returns_int(self, tmp_path):
        f = tmp_path / "t.xcf"
        f.write_bytes(_make_xcf_bytes(10, 10, 0, 1))
        assert isinstance(xcf_canvas_size_bytes(f), int)

    def test_from_sample(self):
        path = VALID_SAMPLES / "1x1-red-rgb.xcf"
        if path.exists():
            result = xcf_canvas_size_bytes(path)
            assert result > 0
            assert isinstance(result, int)
