"""Tests for zst_decompressed_exceeds_compressed and zst_decompressed_content_ratio (Sprint 98, R308)."""
import sys
from pathlib import Path

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.zst.zst_codec import zst_decompressed_exceeds_compressed, zst_decompressed_content_ratio

ZST = _REPO / "samples" / "by-format" / "zst" / "valid"


def test_decompressed_exceeds_compressed_block_false():
    assert zst_decompressed_exceeds_compressed(ZST / "block-128k.zst") is False


def test_decompressed_exceeds_compressed_dict_true():
    assert zst_decompressed_exceeds_compressed(ZST / "dict-compressed.zst") is True


def test_decompressed_exceeds_compressed_empty_false():
    assert zst_decompressed_exceeds_compressed(ZST / "empty-block.zst") is False


def test_decompressed_exceeds_compressed_returns_bool():
    assert isinstance(zst_decompressed_exceeds_compressed(ZST / "block-128k.zst"), bool)


def test_decompressed_exceeds_compressed_minimal_false():
    assert zst_decompressed_exceeds_compressed(ZST / "minimal-synthetic.zst") is False


def test_decompressed_content_ratio_block():
    assert abs(zst_decompressed_content_ratio(ZST / "block-128k.zst") - 0.5000) < 0.001


def test_decompressed_content_ratio_dict():
    assert zst_decompressed_content_ratio(ZST / "dict-compressed.zst") > 0.9


def test_decompressed_content_ratio_empty():
    assert abs(zst_decompressed_content_ratio(ZST / "empty-block.zst") - 0.0) < 0.001


def test_decompressed_content_ratio_returns_float():
    assert isinstance(zst_decompressed_content_ratio(ZST / "block-128k.zst"), float)


def test_decompressed_content_ratio_between_zero_and_one():
    val = zst_decompressed_content_ratio(ZST / "dict-compressed.zst")
    assert 0.0 <= val <= 1.0
