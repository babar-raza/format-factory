"""Sprint 245 ZST deepening — 2 new analytics functions, 12 tests.

Functions:
  zst_decompressed_size_mod_100_plus_compressed_size_mod_50_plus_max_byte_plus_1_times_10
  zst_byte_sum_div_2000_plus_decompressed_size_mod_300_plus_compressed_size_times_3_mod_1000

Samples (samples/by-format/zst/valid/):
  text-compressed.zst   cs=272, ds=390, bs=35803, mx=121, mn=32
  minimal-synthetic.zst cs=10,  ds=1,   bs=0,     mx=0,   mn=0
  random-data.zst       cs=276, ds=1024, bs=130560, mx=255, mn=0

Expected:
  zst_decompressed_size_mod_100_plus_compressed_size_mod_50_plus_max_byte_plus_1_times_10:
    text    = 390%100 + 272%50 + (121+1)*10 = 90+22+1220 = 1332
    minimal = 1%100 + 10%50 + (0+1)*10     = 1+10+10 = 21
    random  = 1024%100 + 276%50 + (255+1)*10 = 24+26+2560 = 2610

  zst_byte_sum_div_2000_plus_decompressed_size_mod_300_plus_compressed_size_times_3_mod_1000:
    text    = 35803//2000 + 390%300 + 272*3%1000 = 17+90+816 = 923
    minimal = 0//2000 + 1%300 + 10*3%1000        = 0+1+30 = 31
    random  = 130560//2000 + 1024%300 + 276*3%1000 = 65+124+828 = 1017
"""
from pathlib import Path

import pytest

from src.python.zst import (
    zst_decompressed_size_mod_100_plus_compressed_size_mod_50_plus_max_byte_plus_1_times_10,
    zst_byte_sum_div_2000_plus_decompressed_size_mod_300_plus_compressed_size_times_3_mod_1000,
)

_VALID = Path("samples/by-format/zst/valid")
TEXT = _VALID / "text-compressed.zst"
MINIMAL = _VALID / "minimal-synthetic.zst"
RANDOM = _VALID / "random-data.zst"


class TestZstDecompressedSizeMod100PlusCompressedSizeMod50PlusMaxBytePlus1Times10:
    def test_text_value(self):
        assert zst_decompressed_size_mod_100_plus_compressed_size_mod_50_plus_max_byte_plus_1_times_10(TEXT) == 1332

    def test_minimal_value(self):
        assert zst_decompressed_size_mod_100_plus_compressed_size_mod_50_plus_max_byte_plus_1_times_10(MINIMAL) == 21

    def test_random_value(self):
        assert zst_decompressed_size_mod_100_plus_compressed_size_mod_50_plus_max_byte_plus_1_times_10(RANDOM) == 2610

    def test_returns_int(self):
        assert isinstance(zst_decompressed_size_mod_100_plus_compressed_size_mod_50_plus_max_byte_plus_1_times_10(TEXT), int)

    def test_all_distinct(self):
        vals = [
            zst_decompressed_size_mod_100_plus_compressed_size_mod_50_plus_max_byte_plus_1_times_10(TEXT),
            zst_decompressed_size_mod_100_plus_compressed_size_mod_50_plus_max_byte_plus_1_times_10(MINIMAL),
            zst_decompressed_size_mod_100_plus_compressed_size_mod_50_plus_max_byte_plus_1_times_10(RANDOM),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert zst_decompressed_size_mod_100_plus_compressed_size_mod_50_plus_max_byte_plus_1_times_10(TEXT) > 0


class TestZstByteSumDiv2000PlusDecompressedSizeMod300PlusCompressedSizeTimes3Mod1000:
    def test_text_value(self):
        assert zst_byte_sum_div_2000_plus_decompressed_size_mod_300_plus_compressed_size_times_3_mod_1000(TEXT) == 923

    def test_minimal_value(self):
        assert zst_byte_sum_div_2000_plus_decompressed_size_mod_300_plus_compressed_size_times_3_mod_1000(MINIMAL) == 31

    def test_random_value(self):
        assert zst_byte_sum_div_2000_plus_decompressed_size_mod_300_plus_compressed_size_times_3_mod_1000(RANDOM) == 1017

    def test_returns_int(self):
        assert isinstance(zst_byte_sum_div_2000_plus_decompressed_size_mod_300_plus_compressed_size_times_3_mod_1000(TEXT), int)

    def test_all_distinct(self):
        vals = [
            zst_byte_sum_div_2000_plus_decompressed_size_mod_300_plus_compressed_size_times_3_mod_1000(TEXT),
            zst_byte_sum_div_2000_plus_decompressed_size_mod_300_plus_compressed_size_times_3_mod_1000(MINIMAL),
            zst_byte_sum_div_2000_plus_decompressed_size_mod_300_plus_compressed_size_times_3_mod_1000(RANDOM),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert zst_byte_sum_div_2000_plus_decompressed_size_mod_300_plus_compressed_size_times_3_mod_1000(TEXT) > 0
