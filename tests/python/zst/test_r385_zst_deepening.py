"""Tests for ZST product deepening sprint 156.

New functions:
  zst_byte_sum_minus_decompressed_size  — decompressed byte sum minus decompressed size
  zst_compressed_size_plus_frame_count  — compressed file size plus frame count
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.zst import (
    zst_byte_sum_minus_decompressed_size,
    zst_compressed_size_plus_frame_count,
)

_TEXT = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "text-compressed.zst")
_MIN = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "minimal-synthetic.zst")
_RAND = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "random-data.zst")


class TestZstByteSumMinusDecompressedSize:
    def test_return_type(self):
        assert isinstance(zst_byte_sum_minus_decompressed_size(_TEXT), int)

    def test_exact_35413_for_text(self):
        # text-compressed: byte_sum=35803, decomp=390 → 35413
        assert zst_byte_sum_minus_decompressed_size(_TEXT) == 35413

    def test_zero_for_minimal(self):
        # minimal-synthetic: byte_sum=0, decomp=1 → max(0, -1) = 0
        assert zst_byte_sum_minus_decompressed_size(_MIN) == 0

    def test_exact_129536_for_random(self):
        # random-data: byte_sum=130560, decomp=1024 → 129536
        assert zst_byte_sum_minus_decompressed_size(_RAND) == 129536

    def test_nonnegative(self):
        assert zst_byte_sum_minus_decompressed_size(_MIN) >= 0

    def test_consistent(self):
        assert zst_byte_sum_minus_decompressed_size(_TEXT) == zst_byte_sum_minus_decompressed_size(_TEXT)


class TestZstCompressedSizePlusFrameCount:
    def test_return_type(self):
        assert isinstance(zst_compressed_size_plus_frame_count(_TEXT), int)

    def test_exact_273_for_text(self):
        # text-compressed: compressed=272, frames=1 → 273
        assert zst_compressed_size_plus_frame_count(_TEXT) == 273

    def test_exact_11_for_minimal(self):
        # minimal-synthetic: compressed=10, frames=1 → 11
        assert zst_compressed_size_plus_frame_count(_MIN) == 11

    def test_exact_277_for_random(self):
        # random-data: compressed=276, frames=1 → 277
        assert zst_compressed_size_plus_frame_count(_RAND) == 277

    def test_positive(self):
        assert zst_compressed_size_plus_frame_count(_MIN) > 0

    def test_consistent(self):
        assert zst_compressed_size_plus_frame_count(_TEXT) == zst_compressed_size_plus_frame_count(_TEXT)
