"""Tests for ZST product deepening sprint 197.

New functions:
  zst_byte_sum_div_100_plus_compressed_size  — bs//100 + cs
  zst_decompressed_size_times_compressed_size_div_1000  — ds*cs//1000
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.zst import (
    zst_byte_sum_div_100_plus_compressed_size,
    zst_decompressed_size_times_compressed_size_div_1000,
)

_TEXT = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "text-compressed.zst")
_MINI = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "minimal-synthetic.zst")
_RAND = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "random-data.zst")


class TestZstByteSumDiv100PlusCompressedSize:
    def test_return_type(self):
        assert isinstance(zst_byte_sum_div_100_plus_compressed_size(_TEXT), int)

    def test_exact_630_for_text(self):
        # text-compressed: bs=35803, cs=272 → 35803//100 + 272 = 630
        assert zst_byte_sum_div_100_plus_compressed_size(_TEXT) == 630

    def test_exact_10_for_minimal(self):
        # minimal-synthetic: bs=0, cs=10 → 0//100 + 10 = 10
        assert zst_byte_sum_div_100_plus_compressed_size(_MINI) == 10

    def test_exact_1581_for_random(self):
        # random-data: bs=130560, cs=276 → 130560//100 + 276 = 1581
        assert zst_byte_sum_div_100_plus_compressed_size(_RAND) == 1581

    def test_nonnegative(self):
        assert zst_byte_sum_div_100_plus_compressed_size(_TEXT) >= 0

    def test_consistent(self):
        assert zst_byte_sum_div_100_plus_compressed_size(_RAND) == zst_byte_sum_div_100_plus_compressed_size(_RAND)


class TestZstDecompressedSizeTimesCompressedSizeDiv1000:
    def test_return_type(self):
        assert isinstance(zst_decompressed_size_times_compressed_size_div_1000(_TEXT), int)

    def test_exact_106_for_text(self):
        # text-compressed: ds=390, cs=272 → 390*272//1000 = 106
        assert zst_decompressed_size_times_compressed_size_div_1000(_TEXT) == 106

    def test_exact_0_for_minimal(self):
        # minimal-synthetic: ds=1, cs=10 → 1*10//1000 = 0
        assert zst_decompressed_size_times_compressed_size_div_1000(_MINI) == 0

    def test_exact_282_for_random(self):
        # random-data: ds=1024, cs=276 → 1024*276//1000 = 282
        assert zst_decompressed_size_times_compressed_size_div_1000(_RAND) == 282

    def test_nonnegative(self):
        assert zst_decompressed_size_times_compressed_size_div_1000(_TEXT) >= 0

    def test_consistent(self):
        assert zst_decompressed_size_times_compressed_size_div_1000(_RAND) == zst_decompressed_size_times_compressed_size_div_1000(_RAND)
