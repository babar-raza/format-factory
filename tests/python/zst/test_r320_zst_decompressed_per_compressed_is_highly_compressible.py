"""Tests for zst_decompressed_per_compressed and zst_is_highly_compressible (Sprint 110, R320)."""
import sys
from pathlib import Path

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.zst.zst_codec import zst_decompressed_per_compressed, zst_is_highly_compressible

ZST = _REPO / "samples" / "by-format" / "zst" / "valid"


def test_ratio_block():
    assert abs(zst_decompressed_per_compressed(ZST / "block-128k.zst") - 0.9999) < 0.001


def test_ratio_dict():
    assert abs(zst_decompressed_per_compressed(ZST / "dict-compressed.zst") - 56.2162) < 0.01


def test_ratio_empty():
    assert abs(zst_decompressed_per_compressed(ZST / "empty-block.zst") - 0.0) < 0.001


def test_ratio_returns_float():
    assert isinstance(zst_decompressed_per_compressed(ZST / "block-128k.zst"), float)


def test_ratio_nonnegative():
    assert zst_decompressed_per_compressed(ZST / "block-128k.zst") >= 0.0


def test_highly_block():
    assert zst_is_highly_compressible(ZST / "block-128k.zst") is False


def test_highly_dict():
    assert zst_is_highly_compressible(ZST / "dict-compressed.zst") is True


def test_highly_empty():
    assert zst_is_highly_compressible(ZST / "empty-block.zst") is False


def test_highly_returns_bool():
    assert isinstance(zst_is_highly_compressible(ZST / "block-128k.zst"), bool)


def test_highly_consistent():
    ratio = zst_decompressed_per_compressed(ZST / "dict-compressed.zst")
    assert (ratio > 10.0) == zst_is_highly_compressible(ZST / "dict-compressed.zst")
