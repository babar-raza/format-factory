"""
Tests for XCF analytics gap closure (2 FOSS gaps).
Closes: GAP-XCF-FOSS-XCF_IS_MULT-001, GAP-XCF-FOSS-XCF_FILE_B-001
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from xcf.xcf_parser import (
    xcf_is_multi_pixel,
    xcf_file_bytes_per_layer,
)

_XCF_1x1 = _REPO / "samples/by-format/xcf/valid/1x1-red-rgb.xcf"
_XCF_2x2 = _REPO / "samples/by-format/xcf/valid/2x2-gray.xcf"
_XCF_RGBA = _REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf"


class TestXcfIsMultiPixel:
    def test_returns_bool(self):
        assert isinstance(xcf_is_multi_pixel(_XCF_1x1), bool)

    def test_single_pixel_is_not_multi(self):
        # 1x1 canvas has exactly 1 pixel
        assert xcf_is_multi_pixel(_XCF_1x1) is False

    def test_2x2_is_multi_pixel(self):
        # 2x2 canvas has 4 pixels
        assert xcf_is_multi_pixel(_XCF_2x2) is True

    def test_consistent_result(self):
        r1 = xcf_is_multi_pixel(_XCF_RGBA)
        r2 = xcf_is_multi_pixel(_XCF_RGBA)
        assert r1 == r2


class TestXcfFileBytesPerLayer:
    def test_returns_float(self):
        assert isinstance(xcf_file_bytes_per_layer(_XCF_1x1), float)

    def test_positive(self):
        # XCF file with at least 1 layer must have > 0 bytes
        assert xcf_file_bytes_per_layer(_XCF_1x1) > 0.0

    def test_nonnegative(self):
        assert xcf_file_bytes_per_layer(_XCF_2x2) >= 0.0

    def test_consistent_across_calls(self):
        r1 = xcf_file_bytes_per_layer(_XCF_RGBA)
        r2 = xcf_file_bytes_per_layer(_XCF_RGBA)
        assert r1 == pytest.approx(r2)
