"""Tests for xcf_bytes_per_layer, xcf_is_landscape,
zst_compression_saving_percentage, zst_is_empty_decompressed (Sprint 117, R327).
"""
import sys
from pathlib import Path

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf.xcf_parser import xcf_bytes_per_layer, xcf_is_landscape
from src.python.zst.zst_codec import zst_compression_saving_percentage, zst_is_empty_decompressed

XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
ZST = _REPO / "samples" / "by-format" / "zst" / "valid"


def test_xcf_bpl_red():
    assert abs(xcf_bytes_per_layer(XCF / "1x1-red-rgb.xcf") - 177.0) < 0.1


def test_xcf_bpl_blue():
    assert abs(xcf_bytes_per_layer(XCF / "1x1-rgba-blue.xcf") - 178.0) < 0.1


def test_xcf_bpl_gray():
    assert abs(xcf_bytes_per_layer(XCF / "2x2-gray.xcf") - 178.0) < 0.1


def test_xcf_bpl_returns_float():
    assert isinstance(xcf_bytes_per_layer(XCF / "1x1-red-rgb.xcf"), float)


def test_xcf_bpl_positive():
    assert xcf_bytes_per_layer(XCF / "1x1-red-rgb.xcf") > 0.0


def test_xcf_landscape_red():
    assert xcf_is_landscape(XCF / "1x1-red-rgb.xcf") is False


def test_xcf_landscape_blue():
    assert xcf_is_landscape(XCF / "1x1-rgba-blue.xcf") is False


def test_xcf_landscape_gray():
    assert xcf_is_landscape(XCF / "2x2-gray.xcf") is False


def test_xcf_landscape_returns_bool():
    assert isinstance(xcf_is_landscape(XCF / "1x1-red-rgb.xcf"), bool)


def test_xcf_landscape_type_check():
    val = xcf_is_landscape(XCF / "2x2-gray.xcf")
    assert val is True or val is False


def test_zst_saving_block():
    assert abs(zst_compression_saving_percentage(ZST / "block-128k.zst") - (-0.01)) < 0.1


def test_zst_saving_dict():
    assert abs(zst_compression_saving_percentage(ZST / "dict-compressed.zst") - 98.22) < 0.1


def test_zst_saving_empty():
    assert abs(zst_compression_saving_percentage(ZST / "empty-block.zst") - 0.0) < 0.01


def test_zst_saving_returns_float():
    assert isinstance(zst_compression_saving_percentage(ZST / "block-128k.zst"), float)


def test_zst_saving_dict_positive():
    assert zst_compression_saving_percentage(ZST / "dict-compressed.zst") > 0.0


def test_zst_empty_block():
    assert zst_is_empty_decompressed(ZST / "block-128k.zst") is False


def test_zst_empty_dict():
    assert zst_is_empty_decompressed(ZST / "dict-compressed.zst") is False


def test_zst_empty_empty():
    assert zst_is_empty_decompressed(ZST / "empty-block.zst") is True


def test_zst_empty_returns_bool():
    assert isinstance(zst_is_empty_decompressed(ZST / "block-128k.zst"), bool)


def test_zst_empty_consistent():
    assert zst_is_empty_decompressed(ZST / "empty-block.zst") is True
