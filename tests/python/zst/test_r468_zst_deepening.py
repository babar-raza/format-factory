"""Sprint 239 ZST deepening — 2 new analytics functions, 12 tests.

Functions:
  zst_compressed_size_mod_100_plus_decompressed_size_mod_50_plus_max_byte_times_3
  zst_byte_sum_div_1000_plus_compressed_size_times_decompressed_size_mod_1000

Samples (samples/by-format/zst/valid/):
  text-compressed.zst   cs=272, ds=390, bs=35803, mx=121, mn=32
  minimal-synthetic.zst cs=10,  ds=1,   bs=0,     mx=0,   mn=0
  random-data.zst       cs=276, ds=1024, bs=130560, mx=255, mn=0

Expected:
  zst_compressed_size_mod_100_plus_decompressed_size_mod_50_plus_max_byte_times_3:
    text    = 272%100 + 390%50 + 121*3 = 72+40+363 = 475
    minimal = 10%100 + 1%50 + 0*3     = 10+1+0 = 11
    random  = 276%100 + 1024%50 + 255*3 = 76+24+765 = 865

  zst_byte_sum_div_1000_plus_compressed_size_times_decompressed_size_mod_1000:
    text    = 35803//1000 + 272*390%1000 = 35+106080%1000 = 35+80 = 115
    minimal = 0//1000 + 10*1%1000       = 0+10 = 10
    random  = 130560//1000 + 276*1024%1000 = 130+282624%1000 = 130+624 = 754
"""
from pathlib import Path

import pytest

from src.python.zst import (
    zst_compressed_size_mod_100_plus_decompressed_size_mod_50_plus_max_byte_times_3,
    zst_byte_sum_div_1000_plus_compressed_size_times_decompressed_size_mod_1000,
)

_VALID = Path("samples/by-format/zst/valid")
TEXT = _VALID / "text-compressed.zst"
MINIMAL = _VALID / "minimal-synthetic.zst"
RANDOM = _VALID / "random-data.zst"


class TestZstCompressedSizeMod100PlusDecompressedSizeMod50PlusMaxBytesTimes3:
    def test_text_value(self):
        assert zst_compressed_size_mod_100_plus_decompressed_size_mod_50_plus_max_byte_times_3(TEXT) == 475

    def test_minimal_value(self):
        assert zst_compressed_size_mod_100_plus_decompressed_size_mod_50_plus_max_byte_times_3(MINIMAL) == 11

    def test_random_value(self):
        assert zst_compressed_size_mod_100_plus_decompressed_size_mod_50_plus_max_byte_times_3(RANDOM) == 865

    def test_returns_int(self):
        assert isinstance(zst_compressed_size_mod_100_plus_decompressed_size_mod_50_plus_max_byte_times_3(TEXT), int)

    def test_all_distinct(self):
        vals = [
            zst_compressed_size_mod_100_plus_decompressed_size_mod_50_plus_max_byte_times_3(TEXT),
            zst_compressed_size_mod_100_plus_decompressed_size_mod_50_plus_max_byte_times_3(MINIMAL),
            zst_compressed_size_mod_100_plus_decompressed_size_mod_50_plus_max_byte_times_3(RANDOM),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert zst_compressed_size_mod_100_plus_decompressed_size_mod_50_plus_max_byte_times_3(TEXT) > 0


class TestZstByteSumDiv1000PlusCompressedSizeTimesDecompressedSizeMod1000:
    def test_text_value(self):
        assert zst_byte_sum_div_1000_plus_compressed_size_times_decompressed_size_mod_1000(TEXT) == 115

    def test_minimal_value(self):
        assert zst_byte_sum_div_1000_plus_compressed_size_times_decompressed_size_mod_1000(MINIMAL) == 10

    def test_random_value(self):
        assert zst_byte_sum_div_1000_plus_compressed_size_times_decompressed_size_mod_1000(RANDOM) == 754

    def test_returns_int(self):
        assert isinstance(zst_byte_sum_div_1000_plus_compressed_size_times_decompressed_size_mod_1000(TEXT), int)

    def test_all_distinct(self):
        vals = [
            zst_byte_sum_div_1000_plus_compressed_size_times_decompressed_size_mod_1000(TEXT),
            zst_byte_sum_div_1000_plus_compressed_size_times_decompressed_size_mod_1000(MINIMAL),
            zst_byte_sum_div_1000_plus_compressed_size_times_decompressed_size_mod_1000(RANDOM),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert zst_byte_sum_div_1000_plus_compressed_size_times_decompressed_size_mod_1000(TEXT) > 0
