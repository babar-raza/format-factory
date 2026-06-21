"""Tests for xcf_image_area and xcf_file_size_per_pixel (Sprint 110, R320)."""
import sys
from pathlib import Path

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf.xcf_parser import xcf_image_area, xcf_file_size_per_pixel

XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"


def test_area_red():
    assert xcf_image_area(XCF / "1x1-red-rgb.xcf") == 1


def test_area_blue():
    assert xcf_image_area(XCF / "1x1-rgba-blue.xcf") == 1


def test_area_gray():
    assert xcf_image_area(XCF / "2x2-gray.xcf") == 4


def test_area_returns_int():
    assert isinstance(xcf_image_area(XCF / "1x1-red-rgb.xcf"), int)


def test_area_positive():
    assert xcf_image_area(XCF / "2x2-gray.xcf") > 0


def test_fspp_red():
    assert abs(xcf_file_size_per_pixel(XCF / "1x1-red-rgb.xcf") - 177.0) < 0.01


def test_fspp_blue():
    assert abs(xcf_file_size_per_pixel(XCF / "1x1-rgba-blue.xcf") - 178.0) < 0.01


def test_fspp_gray():
    assert abs(xcf_file_size_per_pixel(XCF / "2x2-gray.xcf") - 44.5) < 0.01


def test_fspp_returns_float():
    assert isinstance(xcf_file_size_per_pixel(XCF / "1x1-red-rgb.xcf"), float)


def test_fspp_positive():
    assert xcf_file_size_per_pixel(XCF / "2x2-gray.xcf") > 0.0
