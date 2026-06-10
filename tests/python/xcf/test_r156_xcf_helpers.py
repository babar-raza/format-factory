"""
test_r156_xcf_helpers.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT15-001
Added: 2026-06-10

Tests for XCF xcf_version and xcf_image_type_name functions.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from xcf.xcf_parser import xcf_version, xcf_image_type_name, XcfError

_SAMPLES = _REPO / "samples" / "by-format" / "xcf" / "valid"


class TestXcfVersion:
    def test_rgb_file(self):
        ver = xcf_version(_SAMPLES / "1x1-red-rgb.xcf")
        assert isinstance(ver, str)
        assert len(ver) > 0

    def test_gray_file(self):
        ver = xcf_version(_SAMPLES / "2x2-gray.xcf")
        assert isinstance(ver, str)

    def test_rgba_file(self):
        ver = xcf_version(_SAMPLES / "1x1-rgba-blue.xcf")
        assert isinstance(ver, str)

    def test_nonexistent_file(self, tmp_path):
        with pytest.raises(XcfError):
            xcf_version(tmp_path / "ghost.xcf")

    def test_invalid_file(self):
        invalid = _REPO / "samples" / "by-format" / "xcf" / "invalid" / "wrong-magic.xcf"
        with pytest.raises(XcfError):
            xcf_version(invalid)


class TestXcfImageTypeName:
    def test_rgb_type(self):
        name = xcf_image_type_name(_SAMPLES / "1x1-red-rgb.xcf")
        assert name == "RGB"

    def test_grayscale_type(self):
        name = xcf_image_type_name(_SAMPLES / "2x2-gray.xcf")
        assert name == "Grayscale"

    def test_rgba_is_rgb(self):
        name = xcf_image_type_name(_SAMPLES / "1x1-rgba-blue.xcf")
        assert name == "RGB"

    def test_nonexistent_file(self, tmp_path):
        with pytest.raises(XcfError):
            xcf_image_type_name(tmp_path / "ghost.xcf")
