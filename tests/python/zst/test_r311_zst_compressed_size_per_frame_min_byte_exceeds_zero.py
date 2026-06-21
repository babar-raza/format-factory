"""Tests for zst_compressed_size_per_frame and zst_min_byte_exceeds_zero (Sprint 101, R311)."""
import sys
from pathlib import Path

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.zst.zst_codec import zst_compressed_size_per_frame, zst_min_byte_exceeds_zero

ZST = _REPO / "samples" / "by-format" / "zst" / "valid"


def test_compressed_size_per_frame_block_128k():
    assert abs(zst_compressed_size_per_frame(ZST / "block-128k.zst") - 131081.0) < 1.0


def test_compressed_size_per_frame_dict_compressed():
    assert abs(zst_compressed_size_per_frame(ZST / "dict-compressed.zst") - 74.0) < 1.0


def test_compressed_size_per_frame_empty():
    assert abs(zst_compressed_size_per_frame(ZST / "empty-block.zst") - 11.0) < 1.0


def test_compressed_size_per_frame_returns_float():
    assert isinstance(zst_compressed_size_per_frame(ZST / "block-128k.zst"), float)


def test_compressed_size_per_frame_positive():
    assert zst_compressed_size_per_frame(ZST / "text-compressed.zst") > 0.0


def test_min_byte_exceeds_zero_block():
    assert zst_min_byte_exceeds_zero(ZST / "block-128k.zst") is False


def test_min_byte_exceeds_zero_dict():
    assert zst_min_byte_exceeds_zero(ZST / "dict-compressed.zst") is True


def test_min_byte_exceeds_zero_empty():
    assert zst_min_byte_exceeds_zero(ZST / "empty-block.zst") is False


def test_min_byte_exceeds_zero_returns_bool():
    assert isinstance(zst_min_byte_exceeds_zero(ZST / "block-128k.zst"), bool)


def test_min_byte_exceeds_zero_text():
    assert zst_min_byte_exceeds_zero(ZST / "text-compressed.zst") is True
