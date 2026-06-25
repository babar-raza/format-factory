"""Tests for real XCF layer name reading — GAP-XCF-LAYER-NAMES closure.

Gap closure: GAP-XCF-LAYER-NAMES (missing_real_implementation for LayerNames capability)
Covers: xcf_layer_name_list returning real names from XCF layer records,
        _read_xcf_string length-prefixed format, XcfImage.layer_names field.
"""
from __future__ import annotations

from pathlib import Path
import sys

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from xcf.xcf_parser import (  # type: ignore
    parse_xcf_strict,
    xcf_layer_name_list,
    _read_xcf_string,
)

_XCF_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"
_RGB = str(_XCF_DIR / "1x1-red-rgb.xcf")
_RGBA = str(_XCF_DIR / "1x1-rgba-blue.xcf")
_GRAY = str(_XCF_DIR / "2x2-gray.xcf")


class TestReadXcfString:
    def test_reads_length_prefixed_string(self):
        # Construct: uint32(11) + "Background\0"
        import struct
        data = struct.pack(">I", 11) + b"Background\x00"
        name, end = _read_xcf_string(data, 0)
        assert name == "Background"
        assert end == 15  # 4 + 11

    def test_empty_string_length_zero(self):
        import struct
        data = struct.pack(">I", 0)
        name, end = _read_xcf_string(data, 0)
        assert name == ""
        assert end == 4

    def test_returns_tuple(self):
        import struct
        data = struct.pack(">I", 5) + b"test\x00"
        result = _read_xcf_string(data, 0)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_offset_past_end_returns_empty(self):
        data = b"\x00" * 2  # too short for 4-byte length
        name, _ = _read_xcf_string(data, 0)
        assert name == ""


class TestXcfImageLayerNames:
    def test_layer_names_field_present(self):
        img = parse_xcf_strict(_RGB)
        assert hasattr(img, "layer_names")

    def test_layer_names_is_list(self):
        img = parse_xcf_strict(_RGB)
        assert isinstance(img.layer_names, list)

    def test_layer_names_count_matches_num_layers(self):
        img = parse_xcf_strict(_RGB)
        assert len(img.layer_names) == img.num_layers

    def test_layer_names_are_strings(self):
        img = parse_xcf_strict(_RGB)
        for name in img.layer_names:
            assert isinstance(name, str)

    def test_rgb_layer_name_is_background(self):
        img = parse_xcf_strict(_RGB)
        assert img.layer_names == ["Background"]

    def test_gray_layer_name_is_background(self):
        img = parse_xcf_strict(_GRAY)
        assert img.layer_names == ["Background"]

    def test_rgba_has_layer_names(self):
        img = parse_xcf_strict(_RGBA)
        assert len(img.layer_names) >= 1


class TestXcfLayerNameListReal:
    def test_returns_list(self):
        assert isinstance(xcf_layer_name_list(_RGB), list)

    def test_rgb_returns_background(self):
        names = xcf_layer_name_list(_RGB)
        assert names == ["Background"]

    def test_gray_returns_background(self):
        names = xcf_layer_name_list(_GRAY)
        assert names == ["Background"]

    def test_rgba_nonempty(self):
        names = xcf_layer_name_list(_RGBA)
        assert len(names) >= 1

    def test_names_are_strings(self):
        for f in [_RGB, _RGBA, _GRAY]:
            for name in xcf_layer_name_list(f):
                assert isinstance(name, str)

    def test_count_matches_layer_count(self):
        from xcf.xcf_parser import xcf_layer_count  # type: ignore
        for f in [_RGB, _RGBA, _GRAY]:
            assert len(xcf_layer_name_list(f)) == xcf_layer_count(f)

    def test_not_synthetic_placeholder(self):
        # Real names should NOT start with "Layer " positional placeholder format
        names = xcf_layer_name_list(_RGB)
        # The real name is "Background", not "Layer 0"
        assert names != ["Layer 0"]
        assert "Background" in names
