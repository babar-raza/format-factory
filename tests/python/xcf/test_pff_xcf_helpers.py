"""Tests for XCF inspection helpers — product-fix-forward sprint."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from xcf import xcf_layer_count, xcf_image_dimensions, XcfError

_FIXTURES = _REPO / "samples" / "by-format" / "xcf" / "valid"
_INVALID = _REPO / "samples" / "by-format" / "xcf" / "invalid"


def test_layer_count_1x1_red():
    count = xcf_layer_count(_FIXTURES / "1x1-red-rgb.xcf")
    assert isinstance(count, int)
    assert count >= 1


def test_layer_count_2x2_gray():
    count = xcf_layer_count(_FIXTURES / "2x2-gray.xcf")
    assert isinstance(count, int)
    assert count >= 1


def test_image_dimensions_1x1_red():
    dims = xcf_image_dimensions(_FIXTURES / "1x1-red-rgb.xcf")
    assert dims["width"] == 1
    assert dims["height"] == 1


def test_image_dimensions_2x2_gray():
    dims = xcf_image_dimensions(_FIXTURES / "2x2-gray.xcf")
    assert dims["width"] == 2
    assert dims["height"] == 2


def test_image_dimensions_returns_dict():
    dims = xcf_image_dimensions(_FIXTURES / "1x1-red-rgb.xcf")
    assert isinstance(dims, dict)
    assert "width" in dims
    assert "height" in dims


def test_layer_count_invalid_raises():
    with pytest.raises(XcfError):
        xcf_layer_count(_INVALID / "wrong-magic.xcf")


def test_image_dimensions_invalid_raises():
    with pytest.raises(XcfError):
        xcf_image_dimensions(_INVALID / "wrong-magic.xcf")


def test_layer_count_nonexistent_raises():
    with pytest.raises(XcfError):
        xcf_layer_count("/nonexistent/file.xcf")


def test_callable_from_package():
    from xcf import xcf_layer_count as fn1, xcf_image_dimensions as fn2
    assert callable(fn1)
    assert callable(fn2)
