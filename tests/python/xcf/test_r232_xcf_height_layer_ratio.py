"""Tests for xcf_height and xcf_layer_to_canvas_ratio.

Product deepening: XCF analytics — TC-H3-002-XCF / PDC-XCF-HEIGHT-001.
"""
import struct
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.xcf import xcf_height, xcf_layer_to_canvas_ratio


def _make_xcf(tmp_path, name, width=100, height=100, image_type=0, num_layers=1):
    header = b"gimp xcf " + b"v011" + b"\x00"
    header += struct.pack(">III", width, height, image_type)
    header += struct.pack(">II", 0, 0)  # PROP_END
    for i in range(num_layers):
        header += struct.pack(">I", 100 + i * 100)
    header += struct.pack(">I", 0)  # sentinel
    header += struct.pack(">I", 0)  # channel sentinel
    path = tmp_path / f"{name}.xcf"
    path.write_bytes(header)
    return path


class TestXcfHeight:
    def test_100(self, tmp_path):
        f = _make_xcf(tmp_path, "h100", height=100)
        assert xcf_height(f) == 100

    def test_500(self, tmp_path):
        f = _make_xcf(tmp_path, "h500", height=500)
        assert xcf_height(f) == 500

    def test_1(self, tmp_path):
        f = _make_xcf(tmp_path, "h1", height=1)
        assert xcf_height(f) == 1

    def test_returns_int(self, tmp_path):
        f = _make_xcf(tmp_path, "type", height=200)
        assert isinstance(xcf_height(f), int)

    def test_square(self, tmp_path):
        f = _make_xcf(tmp_path, "sq", width=300, height=300)
        assert xcf_height(f) == 300


class TestXcfLayerToCanvasRatio:
    def test_single_layer_1mp(self, tmp_path):
        f = _make_xcf(tmp_path, "1l", width=1000, height=1000, num_layers=1)
        result = xcf_layer_to_canvas_ratio(f)
        assert abs(result - 1.0) < 0.01

    def test_two_layers(self, tmp_path):
        f = _make_xcf(tmp_path, "2l", width=1000, height=1000, num_layers=2)
        result = xcf_layer_to_canvas_ratio(f)
        assert abs(result - 2.0) < 0.01

    def test_small_image(self, tmp_path):
        f = _make_xcf(tmp_path, "small", width=100, height=100, num_layers=1)
        result = xcf_layer_to_canvas_ratio(f)
        assert result > 0

    def test_returns_float(self, tmp_path):
        f = _make_xcf(tmp_path, "type2", width=500, height=500, num_layers=3)
        assert isinstance(xcf_layer_to_canvas_ratio(f), float)

    def test_positive(self, tmp_path):
        f = _make_xcf(tmp_path, "pos", width=200, height=200, num_layers=1)
        assert xcf_layer_to_canvas_ratio(f) > 0
