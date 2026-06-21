"""Sprint 227 ZST deepening — 2 new analytics functions, 12 tests.

Functions:
  zst_decompressed_size_plus_max_byte_times_compressed_size_div_100_plus_compressed_size_div_10
  zst_byte_sum_div_1000_plus_min_byte_times_compressed_size_div_100_plus_decompressed_size

Samples (samples/by-format/zst/valid/):
  text-compressed.zst   cs=272, ds=390, bs=35803, mx=121, mn=32
  minimal-synthetic.zst cs=10,  ds=1,   bs=0,     mx=0,   mn=0
  random-data.zst       cs=276, ds=1024, bs=130560, mx=255, mn=0

Expected:
  zst_decompressed_size_plus_max_byte_times_compressed_size_div_100_plus_compressed_size_div_10:
    text    = (390+121)*272//100 + 272//10 = 1389 + 27 = 1416
    minimal = (1+0)*10//100 + 10//10       = 0 + 1 = 1
    random  = (1024+255)*276//100 + 276//10 = 3530 + 27 = 3557

  zst_byte_sum_div_1000_plus_min_byte_times_compressed_size_div_100_plus_decompressed_size:
    text    = 35803//1000 + 32*272//100 + 390 = 35 + 87 + 390 = 512
    minimal = 0//1000 + 0*10//100 + 1          = 1
    random  = 130560//1000 + 0*276//100 + 1024 = 130 + 0 + 1024 = 1154
"""
from pathlib import Path

import pytest

from src.python.zst import (
    zst_decompressed_size_plus_max_byte_times_compressed_size_div_100_plus_compressed_size_div_10,
    zst_byte_sum_div_1000_plus_min_byte_times_compressed_size_div_100_plus_decompressed_size,
)

_VALID = Path("samples/by-format/zst/valid")
TEXT = _VALID / "text-compressed.zst"
MINIMAL = _VALID / "minimal-synthetic.zst"
RANDOM = _VALID / "random-data.zst"


class TestZstDecompressedSizePlusMaxByteTimesCompressedSizeDiv100PlusCompressedSizeDiv10:
    def test_text_value(self):
        assert zst_decompressed_size_plus_max_byte_times_compressed_size_div_100_plus_compressed_size_div_10(TEXT) == 1416

    def test_minimal_value(self):
        assert zst_decompressed_size_plus_max_byte_times_compressed_size_div_100_plus_compressed_size_div_10(MINIMAL) == 1

    def test_random_value(self):
        assert zst_decompressed_size_plus_max_byte_times_compressed_size_div_100_plus_compressed_size_div_10(RANDOM) == 3557

    def test_returns_int(self):
        assert isinstance(zst_decompressed_size_plus_max_byte_times_compressed_size_div_100_plus_compressed_size_div_10(TEXT), int)

    def test_all_distinct(self):
        vals = [
            zst_decompressed_size_plus_max_byte_times_compressed_size_div_100_plus_compressed_size_div_10(TEXT),
            zst_decompressed_size_plus_max_byte_times_compressed_size_div_100_plus_compressed_size_div_10(MINIMAL),
            zst_decompressed_size_plus_max_byte_times_compressed_size_div_100_plus_compressed_size_div_10(RANDOM),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert zst_decompressed_size_plus_max_byte_times_compressed_size_div_100_plus_compressed_size_div_10(TEXT) > 0


class TestZstByteSumDiv1000PlusMinByteTimesCompressedSizeDiv100PlusDecompressedSize:
    def test_text_value(self):
        assert zst_byte_sum_div_1000_plus_min_byte_times_compressed_size_div_100_plus_decompressed_size(TEXT) == 512

    def test_minimal_value(self):
        assert zst_byte_sum_div_1000_plus_min_byte_times_compressed_size_div_100_plus_decompressed_size(MINIMAL) == 1

    def test_random_value(self):
        assert zst_byte_sum_div_1000_plus_min_byte_times_compressed_size_div_100_plus_decompressed_size(RANDOM) == 1154

    def test_returns_int(self):
        assert isinstance(zst_byte_sum_div_1000_plus_min_byte_times_compressed_size_div_100_plus_decompressed_size(TEXT), int)

    def test_all_distinct(self):
        vals = [
            zst_byte_sum_div_1000_plus_min_byte_times_compressed_size_div_100_plus_decompressed_size(TEXT),
            zst_byte_sum_div_1000_plus_min_byte_times_compressed_size_div_100_plus_decompressed_size(MINIMAL),
            zst_byte_sum_div_1000_plus_min_byte_times_compressed_size_div_100_plus_decompressed_size(RANDOM),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert zst_byte_sum_div_1000_plus_min_byte_times_compressed_size_div_100_plus_decompressed_size(TEXT) > 0
