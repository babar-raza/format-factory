"""Sprint 125 — XCF (xcf_pixel_area, xcf_bytes_per_dimension)
and ZST (zst_bytes_per_decompressed_byte, zst_is_trivial_compression).
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf.xcf_parser import xcf_pixel_area, xcf_bytes_per_dimension
from src.python.zst.zst_codec import zst_bytes_per_decompressed_byte, zst_is_trivial_compression

XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
ZST = _REPO / "samples" / "by-format" / "zst" / "valid"


class TestXcfPixelArea:
    def test_red_value(self):
        assert xcf_pixel_area(XCF / "1x1-red-rgb.xcf") == 1

    def test_blue_value(self):
        assert xcf_pixel_area(XCF / "1x1-rgba-blue.xcf") == 1

    def test_gray_value(self):
        assert xcf_pixel_area(XCF / "2x2-gray.xcf") == 4

    def test_returns_int(self):
        assert isinstance(xcf_pixel_area(XCF / "1x1-red-rgb.xcf"), int)

    def test_non_negative(self):
        assert xcf_pixel_area(XCF / "2x2-gray.xcf") >= 0


class TestXcfBytesPerDimension:
    def test_red_value(self):
        assert abs(xcf_bytes_per_dimension(XCF / "1x1-red-rgb.xcf") - 88.5) < 0.01

    def test_blue_value(self):
        assert abs(xcf_bytes_per_dimension(XCF / "1x1-rgba-blue.xcf") - 89.0) < 0.01

    def test_gray_value(self):
        assert abs(xcf_bytes_per_dimension(XCF / "2x2-gray.xcf") - 44.5) < 0.01

    def test_returns_float(self):
        assert isinstance(xcf_bytes_per_dimension(XCF / "1x1-red-rgb.xcf"), float)

    def test_positive(self):
        assert xcf_bytes_per_dimension(XCF / "2x2-gray.xcf") > 0.0


class TestZstBytesPerDecompressedByte:
    def test_block_value(self):
        assert abs(zst_bytes_per_decompressed_byte(ZST / "block-128k.zst") - 1.0001) < 0.001

    def test_dict_value(self):
        assert abs(zst_bytes_per_decompressed_byte(ZST / "dict-compressed.zst") - 0.01779) < 0.001

    def test_empty_value(self):
        assert abs(zst_bytes_per_decompressed_byte(ZST / "empty-block.zst") - 0.0) < 0.001

    def test_returns_float(self):
        assert isinstance(zst_bytes_per_decompressed_byte(ZST / "block-128k.zst"), float)

    def test_non_negative(self):
        assert zst_bytes_per_decompressed_byte(ZST / "dict-compressed.zst") >= 0.0


class TestZstIsTrivialCompression:
    def test_block_trivial(self):
        assert zst_is_trivial_compression(ZST / "block-128k.zst") is True

    def test_dict_not_trivial(self):
        assert zst_is_trivial_compression(ZST / "dict-compressed.zst") is False

    def test_empty_trivial(self):
        assert zst_is_trivial_compression(ZST / "empty-block.zst") is True

    def test_returns_bool(self):
        assert isinstance(zst_is_trivial_compression(ZST / "block-128k.zst"), bool)

    def test_dict_is_bool(self):
        assert isinstance(zst_is_trivial_compression(ZST / "dict-compressed.zst"), bool)
