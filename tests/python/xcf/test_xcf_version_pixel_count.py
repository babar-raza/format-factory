"""
test_xcf_version_pixel_count.py

Sprint: FORMAT-FACTORY-GAP-DRIVEN-PRODUCT-RNEXT-001
Gap IDs: GAP-XCF-FOSS-XCF_VERSION-001 (implied), GAP-XCF-FOSS-XCFPIXELCOUNT

Focused tests for xcf_version and xcf_pixel_count.
Closes missing_test_coverage gaps for both functions.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from xcf.xcf_parser import xcf_version, xcf_pixel_count, xcf_file_size, XcfError

_SAMPLES = _REPO / "samples" / "by-format" / "xcf" / "valid"


class TestXcfVersion:
    def test_rgb_image_version_is_string(self):
        ver = xcf_version(_SAMPLES / "1x1-red-rgb.xcf")
        assert isinstance(ver, str)
        assert len(ver) > 0

    def test_gray_image_version_is_string(self):
        ver = xcf_version(_SAMPLES / "2x2-gray.xcf")
        assert isinstance(ver, str)

    def test_missing_file_raises(self):
        with pytest.raises(XcfError):
            xcf_version(_SAMPLES / "ghost.xcf")


class TestXcfPixelCount:
    def test_1x1_pixel_count(self):
        count = xcf_pixel_count(_SAMPLES / "1x1-red-rgb.xcf")
        assert count == 1  # 1*1

    def test_2x2_pixel_count(self):
        count = xcf_pixel_count(_SAMPLES / "2x2-gray.xcf")
        assert count == 4  # 2*2

    def test_pixel_count_positive(self):
        count = xcf_pixel_count(_SAMPLES / "1x1-rgba-blue.xcf")
        assert count > 0

    def test_missing_file_raises(self):
        with pytest.raises(XcfError):
            xcf_pixel_count(_SAMPLES / "ghost.xcf")


class TestXcfFileSize:
    def test_file_size_positive(self):
        size = xcf_file_size(_SAMPLES / "1x1-red-rgb.xcf")
        assert isinstance(size, int)
        assert size > 0

    def test_gray_file_size_positive(self):
        size = xcf_file_size(_SAMPLES / "2x2-gray.xcf")
        assert size > 0

    def test_missing_file_raises(self):
        with pytest.raises(XcfError):
            xcf_file_size(_SAMPLES / "ghost.xcf")
