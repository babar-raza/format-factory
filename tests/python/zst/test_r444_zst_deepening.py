"""Sprint 215 ZST deepening — 2 new analytics functions, 12 tests.

Functions:
  zst_decompressed_size_plus_max_byte_times_compressed_size_div_100
  zst_byte_sum_mod_500_plus_compressed_size_times_2

Samples (samples/by-format/zst/valid/):
  text-compressed.zst   cs=272, ds=390, bs=35803, mx=121, mn=32
  minimal-synthetic.zst cs=10,  ds=1,   bs=0,     mx=0,   mn=0
  random-data.zst       cs=276, ds=1024, bs=130560, mx=255, mn=0

Expected:
  zst_decompressed_size_plus_max_byte_times_compressed_size_div_100:
    text    = 390 + 121*272//100 = 719
    minimal = 1 + 0*10//100     = 1
    random  = 1024 + 255*276//100 = 1727

  zst_byte_sum_mod_500_plus_compressed_size_times_2:
    text    = 35803%500 + 272*2 = 303 + 544 = 847
    minimal = 0%500 + 10*2     = 20
    random  = 130560%500 + 276*2 = 60 + 552 = 612
"""
from pathlib import Path

import pytest

from src.python.zst import (
    zst_decompressed_size_plus_max_byte_times_compressed_size_div_100,
    zst_byte_sum_mod_500_plus_compressed_size_times_2,
)

_VALID = Path("samples/by-format/zst/valid")
TEXT = _VALID / "text-compressed.zst"
MINIMAL = _VALID / "minimal-synthetic.zst"
RANDOM = _VALID / "random-data.zst"


class TestZstDecompressedSizePlusMaxByteTimesCompressedSizeDiv100:
    def test_text_value(self):
        assert zst_decompressed_size_plus_max_byte_times_compressed_size_div_100(TEXT) == 719

    def test_minimal_value(self):
        assert zst_decompressed_size_plus_max_byte_times_compressed_size_div_100(MINIMAL) == 1

    def test_random_value(self):
        assert zst_decompressed_size_plus_max_byte_times_compressed_size_div_100(RANDOM) == 1727

    def test_returns_int(self):
        assert isinstance(zst_decompressed_size_plus_max_byte_times_compressed_size_div_100(TEXT), int)

    def test_all_distinct(self):
        vals = [
            zst_decompressed_size_plus_max_byte_times_compressed_size_div_100(TEXT),
            zst_decompressed_size_plus_max_byte_times_compressed_size_div_100(MINIMAL),
            zst_decompressed_size_plus_max_byte_times_compressed_size_div_100(RANDOM),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert zst_decompressed_size_plus_max_byte_times_compressed_size_div_100(TEXT) > 0


class TestZstByteSumMod500PlusCompressedSizeTimes2:
    def test_text_value(self):
        assert zst_byte_sum_mod_500_plus_compressed_size_times_2(TEXT) == 847

    def test_minimal_value(self):
        assert zst_byte_sum_mod_500_plus_compressed_size_times_2(MINIMAL) == 20

    def test_random_value(self):
        assert zst_byte_sum_mod_500_plus_compressed_size_times_2(RANDOM) == 612

    def test_returns_int(self):
        assert isinstance(zst_byte_sum_mod_500_plus_compressed_size_times_2(TEXT), int)

    def test_all_distinct(self):
        vals = [
            zst_byte_sum_mod_500_plus_compressed_size_times_2(TEXT),
            zst_byte_sum_mod_500_plus_compressed_size_times_2(MINIMAL),
            zst_byte_sum_mod_500_plus_compressed_size_times_2(RANDOM),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert zst_byte_sum_mod_500_plus_compressed_size_times_2(TEXT) > 0
