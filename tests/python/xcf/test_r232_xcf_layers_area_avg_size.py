"""Tests for xcf_total_layers_area and xcf_average_layer_size.

Product deepening: XCF analytics — TC-H3-002-XCF / PDC-XCF-LAYERS-AREA-001.
"""
import struct
import sys
import tempfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from xcf.xcf_parser import xcf_total_layers_area, xcf_average_layer_size


def _make_xcf(width=1, height=1, image_type=0, version=b"v011", num_layers=1):
    header = b"gimp xcf " + version + b"\x00"
    header += struct.pack(">III", width, height, image_type)
    header += struct.pack(">II", 0, 0)  # PROP_END
    for i in range(num_layers):
        header += struct.pack(">I", 100 + i * 100)
    header += struct.pack(">I", 0)  # sentinel
    header += b"\x00" * 512
    tmp = tempfile.NamedTemporaryFile(suffix=".xcf", delete=False)
    tmp.write(header)
    tmp.close()
    return str(tmp.name)


class TestXcfTotalLayersArea:
    def test_1x1_single_layer(self):
        p = _make_xcf(1, 1, num_layers=1)
        assert xcf_total_layers_area(p) == 1

    def test_10x10_two_layers(self):
        p = _make_xcf(10, 10, num_layers=2)
        assert xcf_total_layers_area(p) == 200

    def test_100x100_single_layer(self):
        p = _make_xcf(100, 100, num_layers=1)
        assert xcf_total_layers_area(p) == 10000

    def test_returns_int(self):
        p = _make_xcf(5, 5, num_layers=1)
        assert isinstance(xcf_total_layers_area(p), int)

    def test_non_negative(self):
        p = _make_xcf(1, 1, num_layers=1)
        assert xcf_total_layers_area(p) >= 0


class TestXcfAverageLayerSize:
    def test_single_layer(self):
        p = _make_xcf(100, 100, num_layers=1)
        assert xcf_average_layer_size(p) == pytest.approx(10000.0)

    def test_two_layers(self):
        p = _make_xcf(100, 100, num_layers=2)
        assert xcf_average_layer_size(p) == pytest.approx(5000.0)

    def test_five_layers(self):
        p = _make_xcf(100, 100, num_layers=5)
        assert xcf_average_layer_size(p) == pytest.approx(2000.0)

    def test_returns_float(self):
        p = _make_xcf(10, 10, num_layers=1)
        assert isinstance(xcf_average_layer_size(p), float)

    def test_non_negative(self):
        p = _make_xcf(1, 1, num_layers=1)
        assert xcf_average_layer_size(p) >= 0.0
