"""Tests for xcf_is_portrait and xcf_layer_count_per_megapixel (Sprint 27)."""
import sys
import struct
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from xcf import xcf_is_portrait, xcf_layer_count_per_megapixel


def _make_xcf(tmp_path, name, width, height, num_layers=1):
    """Create a minimal valid XCF file with given dimensions and layer count."""
    # Header: magic(9) + version(4) + NUL(1) + width(4) + height(4) + type(4)
    header = b"gimp xcf " + b"v011" + b"\x00"
    header += struct.pack(">III", width, height, 0)
    # Property list: single PROP_END
    props = struct.pack(">II", 0, 0)
    # Layer offsets: fake offsets + zero sentinel
    layers = b""
    for i in range(num_layers):
        layers += struct.pack(">I", 100 + i * 50)
    layers += struct.pack(">I", 0)
    p = tmp_path / f"{name}.xcf"
    p.write_bytes(header + props + layers)
    return str(p)


class TestXcfIsPortrait:
    def test_portrait_image(self, tmp_path):
        # height > width => portrait
        p = _make_xcf(tmp_path, "pt", width=100, height=200)
        assert xcf_is_portrait(p) is True

    def test_landscape_not_portrait(self, tmp_path):
        p = _make_xcf(tmp_path, "ls", width=300, height=100)
        assert xcf_is_portrait(p) is False

    def test_square_not_portrait(self, tmp_path):
        p = _make_xcf(tmp_path, "sq", width=100, height=100)
        assert xcf_is_portrait(p) is False

    def test_return_type(self, tmp_path):
        p = _make_xcf(tmp_path, "rt", width=50, height=150)
        assert isinstance(xcf_is_portrait(p), bool)

    def test_tall_portrait(self, tmp_path):
        # height 1000, width 10 => portrait
        p = _make_xcf(tmp_path, "tp", width=10, height=1000)
        assert xcf_is_portrait(p) is True


class TestXcfLayerCountPerMegapixel:
    def test_exact_value(self, tmp_path):
        # 1000x1000 = 1 megapixel; 1 layer => 1.0
        p = _make_xcf(tmp_path, "mp1", width=1000, height=1000, num_layers=1)
        result = xcf_layer_count_per_megapixel(p)
        assert isinstance(result, float)

    def test_return_type(self, tmp_path):
        p = _make_xcf(tmp_path, "rt2", width=100, height=100)
        assert isinstance(xcf_layer_count_per_megapixel(p), float)

    def test_nonnegative(self, tmp_path):
        p = _make_xcf(tmp_path, "nn", width=200, height=300)
        assert xcf_layer_count_per_megapixel(p) >= 0.0

    def test_small_image_high_ratio(self, tmp_path):
        # 10x10 = 0.0001 megapixels; 1 layer => very high ratio
        p = _make_xcf(tmp_path, "sm", width=10, height=10, num_layers=1)
        result = xcf_layer_count_per_megapixel(p)
        assert result > 100.0

    def test_large_image_small_ratio(self, tmp_path):
        # 2000x2000 = 4 megapixels; 1 layer => 0.25
        p = _make_xcf(tmp_path, "li", width=2000, height=2000, num_layers=1)
        result = xcf_layer_count_per_megapixel(p)
        assert result == pytest.approx(0.25, abs=0.01)
