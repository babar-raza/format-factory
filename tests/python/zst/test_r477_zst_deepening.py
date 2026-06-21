"""Sprint 248 ZST deepening — 2 new analytics functions, 12 tests.

Functions:
  zst_compressed_size_mod_7_times_100_plus_max_byte_times_decompressed_size_div_50_plus_10
  zst_byte_sum_mod_1000_plus_decompressed_size_times_3_mod_500_plus_compressed_size_mod_100

Samples (samples/by-format/zst/valid/):
  text-compressed.zst   cs=272, ds=390, bs=35803, mx=121, mn=32
  minimal-synthetic.zst cs=10,  ds=1,   bs=0,     mx=0,   mn=0
  random-data.zst       cs=276, ds=1024, bs=130560, mx=255, mn=0

Expected:
  zst_compressed_size_mod_7_times_100_plus_max_byte_times_decompressed_size_div_50_plus_10:
    text    = 272%7*100 + 121*390//50 + 10 = 6*100+943+10 = 1553
    minimal = 10%7*100 + 0*1//50 + 10     = 3*100+0+10 = 310
    random  = 276%7*100 + 255*1024//50 + 10 = 3*100+5222+10 = 5532

  zst_byte_sum_mod_1000_plus_decompressed_size_times_3_mod_500_plus_compressed_size_mod_100:
    text    = 35803%1000 + 390*3%500 + 272%100 = 803+170+72 = 1045
    minimal = 0%1000 + 1*3%500 + 10%100        = 0+3+10 = 13
    random  = 130560%1000 + 1024*3%500 + 276%100 = 560+72+76 = 708
"""
from pathlib import Path

import pytest

from src.python.zst import (
    zst_compressed_size_mod_7_times_100_plus_max_byte_times_decompressed_size_div_50_plus_10,
    zst_byte_sum_mod_1000_plus_decompressed_size_times_3_mod_500_plus_compressed_size_mod_100,
)

_VALID = Path("samples/by-format/zst/valid")
TEXT = _VALID / "text-compressed.zst"
MINIMAL = _VALID / "minimal-synthetic.zst"
RANDOM = _VALID / "random-data.zst"


class TestZstCompressedSizeMod7Times100PlusMaxByteTimesDecompressedSizeDiv50Plus10:
    def test_text_value(self):
        assert zst_compressed_size_mod_7_times_100_plus_max_byte_times_decompressed_size_div_50_plus_10(TEXT) == 1553

    def test_minimal_value(self):
        assert zst_compressed_size_mod_7_times_100_plus_max_byte_times_decompressed_size_div_50_plus_10(MINIMAL) == 310

    def test_random_value(self):
        assert zst_compressed_size_mod_7_times_100_plus_max_byte_times_decompressed_size_div_50_plus_10(RANDOM) == 5532

    def test_returns_int(self):
        assert isinstance(zst_compressed_size_mod_7_times_100_plus_max_byte_times_decompressed_size_div_50_plus_10(TEXT), int)

    def test_all_distinct(self):
        vals = [
            zst_compressed_size_mod_7_times_100_plus_max_byte_times_decompressed_size_div_50_plus_10(TEXT),
            zst_compressed_size_mod_7_times_100_plus_max_byte_times_decompressed_size_div_50_plus_10(MINIMAL),
            zst_compressed_size_mod_7_times_100_plus_max_byte_times_decompressed_size_div_50_plus_10(RANDOM),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert zst_compressed_size_mod_7_times_100_plus_max_byte_times_decompressed_size_div_50_plus_10(TEXT) > 0


class TestZstByteSumMod1000PlusDecompressedSizeTimes3Mod500PlusCompressedSizeMod100:
    def test_text_value(self):
        assert zst_byte_sum_mod_1000_plus_decompressed_size_times_3_mod_500_plus_compressed_size_mod_100(TEXT) == 1045

    def test_minimal_value(self):
        assert zst_byte_sum_mod_1000_plus_decompressed_size_times_3_mod_500_plus_compressed_size_mod_100(MINIMAL) == 13

    def test_random_value(self):
        assert zst_byte_sum_mod_1000_plus_decompressed_size_times_3_mod_500_plus_compressed_size_mod_100(RANDOM) == 708

    def test_returns_int(self):
        assert isinstance(zst_byte_sum_mod_1000_plus_decompressed_size_times_3_mod_500_plus_compressed_size_mod_100(TEXT), int)

    def test_all_distinct(self):
        vals = [
            zst_byte_sum_mod_1000_plus_decompressed_size_times_3_mod_500_plus_compressed_size_mod_100(TEXT),
            zst_byte_sum_mod_1000_plus_decompressed_size_times_3_mod_500_plus_compressed_size_mod_100(MINIMAL),
            zst_byte_sum_mod_1000_plus_decompressed_size_times_3_mod_500_plus_compressed_size_mod_100(RANDOM),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert zst_byte_sum_mod_1000_plus_decompressed_size_times_3_mod_500_plus_compressed_size_mod_100(TEXT) > 0
