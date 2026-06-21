"""Sprint 230 ZST deepening — 2 new analytics functions, 12 tests.

Functions:
  zst_decompressed_size_times_max_byte_plus_1_div_10_plus_compressed_size_mod_100
  zst_byte_sum_mod_1000_plus_decompressed_size_times_2_plus_compressed_size_mod_50

Samples (samples/by-format/zst/valid/):
  text-compressed.zst   cs=272, ds=390, bs=35803, mx=121, mn=32
  minimal-synthetic.zst cs=10,  ds=1,   bs=0,     mx=0,   mn=0
  random-data.zst       cs=276, ds=1024, bs=130560, mx=255, mn=0

Expected:
  zst_decompressed_size_times_max_byte_plus_1_div_10_plus_compressed_size_mod_100:
    text    = 390*(121+1)//10 + 272%100 = 47580//10 + 72 = 4758+72 = 4830
    minimal = 1*(0+1)//10 + 10%100     = 0+10 = 10
    random  = 1024*(255+1)//10 + 276%100 = 262144//10+76 = 26214+76 = 26290

  zst_byte_sum_mod_1000_plus_decompressed_size_times_2_plus_compressed_size_mod_50:
    text    = 35803%1000 + 390*2 + 272%50 = 803+780+22 = 1605
    minimal = 0%1000 + 1*2 + 10%50       = 0+2+10 = 12
    random  = 130560%1000 + 1024*2 + 276%50 = 560+2048+26 = 2634
"""
from pathlib import Path

import pytest

from src.python.zst import (
    zst_decompressed_size_times_max_byte_plus_1_div_10_plus_compressed_size_mod_100,
    zst_byte_sum_mod_1000_plus_decompressed_size_times_2_plus_compressed_size_mod_50,
)

_VALID = Path("samples/by-format/zst/valid")
TEXT = _VALID / "text-compressed.zst"
MINIMAL = _VALID / "minimal-synthetic.zst"
RANDOM = _VALID / "random-data.zst"


class TestZstDecompressedSizeTimesMaxBytePlus1Div10PlusCompressedSizeMod100:
    def test_text_value(self):
        assert zst_decompressed_size_times_max_byte_plus_1_div_10_plus_compressed_size_mod_100(TEXT) == 4830

    def test_minimal_value(self):
        assert zst_decompressed_size_times_max_byte_plus_1_div_10_plus_compressed_size_mod_100(MINIMAL) == 10

    def test_random_value(self):
        assert zst_decompressed_size_times_max_byte_plus_1_div_10_plus_compressed_size_mod_100(RANDOM) == 26290

    def test_returns_int(self):
        assert isinstance(zst_decompressed_size_times_max_byte_plus_1_div_10_plus_compressed_size_mod_100(TEXT), int)

    def test_all_distinct(self):
        vals = [
            zst_decompressed_size_times_max_byte_plus_1_div_10_plus_compressed_size_mod_100(TEXT),
            zst_decompressed_size_times_max_byte_plus_1_div_10_plus_compressed_size_mod_100(MINIMAL),
            zst_decompressed_size_times_max_byte_plus_1_div_10_plus_compressed_size_mod_100(RANDOM),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert zst_decompressed_size_times_max_byte_plus_1_div_10_plus_compressed_size_mod_100(TEXT) > 0


class TestZstByteSumMod1000PlusDecompressedSizeTimes2PlusCompressedSizeMod50:
    def test_text_value(self):
        assert zst_byte_sum_mod_1000_plus_decompressed_size_times_2_plus_compressed_size_mod_50(TEXT) == 1605

    def test_minimal_value(self):
        assert zst_byte_sum_mod_1000_plus_decompressed_size_times_2_plus_compressed_size_mod_50(MINIMAL) == 12

    def test_random_value(self):
        assert zst_byte_sum_mod_1000_plus_decompressed_size_times_2_plus_compressed_size_mod_50(RANDOM) == 2634

    def test_returns_int(self):
        assert isinstance(zst_byte_sum_mod_1000_plus_decompressed_size_times_2_plus_compressed_size_mod_50(TEXT), int)

    def test_all_distinct(self):
        vals = [
            zst_byte_sum_mod_1000_plus_decompressed_size_times_2_plus_compressed_size_mod_50(TEXT),
            zst_byte_sum_mod_1000_plus_decompressed_size_times_2_plus_compressed_size_mod_50(MINIMAL),
            zst_byte_sum_mod_1000_plus_decompressed_size_times_2_plus_compressed_size_mod_50(RANDOM),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert zst_byte_sum_mod_1000_plus_decompressed_size_times_2_plus_compressed_size_mod_50(TEXT) > 0
