"""Tests for ZST Sprint 43 gap closure.

Closes:
  GAP-ZST-FOSS-ZST_COMPRESS-001  (Zst Compression Saving)
  GAP-ZST-FOSS-ZST_IS_HIGHL-001  (Zst Is Highly Compressed)
  GAP-ZST-FOSS-ZST_IS_RLE_E-001  (Zst Is Rle Efficient)
  GAP-ZST-FOSS-ZST_FILE_SIZ-001  (Zst File Size Bytes)
  GAP-ZST-FOSS-ZST_IS_EMPTY-001  (Zst Is Empty Content)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.zst import (
    zst_compression_saving,
    zst_file_size_bytes,
    zst_is_empty_content,
    zst_is_highly_compressed,
    zst_is_rle_efficient,
)

_DIR = _REPO / "samples" / "by-format" / "zst" / "valid"
_EMPTY_BLOCK = str(_DIR / "empty-block.zst")
_MINIMAL_SYNTH = str(_DIR / "minimal-synthetic.zst")
_RLE_FIRST = str(_DIR / "rle-first-block.zst")
_BLOCK_128K = str(_DIR / "block-128k.zst")
_DICT_COMPRESSED = str(_DIR / "dict-compressed.zst")


class TestZstCompressionSaving:
    def test_return_type(self):
        assert isinstance(zst_compression_saving(_BLOCK_128K), int)

    def test_zero_for_block_128k(self):
        assert zst_compression_saving(_BLOCK_128K) == 0

    def test_exact_4086_for_dict_compressed(self):
        assert zst_compression_saving(_DICT_COMPRESSED) == 4086

    def test_exact_1048531_for_rle_first(self):
        assert zst_compression_saving(_RLE_FIRST) == 1048531

    def test_nonnegative(self):
        assert zst_compression_saving(_BLOCK_128K) >= 0

    def test_consistent_across_calls(self):
        assert zst_compression_saving(_BLOCK_128K) == zst_compression_saving(_BLOCK_128K)


class TestZstIsHighlyCompressed:
    def test_return_type(self):
        assert isinstance(zst_is_highly_compressed(_BLOCK_128K), bool)

    def test_false_for_block_128k(self):
        assert zst_is_highly_compressed(_BLOCK_128K) is False

    def test_true_for_minimal_synthetic(self):
        assert zst_is_highly_compressed(_MINIMAL_SYNTH) is True

    def test_consistent_across_calls(self):
        assert zst_is_highly_compressed(_BLOCK_128K) == zst_is_highly_compressed(_BLOCK_128K)


class TestZstIsRleEfficient:
    def test_return_type(self):
        assert isinstance(zst_is_rle_efficient(_BLOCK_128K), bool)

    def test_false_for_block_128k(self):
        assert zst_is_rle_efficient(_BLOCK_128K) is False

    def test_true_for_rle_first(self):
        assert zst_is_rle_efficient(_RLE_FIRST) is True

    def test_consistent_across_calls(self):
        assert zst_is_rle_efficient(_BLOCK_128K) == zst_is_rle_efficient(_BLOCK_128K)


class TestZstFileSizeBytes:
    def test_return_type(self):
        assert isinstance(zst_file_size_bytes(_EMPTY_BLOCK), int)

    def test_exact_11_for_empty_block(self):
        assert zst_file_size_bytes(_EMPTY_BLOCK) == 11

    def test_exact_10_for_minimal_synthetic(self):
        assert zst_file_size_bytes(_MINIMAL_SYNTH) == 10

    def test_positive(self):
        assert zst_file_size_bytes(_EMPTY_BLOCK) > 0

    def test_consistent_across_calls(self):
        assert zst_file_size_bytes(_EMPTY_BLOCK) == zst_file_size_bytes(_EMPTY_BLOCK)


class TestZstIsEmptyContent:
    def test_return_type(self):
        assert isinstance(zst_is_empty_content(_BLOCK_128K), bool)

    def test_false_for_block_128k(self):
        assert zst_is_empty_content(_BLOCK_128K) is False

    def test_true_for_empty_block(self):
        assert zst_is_empty_content(_EMPTY_BLOCK) is True

    def test_consistent_across_calls(self):
        assert zst_is_empty_content(_BLOCK_128K) == zst_is_empty_content(_BLOCK_128K)
