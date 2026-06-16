"""Tests for xcf_image_type_code and xcf_file_header_overhead (Sprint 68)."""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src" / "python"))

from xcf.xcf_parser import xcf_image_type_code, xcf_file_header_overhead

XCF = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "xcf" / "valid"


class TestXcfImageTypeCode:
    def test_rgb_is_zero(self):
        assert xcf_image_type_code(XCF / "1x1-red-rgb.xcf") == 0

    def test_rgba_is_zero(self):
        assert xcf_image_type_code(XCF / "1x1-rgba-blue.xcf") == 0

    def test_gray_is_one(self):
        assert xcf_image_type_code(XCF / "2x2-gray.xcf") == 1

    def test_returns_int(self):
        assert isinstance(xcf_image_type_code(XCF / "1x1-red-rgb.xcf"), int)

    def test_nonnegative(self):
        for f in ["1x1-red-rgb.xcf", "1x1-rgba-blue.xcf", "2x2-gray.xcf"]:
            assert xcf_image_type_code(XCF / f) >= 0


class TestXcfFileHeaderOverhead:
    def test_red(self):
        assert xcf_file_header_overhead(XCF / "1x1-red-rgb.xcf") == 176

    def test_rgba_blue(self):
        assert xcf_file_header_overhead(XCF / "1x1-rgba-blue.xcf") == 177

    def test_gray(self):
        assert xcf_file_header_overhead(XCF / "2x2-gray.xcf") == 174

    def test_returns_int(self):
        assert isinstance(xcf_file_header_overhead(XCF / "1x1-red-rgb.xcf"), int)

    def test_all_distinct(self):
        vals = [xcf_file_header_overhead(XCF / f) for f in ["1x1-red-rgb.xcf", "1x1-rgba-blue.xcf", "2x2-gray.xcf"]]
        assert len(set(vals)) == 3
