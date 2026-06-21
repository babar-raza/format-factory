"""Tests for ZST product deepening sprint 161.

New functions:
  zst_decompressed_size_times_compressed_size — decompressed size * compressed size
  zst_avg_byte_value_int                      — avg decompressed byte value as int
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.zst import (
    zst_decompressed_size_times_compressed_size,
    zst_avg_byte_value_int,
)

_TEXT = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "text-compressed.zst")
_MIN = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "minimal-synthetic.zst")
_RAND = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "random-data.zst")


class TestZstDecompressedSizeTimesCompressedSize:
    def test_return_type(self):
        assert isinstance(zst_decompressed_size_times_compressed_size(_TEXT), int)

    def test_exact_106080_for_text(self):
        # text-compressed: ds=390, cs=272 → 106080
        assert zst_decompressed_size_times_compressed_size(_TEXT) == 106080

    def test_exact_10_for_minimal(self):
        # minimal-synthetic: ds=1, cs=10 → 10
        assert zst_decompressed_size_times_compressed_size(_MIN) == 10

    def test_exact_282624_for_random(self):
        # random-data: ds=1024, cs=276 → 282624
        assert zst_decompressed_size_times_compressed_size(_RAND) == 282624

    def test_positive(self):
        assert zst_decompressed_size_times_compressed_size(_MIN) > 0

    def test_consistent(self):
        assert zst_decompressed_size_times_compressed_size(_TEXT) == zst_decompressed_size_times_compressed_size(_TEXT)


class TestZstAvgByteValueInt:
    def test_return_type(self):
        assert isinstance(zst_avg_byte_value_int(_TEXT), int)

    def test_exact_91_for_text(self):
        # text-compressed: byte_sum=35803, ds=390 → 35803//390 = 91
        assert zst_avg_byte_value_int(_TEXT) == 91

    def test_zero_for_minimal(self):
        # minimal-synthetic: byte_sum=0, ds=1 → 0
        assert zst_avg_byte_value_int(_MIN) == 0

    def test_exact_127_for_random(self):
        # random-data: byte_sum=130560, ds=1024 → 130560//1024 = 127
        assert zst_avg_byte_value_int(_RAND) == 127

    def test_nonnegative(self):
        assert zst_avg_byte_value_int(_MIN) >= 0

    def test_consistent(self):
        assert zst_avg_byte_value_int(_TEXT) == zst_avg_byte_value_int(_TEXT)
