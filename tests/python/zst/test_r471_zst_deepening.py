"""Sprint 242 ZST deepening — 2 new analytics functions, 12 tests.

Functions:
  zst_max_byte_plus_1_times_compressed_size_mod_100_plus_decompressed_size_mod_200
  zst_byte_sum_mod_500_plus_compressed_size_plus_max_byte_times_decompressed_size_div_100

Samples (samples/by-format/zst/valid/):
  text-compressed.zst   cs=272, ds=390, bs=35803, mx=121, mn=32
  minimal-synthetic.zst cs=10,  ds=1,   bs=0,     mx=0,   mn=0
  random-data.zst       cs=276, ds=1024, bs=130560, mx=255, mn=0

Expected:
  zst_max_byte_plus_1_times_compressed_size_mod_100_plus_decompressed_size_mod_200:
    text    = (121+1)*272%100 + 390%200 = 33184%100 + 190 = 84+190 = 274
    minimal = (0+1)*10%100 + 1%200      = 10 + 1 = 11
    random  = (255+1)*276%100 + 1024%200 = 70656%100 + 24 = 56+24 = 80

  zst_byte_sum_mod_500_plus_compressed_size_plus_max_byte_times_decompressed_size_div_100:
    text    = 35803%500 + 272 + 121*390//100 = 303+272+471 = 1046
    minimal = 0%500 + 10 + 0*1//100          = 0+10+0 = 10
    random  = 130560%500 + 276 + 255*1024//100 = 60+276+2611 = 2947
"""
from pathlib import Path

import pytest

from src.python.zst import (
    zst_max_byte_plus_1_times_compressed_size_mod_100_plus_decompressed_size_mod_200,
    zst_byte_sum_mod_500_plus_compressed_size_plus_max_byte_times_decompressed_size_div_100,
)

_VALID = Path("samples/by-format/zst/valid")
TEXT = _VALID / "text-compressed.zst"
MINIMAL = _VALID / "minimal-synthetic.zst"
RANDOM = _VALID / "random-data.zst"


class TestZstMaxBytePlus1TimesCompressedSizeMod100PlusDecompressedSizeMod200:
    def test_text_value(self):
        assert zst_max_byte_plus_1_times_compressed_size_mod_100_plus_decompressed_size_mod_200(TEXT) == 274

    def test_minimal_value(self):
        assert zst_max_byte_plus_1_times_compressed_size_mod_100_plus_decompressed_size_mod_200(MINIMAL) == 11

    def test_random_value(self):
        assert zst_max_byte_plus_1_times_compressed_size_mod_100_plus_decompressed_size_mod_200(RANDOM) == 80

    def test_returns_int(self):
        assert isinstance(zst_max_byte_plus_1_times_compressed_size_mod_100_plus_decompressed_size_mod_200(TEXT), int)

    def test_all_distinct(self):
        vals = [
            zst_max_byte_plus_1_times_compressed_size_mod_100_plus_decompressed_size_mod_200(TEXT),
            zst_max_byte_plus_1_times_compressed_size_mod_100_plus_decompressed_size_mod_200(MINIMAL),
            zst_max_byte_plus_1_times_compressed_size_mod_100_plus_decompressed_size_mod_200(RANDOM),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert zst_max_byte_plus_1_times_compressed_size_mod_100_plus_decompressed_size_mod_200(TEXT) > 0


class TestZstByteSumMod500PlusCompressedSizePlusMaxByteTimesDecompressedSizeDiv100:
    def test_text_value(self):
        assert zst_byte_sum_mod_500_plus_compressed_size_plus_max_byte_times_decompressed_size_div_100(TEXT) == 1046

    def test_minimal_value(self):
        assert zst_byte_sum_mod_500_plus_compressed_size_plus_max_byte_times_decompressed_size_div_100(MINIMAL) == 10

    def test_random_value(self):
        assert zst_byte_sum_mod_500_plus_compressed_size_plus_max_byte_times_decompressed_size_div_100(RANDOM) == 2947

    def test_returns_int(self):
        assert isinstance(zst_byte_sum_mod_500_plus_compressed_size_plus_max_byte_times_decompressed_size_div_100(TEXT), int)

    def test_all_distinct(self):
        vals = [
            zst_byte_sum_mod_500_plus_compressed_size_plus_max_byte_times_decompressed_size_div_100(TEXT),
            zst_byte_sum_mod_500_plus_compressed_size_plus_max_byte_times_decompressed_size_div_100(MINIMAL),
            zst_byte_sum_mod_500_plus_compressed_size_plus_max_byte_times_decompressed_size_div_100(RANDOM),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert zst_byte_sum_mod_500_plus_compressed_size_plus_max_byte_times_decompressed_size_div_100(TEXT) > 0
