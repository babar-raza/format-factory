"""Sprint 203 ZST deepening — 2 new analytics functions, 12 tests.

Functions:
  zst_max_byte_plus_min_byte_times_compressed_size
  zst_decompressed_size_div_10_plus_byte_sum_div_1000

Samples (samples/by-format/zst/valid/):
  text-compressed.zst   cs=272, ds=390, bs=35803, mx=121, mn=32
  minimal-synthetic.zst cs=10,  ds=1,   bs=0,     mx=0,   mn=0
  random-data.zst       cs=276, ds=1024, bs=130560, mx=255, mn=0

Expected:
  zst_max_byte_plus_min_byte_times_compressed_size:
    text    = (121+32)*272  = 41616
    minimal = (0+0)*10      = 0
    random  = (255+0)*276   = 70380

  zst_decompressed_size_div_10_plus_byte_sum_div_1000:
    text    = 390//10 + 35803//1000 = 74
    minimal = 1//10 + 0//1000       = 0
    random  = 1024//10 + 130560//1000 = 232
"""
from pathlib import Path

import pytest

from src.python.zst import (
    zst_max_byte_plus_min_byte_times_compressed_size,
    zst_decompressed_size_div_10_plus_byte_sum_div_1000,
)

_VALID = Path("samples/by-format/zst/valid")
TEXT = _VALID / "text-compressed.zst"
MINIMAL = _VALID / "minimal-synthetic.zst"
RANDOM = _VALID / "random-data.zst"


class TestZstMaxBytePlusMinByteTimesCompressedSize:
    def test_text_value(self):
        assert zst_max_byte_plus_min_byte_times_compressed_size(TEXT) == 41616

    def test_minimal_value(self):
        assert zst_max_byte_plus_min_byte_times_compressed_size(MINIMAL) == 0

    def test_random_value(self):
        assert zst_max_byte_plus_min_byte_times_compressed_size(RANDOM) == 70380

    def test_returns_int(self):
        assert isinstance(zst_max_byte_plus_min_byte_times_compressed_size(TEXT), int)

    def test_random_largest(self):
        assert zst_max_byte_plus_min_byte_times_compressed_size(RANDOM) > zst_max_byte_plus_min_byte_times_compressed_size(TEXT)

    def test_non_negative(self):
        assert zst_max_byte_plus_min_byte_times_compressed_size(MINIMAL) >= 0


class TestZstDecompressedSizeDiv10PlusByteSumDiv1000:
    def test_text_value(self):
        assert zst_decompressed_size_div_10_plus_byte_sum_div_1000(TEXT) == 74

    def test_minimal_value(self):
        assert zst_decompressed_size_div_10_plus_byte_sum_div_1000(MINIMAL) == 0

    def test_random_value(self):
        assert zst_decompressed_size_div_10_plus_byte_sum_div_1000(RANDOM) == 232

    def test_returns_int(self):
        assert isinstance(zst_decompressed_size_div_10_plus_byte_sum_div_1000(TEXT), int)

    def test_all_distinct(self):
        vals = [
            zst_decompressed_size_div_10_plus_byte_sum_div_1000(TEXT),
            zst_decompressed_size_div_10_plus_byte_sum_div_1000(MINIMAL),
            zst_decompressed_size_div_10_plus_byte_sum_div_1000(RANDOM),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert zst_decompressed_size_div_10_plus_byte_sum_div_1000(TEXT) > 0
