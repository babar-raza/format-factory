"""
test_xcf_image_ops_advancement.py -- XCF image operations content verification.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-13
Tests xcf_layer_count, xcf_image_dimensions, xcf_version, xcf_pixel_count,
xcf_is_rgb, xcf_is_grayscale with exact value assertions from real samples.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

_SAMPLES = _REPO / "samples" / "by-format" / "xcf" / "valid"

from xcf.xcf_parser import (
    xcf_layer_count,
    xcf_image_dimensions,
    xcf_version,
    xcf_pixel_count,
    xcf_is_rgb,
    xcf_is_grayscale,
    xcf_file_size,
)

_RGB_FILE = str(_SAMPLES / "1x1-red-rgb.xcf")
_GRAY_FILE = str(_SAMPLES / "2x2-gray.xcf")


def test_rgb_layer_count_is_one():
    assert xcf_layer_count(_RGB_FILE) == 1


def test_rgb_dimensions_are_one_by_one():
    dims = xcf_image_dimensions(_RGB_FILE)
    assert dims["width"] == 1
    assert dims["height"] == 1


def test_rgb_pixel_count_is_one():
    assert xcf_pixel_count(_RGB_FILE) == 1


def test_rgb_is_rgb_true():
    assert xcf_is_rgb(_RGB_FILE) is True


def test_rgb_is_grayscale_false():
    assert xcf_is_grayscale(_RGB_FILE) is False


def test_gray_dimensions_are_two_by_two():
    dims = xcf_image_dimensions(_GRAY_FILE)
    assert dims["width"] == 2
    assert dims["height"] == 2


def test_gray_is_grayscale_true():
    assert xcf_is_grayscale(_GRAY_FILE) is True


def test_gray_is_rgb_false():
    assert xcf_is_rgb(_GRAY_FILE) is False


def test_file_size_is_positive():
    size = xcf_file_size(_RGB_FILE)
    assert size > 0


def test_version_is_string():
    ver = xcf_version(_RGB_FILE)
    assert isinstance(ver, str)
    assert len(ver) > 0
