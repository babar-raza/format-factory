"""
test_r161_xcf_is_grayscale.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT21-001
Added: 2026-06-10

Tests for XCF xcf_is_grayscale function.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from xcf.xcf_parser import xcf_is_grayscale, XcfError

_SAMPLES = _REPO / "samples" / "by-format" / "xcf" / "valid"


class TestXcfIsGrayscale:
    def test_gray_image(self):
        assert xcf_is_grayscale(_SAMPLES / "2x2-gray.xcf") is True

    def test_rgb_image(self):
        assert xcf_is_grayscale(_SAMPLES / "1x1-red-rgb.xcf") is False

    def test_rgba_image(self):
        assert xcf_is_grayscale(_SAMPLES / "1x1-rgba-blue.xcf") is False

    def test_nonexistent_file(self):
        with pytest.raises(XcfError):
            xcf_is_grayscale(_SAMPLES / "ghost.xcf")
