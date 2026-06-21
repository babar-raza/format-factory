"""Tests for ZST product deepening sprint 165.

New functions:
  zst_compressed_size_times_avg_byte_value  — compressed size * avg byte value int
  zst_decompressed_size_div_compressed_size — decompressed size // compressed size
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.zst import (
    zst_compressed_size_times_avg_byte_value,
    zst_decompressed_size_div_compressed_size,
)

_TEXT = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "text-compressed.zst")
_MIN = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "minimal-synthetic.zst")
_RAND = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "random-data.zst")


class TestZstCompressedSizeTimesAvgByteValue:
    def test_return_type(self):
        assert isinstance(zst_compressed_size_times_avg_byte_value(_TEXT), int)

    def test_exact_24752_for_text(self):
        # text-compressed: cs=272, avg=91 → 24752
        assert zst_compressed_size_times_avg_byte_value(_TEXT) == 24752

    def test_zero_for_minimal(self):
        # minimal-synthetic: cs=10, avg=0 → 0
        assert zst_compressed_size_times_avg_byte_value(_MIN) == 0

    def test_exact_35052_for_random(self):
        # random-data: cs=276, avg=127 → 35052
        assert zst_compressed_size_times_avg_byte_value(_RAND) == 35052

    def test_nonnegative(self):
        assert zst_compressed_size_times_avg_byte_value(_MIN) >= 0

    def test_consistent(self):
        assert zst_compressed_size_times_avg_byte_value(_TEXT) == zst_compressed_size_times_avg_byte_value(_TEXT)


class TestZstDecompressedSizeDivCompressedSize:
    def test_return_type(self):
        assert isinstance(zst_decompressed_size_div_compressed_size(_TEXT), int)

    def test_exact_1_for_text(self):
        # text-compressed: 390 // 272 = 1
        assert zst_decompressed_size_div_compressed_size(_TEXT) == 1

    def test_zero_for_minimal(self):
        # minimal-synthetic: 1 // 10 = 0
        assert zst_decompressed_size_div_compressed_size(_MIN) == 0

    def test_exact_3_for_random(self):
        # random-data: 1024 // 276 = 3
        assert zst_decompressed_size_div_compressed_size(_RAND) == 3

    def test_nonnegative(self):
        assert zst_decompressed_size_div_compressed_size(_MIN) >= 0

    def test_consistent(self):
        assert zst_decompressed_size_div_compressed_size(_TEXT) == zst_decompressed_size_div_compressed_size(_TEXT)
