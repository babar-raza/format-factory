"""Tests for xcf_width().

Sprint: product-deepening-rnext88
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf.xcf_parser import xcf_width

XCF_SAMPLES = _REPO / "samples" / "by-format" / "xcf" / "valid"


class TestXcfWidth:
    def test_import(self):
        assert callable(xcf_width)

    def test_1x1_red_width(self):
        assert xcf_width(XCF_SAMPLES / "1x1-red-rgb.xcf") == 1

    def test_1x1_rgba_blue_width(self):
        assert xcf_width(XCF_SAMPLES / "1x1-rgba-blue.xcf") == 1

    def test_2x2_gray_width(self):
        assert xcf_width(XCF_SAMPLES / "2x2-gray.xcf") == 2

    def test_returns_int(self):
        result = xcf_width(XCF_SAMPLES / "1x1-red-rgb.xcf")
        assert isinstance(result, int)

    def test_positive(self):
        for sample in XCF_SAMPLES.iterdir():
            if sample.suffix == ".xcf":
                assert xcf_width(sample) > 0
