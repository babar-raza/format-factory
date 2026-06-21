"""Sprint 209 ZST deepening — 2 new analytics functions, 12 tests.

Functions:
  zst_decompressed_size_mod_100_plus_max_byte
  zst_compressed_size_div_5_plus_byte_sum_div_10000

Samples (samples/by-format/zst/valid/):
  text-compressed.zst   cs=272, ds=390, bs=35803, mx=121, mn=32
  minimal-synthetic.zst cs=10,  ds=1,   bs=0,     mx=0,   mn=0
  random-data.zst       cs=276, ds=1024, bs=130560, mx=255, mn=0

Expected:
  zst_decompressed_size_mod_100_plus_max_byte:
    text    = 390%100 + 121  = 211
    minimal = 1%100 + 0      = 1
    random  = 1024%100 + 255 = 279

  zst_compressed_size_div_5_plus_byte_sum_div_10000:
    text    = 272//5 + 35803//10000   = 57
    minimal = 10//5 + 0//10000        = 2
    random  = 276//5 + 130560//10000  = 68
"""
from pathlib import Path

import pytest

from src.python.zst import (
    zst_decompressed_size_mod_100_plus_max_byte,
    zst_compressed_size_div_5_plus_byte_sum_div_10000,
)

_VALID = Path("samples/by-format/zst/valid")
TEXT = _VALID / "text-compressed.zst"
MINIMAL = _VALID / "minimal-synthetic.zst"
RANDOM = _VALID / "random-data.zst"


class TestZstDecompressedSizeMod100PlusMaxByte:
    def test_text_value(self):
        assert zst_decompressed_size_mod_100_plus_max_byte(TEXT) == 211

    def test_minimal_value(self):
        assert zst_decompressed_size_mod_100_plus_max_byte(MINIMAL) == 1

    def test_random_value(self):
        assert zst_decompressed_size_mod_100_plus_max_byte(RANDOM) == 279

    def test_returns_int(self):
        assert isinstance(zst_decompressed_size_mod_100_plus_max_byte(TEXT), int)

    def test_all_distinct(self):
        vals = [
            zst_decompressed_size_mod_100_plus_max_byte(TEXT),
            zst_decompressed_size_mod_100_plus_max_byte(MINIMAL),
            zst_decompressed_size_mod_100_plus_max_byte(RANDOM),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert zst_decompressed_size_mod_100_plus_max_byte(TEXT) > 0


class TestZstCompressedSizeDiv5PlusByteSumDiv10000:
    def test_text_value(self):
        assert zst_compressed_size_div_5_plus_byte_sum_div_10000(TEXT) == 57

    def test_minimal_value(self):
        assert zst_compressed_size_div_5_plus_byte_sum_div_10000(MINIMAL) == 2

    def test_random_value(self):
        assert zst_compressed_size_div_5_plus_byte_sum_div_10000(RANDOM) == 68

    def test_returns_int(self):
        assert isinstance(zst_compressed_size_div_5_plus_byte_sum_div_10000(TEXT), int)

    def test_all_distinct(self):
        vals = [
            zst_compressed_size_div_5_plus_byte_sum_div_10000(TEXT),
            zst_compressed_size_div_5_plus_byte_sum_div_10000(MINIMAL),
            zst_compressed_size_div_5_plus_byte_sum_div_10000(RANDOM),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert zst_compressed_size_div_5_plus_byte_sum_div_10000(TEXT) > 0
