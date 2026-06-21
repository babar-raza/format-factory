"""Sprint 236 ZST deepening — 2 new analytics functions, 12 tests.

Functions:
  zst_max_byte_minus_min_byte_times_compressed_size_div_100_plus_decompressed_size
  zst_byte_sum_div_500_plus_max_byte_times_min_byte_div_10_plus_compressed_size

Samples (samples/by-format/zst/valid/):
  text-compressed.zst   cs=272, ds=390, bs=35803, mx=121, mn=32
  minimal-synthetic.zst cs=10,  ds=1,   bs=0,     mx=0,   mn=0
  random-data.zst       cs=276, ds=1024, bs=130560, mx=255, mn=0

Expected:
  zst_max_byte_minus_min_byte_times_compressed_size_div_100_plus_decompressed_size:
    text    = (121-32)*272//100 + 390 = 89*272//100+390 = 24208//100+390 = 242+390 = 632
    minimal = (0-0)*10//100 + 1       = 0+1 = 1
    random  = (255-0)*276//100 + 1024 = 70380//100+1024 = 703+1024 = 1727

  zst_byte_sum_div_500_plus_max_byte_times_min_byte_div_10_plus_compressed_size:
    text    = 35803//500 + 121*32//10 + 272 = 71+3872//10+272 = 71+387+272 = 730
    minimal = 0//500 + 0*0//10 + 10         = 0+0+10 = 10
    random  = 130560//500 + 255*0//10 + 276 = 261+0+276 = 537
"""
from pathlib import Path

import pytest

from src.python.zst import (
    zst_max_byte_minus_min_byte_times_compressed_size_div_100_plus_decompressed_size,
    zst_byte_sum_div_500_plus_max_byte_times_min_byte_div_10_plus_compressed_size,
)

_VALID = Path("samples/by-format/zst/valid")
TEXT = _VALID / "text-compressed.zst"
MINIMAL = _VALID / "minimal-synthetic.zst"
RANDOM = _VALID / "random-data.zst"


class TestZstMaxByteMinusMinByteTimesCompressedSizeDiv100PlusDecompressedSize:
    def test_text_value(self):
        assert zst_max_byte_minus_min_byte_times_compressed_size_div_100_plus_decompressed_size(TEXT) == 632

    def test_minimal_value(self):
        assert zst_max_byte_minus_min_byte_times_compressed_size_div_100_plus_decompressed_size(MINIMAL) == 1

    def test_random_value(self):
        assert zst_max_byte_minus_min_byte_times_compressed_size_div_100_plus_decompressed_size(RANDOM) == 1727

    def test_returns_int(self):
        assert isinstance(zst_max_byte_minus_min_byte_times_compressed_size_div_100_plus_decompressed_size(TEXT), int)

    def test_all_distinct(self):
        vals = [
            zst_max_byte_minus_min_byte_times_compressed_size_div_100_plus_decompressed_size(TEXT),
            zst_max_byte_minus_min_byte_times_compressed_size_div_100_plus_decompressed_size(MINIMAL),
            zst_max_byte_minus_min_byte_times_compressed_size_div_100_plus_decompressed_size(RANDOM),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert zst_max_byte_minus_min_byte_times_compressed_size_div_100_plus_decompressed_size(TEXT) > 0


class TestZstByteSumDiv500PlusMaxByteTimesMinByteDiv10PlusCompressedSize:
    def test_text_value(self):
        assert zst_byte_sum_div_500_plus_max_byte_times_min_byte_div_10_plus_compressed_size(TEXT) == 730

    def test_minimal_value(self):
        assert zst_byte_sum_div_500_plus_max_byte_times_min_byte_div_10_plus_compressed_size(MINIMAL) == 10

    def test_random_value(self):
        assert zst_byte_sum_div_500_plus_max_byte_times_min_byte_div_10_plus_compressed_size(RANDOM) == 537

    def test_returns_int(self):
        assert isinstance(zst_byte_sum_div_500_plus_max_byte_times_min_byte_div_10_plus_compressed_size(TEXT), int)

    def test_all_distinct(self):
        vals = [
            zst_byte_sum_div_500_plus_max_byte_times_min_byte_div_10_plus_compressed_size(TEXT),
            zst_byte_sum_div_500_plus_max_byte_times_min_byte_div_10_plus_compressed_size(MINIMAL),
            zst_byte_sum_div_500_plus_max_byte_times_min_byte_div_10_plus_compressed_size(RANDOM),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert zst_byte_sum_div_500_plus_max_byte_times_min_byte_div_10_plus_compressed_size(TEXT) > 0
