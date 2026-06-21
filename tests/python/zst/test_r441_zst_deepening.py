"""Sprint 212 ZST deepening — 2 new analytics functions, 12 tests.

Functions:
  zst_max_byte_times_10_plus_compressed_size_div_5
  zst_byte_sum_mod_1000_plus_decompressed_size

Samples (samples/by-format/zst/valid/):
  text-compressed.zst   cs=272, ds=390, bs=35803, mx=121, mn=32
  minimal-synthetic.zst cs=10,  ds=1,   bs=0,     mx=0,   mn=0
  random-data.zst       cs=276, ds=1024, bs=130560, mx=255, mn=0

Expected:
  zst_max_byte_times_10_plus_compressed_size_div_5:
    text    = 121*10 + 272//5  = 1264
    minimal = 0*10 + 10//5     = 2
    random  = 255*10 + 276//5  = 2605

  zst_byte_sum_mod_1000_plus_decompressed_size:
    text    = 35803%1000 + 390  = 1193
    minimal = 0%1000 + 1        = 1
    random  = 130560%1000 + 1024 = 1584
"""
from pathlib import Path

import pytest

from src.python.zst import (
    zst_max_byte_times_10_plus_compressed_size_div_5,
    zst_byte_sum_mod_1000_plus_decompressed_size,
)

_VALID = Path("samples/by-format/zst/valid")
TEXT = _VALID / "text-compressed.zst"
MINIMAL = _VALID / "minimal-synthetic.zst"
RANDOM = _VALID / "random-data.zst"


class TestZstMaxByteTimes10PlusCompressedSizeDiv5:
    def test_text_value(self):
        assert zst_max_byte_times_10_plus_compressed_size_div_5(TEXT) == 1264

    def test_minimal_value(self):
        assert zst_max_byte_times_10_plus_compressed_size_div_5(MINIMAL) == 2

    def test_random_value(self):
        assert zst_max_byte_times_10_plus_compressed_size_div_5(RANDOM) == 2605

    def test_returns_int(self):
        assert isinstance(zst_max_byte_times_10_plus_compressed_size_div_5(TEXT), int)

    def test_all_distinct(self):
        vals = [
            zst_max_byte_times_10_plus_compressed_size_div_5(TEXT),
            zst_max_byte_times_10_plus_compressed_size_div_5(MINIMAL),
            zst_max_byte_times_10_plus_compressed_size_div_5(RANDOM),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert zst_max_byte_times_10_plus_compressed_size_div_5(TEXT) > 0


class TestZstByteSumMod1000PlusDecompressedSize:
    def test_text_value(self):
        assert zst_byte_sum_mod_1000_plus_decompressed_size(TEXT) == 1193

    def test_minimal_value(self):
        assert zst_byte_sum_mod_1000_plus_decompressed_size(MINIMAL) == 1

    def test_random_value(self):
        assert zst_byte_sum_mod_1000_plus_decompressed_size(RANDOM) == 1584

    def test_returns_int(self):
        assert isinstance(zst_byte_sum_mod_1000_plus_decompressed_size(TEXT), int)

    def test_all_distinct(self):
        vals = [
            zst_byte_sum_mod_1000_plus_decompressed_size(TEXT),
            zst_byte_sum_mod_1000_plus_decompressed_size(MINIMAL),
            zst_byte_sum_mod_1000_plus_decompressed_size(RANDOM),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert zst_byte_sum_mod_1000_plus_decompressed_size(TEXT) > 0
