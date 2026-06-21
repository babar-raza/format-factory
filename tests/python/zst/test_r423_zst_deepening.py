"""Tests for ZST product deepening sprint 194.

New functions:
  zst_decompressed_size_plus_max_byte_times_compressed_size_div_10  — ds + mx*cs//10
  zst_compressed_size_times_10_plus_decompressed_size_div_10  — cs*10 + ds//10
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.zst import (
    zst_decompressed_size_plus_max_byte_times_compressed_size_div_10,
    zst_compressed_size_times_10_plus_decompressed_size_div_10,
)

_TEXT = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "text-compressed.zst")
_MINI = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "minimal-synthetic.zst")
_RAND = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "random-data.zst")


class TestZstDecompressedSizePlusMaxByteTimesCompressedSizeDiv10:
    def test_return_type(self):
        assert isinstance(zst_decompressed_size_plus_max_byte_times_compressed_size_div_10(_TEXT), int)

    def test_exact_3681_for_text(self):
        # text-compressed: ds=390, mx=121, cs=272 → 390 + 121*272//10 = 3681
        assert zst_decompressed_size_plus_max_byte_times_compressed_size_div_10(_TEXT) == 3681

    def test_exact_1_for_minimal(self):
        # minimal-synthetic: ds=1, mx=0, cs=10 → 1 + 0*10//10 = 1
        assert zst_decompressed_size_plus_max_byte_times_compressed_size_div_10(_MINI) == 1

    def test_exact_8062_for_random(self):
        # random-data: ds=1024, mx=255, cs=276 → 1024 + 255*276//10 = 8062
        assert zst_decompressed_size_plus_max_byte_times_compressed_size_div_10(_RAND) == 8062

    def test_nonnegative(self):
        assert zst_decompressed_size_plus_max_byte_times_compressed_size_div_10(_TEXT) >= 0

    def test_consistent(self):
        assert zst_decompressed_size_plus_max_byte_times_compressed_size_div_10(_RAND) == zst_decompressed_size_plus_max_byte_times_compressed_size_div_10(_RAND)


class TestZstCompressedSizeTimes10PlusDecompressedSizeDiv10:
    def test_return_type(self):
        assert isinstance(zst_compressed_size_times_10_plus_decompressed_size_div_10(_TEXT), int)

    def test_exact_2759_for_text(self):
        # text-compressed: cs=272, ds=390 → 272*10 + 390//10 = 2759
        assert zst_compressed_size_times_10_plus_decompressed_size_div_10(_TEXT) == 2759

    def test_exact_100_for_minimal(self):
        # minimal-synthetic: cs=10, ds=1 → 10*10 + 1//10 = 100
        assert zst_compressed_size_times_10_plus_decompressed_size_div_10(_MINI) == 100

    def test_exact_2862_for_random(self):
        # random-data: cs=276, ds=1024 → 276*10 + 1024//10 = 2862
        assert zst_compressed_size_times_10_plus_decompressed_size_div_10(_RAND) == 2862

    def test_nonnegative(self):
        assert zst_compressed_size_times_10_plus_decompressed_size_div_10(_TEXT) >= 0

    def test_consistent(self):
        assert zst_compressed_size_times_10_plus_decompressed_size_div_10(_RAND) == zst_compressed_size_times_10_plus_decompressed_size_div_10(_RAND)
