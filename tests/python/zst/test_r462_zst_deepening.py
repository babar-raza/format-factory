"""Sprint 233 ZST deepening — 2 new analytics functions, 12 tests.

Functions:
  zst_compressed_size_times_decompressed_size_div_1000_plus_max_byte_plus_1_mod_100
  zst_byte_sum_div_10000_plus_decompressed_size_mod_100_plus_compressed_size_div_20

Samples (samples/by-format/zst/valid/):
  text-compressed.zst   cs=272, ds=390, bs=35803, mx=121, mn=32
  minimal-synthetic.zst cs=10,  ds=1,   bs=0,     mx=0,   mn=0
  random-data.zst       cs=276, ds=1024, bs=130560, mx=255, mn=0

Expected:
  zst_compressed_size_times_decompressed_size_div_1000_plus_max_byte_plus_1_mod_100:
    text    = 272*390//1000 + (121+1)%100 = 106080//1000+122%100 = 106+22 = 128
    minimal = 10*1//1000 + (0+1)%100     = 0+1 = 1
    random  = 276*1024//1000 + (255+1)%100 = 282624//1000+256%100 = 282+56 = 338

  zst_byte_sum_div_10000_plus_decompressed_size_mod_100_plus_compressed_size_div_20:
    text    = 35803//10000 + 390%100 + 272//20 = 3+90+13 = 106
    minimal = 0//10000 + 1%100 + 10//20       = 0+1+0 = 1
    random  = 130560//10000 + 1024%100 + 276//20 = 13+24+13 = 50
"""
from pathlib import Path

import pytest

from src.python.zst import (
    zst_compressed_size_times_decompressed_size_div_1000_plus_max_byte_plus_1_mod_100,
    zst_byte_sum_div_10000_plus_decompressed_size_mod_100_plus_compressed_size_div_20,
)

_VALID = Path("samples/by-format/zst/valid")
TEXT = _VALID / "text-compressed.zst"
MINIMAL = _VALID / "minimal-synthetic.zst"
RANDOM = _VALID / "random-data.zst"


class TestZstCompressedSizeTimesDecompressedSizeDiv1000PlusMaxBytePlus1Mod100:
    def test_text_value(self):
        assert zst_compressed_size_times_decompressed_size_div_1000_plus_max_byte_plus_1_mod_100(TEXT) == 128

    def test_minimal_value(self):
        assert zst_compressed_size_times_decompressed_size_div_1000_plus_max_byte_plus_1_mod_100(MINIMAL) == 1

    def test_random_value(self):
        assert zst_compressed_size_times_decompressed_size_div_1000_plus_max_byte_plus_1_mod_100(RANDOM) == 338

    def test_returns_int(self):
        assert isinstance(zst_compressed_size_times_decompressed_size_div_1000_plus_max_byte_plus_1_mod_100(TEXT), int)

    def test_all_distinct(self):
        vals = [
            zst_compressed_size_times_decompressed_size_div_1000_plus_max_byte_plus_1_mod_100(TEXT),
            zst_compressed_size_times_decompressed_size_div_1000_plus_max_byte_plus_1_mod_100(MINIMAL),
            zst_compressed_size_times_decompressed_size_div_1000_plus_max_byte_plus_1_mod_100(RANDOM),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert zst_compressed_size_times_decompressed_size_div_1000_plus_max_byte_plus_1_mod_100(TEXT) > 0


class TestZstByteSumDiv10000PlusDecompressedSizeMod100PlusCompressedSizeDiv20:
    def test_text_value(self):
        assert zst_byte_sum_div_10000_plus_decompressed_size_mod_100_plus_compressed_size_div_20(TEXT) == 106

    def test_minimal_value(self):
        assert zst_byte_sum_div_10000_plus_decompressed_size_mod_100_plus_compressed_size_div_20(MINIMAL) == 1

    def test_random_value(self):
        assert zst_byte_sum_div_10000_plus_decompressed_size_mod_100_plus_compressed_size_div_20(RANDOM) == 50

    def test_returns_int(self):
        assert isinstance(zst_byte_sum_div_10000_plus_decompressed_size_mod_100_plus_compressed_size_div_20(TEXT), int)

    def test_all_distinct(self):
        vals = [
            zst_byte_sum_div_10000_plus_decompressed_size_mod_100_plus_compressed_size_div_20(TEXT),
            zst_byte_sum_div_10000_plus_decompressed_size_mod_100_plus_compressed_size_div_20(MINIMAL),
            zst_byte_sum_div_10000_plus_decompressed_size_mod_100_plus_compressed_size_div_20(RANDOM),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert zst_byte_sum_div_10000_plus_decompressed_size_mod_100_plus_compressed_size_div_20(TEXT) > 0
