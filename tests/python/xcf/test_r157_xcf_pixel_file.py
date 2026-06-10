"""
test_r157_xcf_pixel_file.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT17-001
Added: 2026-06-10

Tests for XCF xcf_pixel_count and xcf_file_size functions.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from xcf.xcf_parser import xcf_pixel_count, xcf_file_size, XcfError

_SAMPLES = _REPO / "samples" / "by-format" / "xcf" / "valid"


class TestXcfPixelCount:
    def test_1x1_red(self):
        assert xcf_pixel_count(_SAMPLES / "1x1-red-rgb.xcf") == 1

    def test_2x2_gray(self):
        assert xcf_pixel_count(_SAMPLES / "2x2-gray.xcf") == 4

    def test_1x1_rgba(self):
        assert xcf_pixel_count(_SAMPLES / "1x1-rgba-blue.xcf") == 1

    def test_nonexistent_file(self):
        with pytest.raises(XcfError):
            xcf_pixel_count(_SAMPLES / "ghost.xcf")


class TestXcfFileSize:
    def test_1x1_red(self):
        size = xcf_file_size(_SAMPLES / "1x1-red-rgb.xcf")
        assert isinstance(size, int)
        assert size > 0

    def test_2x2_gray(self):
        size = xcf_file_size(_SAMPLES / "2x2-gray.xcf")
        assert size > 0

    def test_1x1_rgba(self):
        size = xcf_file_size(_SAMPLES / "1x1-rgba-blue.xcf")
        assert size > 0

    def test_nonexistent_file(self):
        with pytest.raises(XcfError):
            xcf_file_size(_SAMPLES / "ghost.xcf")

    def test_size_matches_actual(self):
        p = _SAMPLES / "1x1-red-rgb.xcf"
        assert xcf_file_size(p) == p.stat().st_size
