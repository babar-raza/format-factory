"""Sprint 224 ZST deepening — 2 new analytics functions, 12 tests.

Functions:
  zst_byte_sum_div_compressed_size_plus_1_plus_compressed_size_div_10
  zst_max_byte_times_min_byte_plus_compressed_size_times_10

Samples (samples/by-format/zst/valid/):
  text-compressed.zst   cs=272, ds=390, bs=35803, mx=121, mn=32
  minimal-synthetic.zst cs=10,  ds=1,   bs=0,     mx=0,   mn=0
  random-data.zst       cs=276, ds=1024, bs=130560, mx=255, mn=0

Expected:
  zst_byte_sum_div_compressed_size_plus_1_plus_compressed_size_div_10:
    text    = 35803//(272+1) + 272//10  = 131 + 27 = 158
    minimal = 0//(10+1) + 10//10        = 0 + 1 = 1
    random  = 130560//(276+1) + 276//10 = 471 + 27 = 498

  zst_max_byte_times_min_byte_plus_compressed_size_times_10:
    text    = 121*32 + 272*10 = 3872 + 2720 = 6592
    minimal = 0*0 + 10*10     = 100
    random  = 255*0 + 276*10  = 2760
"""
from pathlib import Path

import pytest

from src.python.zst import (
    zst_byte_sum_div_compressed_size_plus_1_plus_compressed_size_div_10,
    zst_max_byte_times_min_byte_plus_compressed_size_times_10,
)

_VALID = Path("samples/by-format/zst/valid")
TEXT = _VALID / "text-compressed.zst"
MINIMAL = _VALID / "minimal-synthetic.zst"
RANDOM = _VALID / "random-data.zst"


class TestZstByteSumDivCompressedSizePlus1PlusCompressedSizeDiv10:
    def test_text_value(self):
        assert zst_byte_sum_div_compressed_size_plus_1_plus_compressed_size_div_10(TEXT) == 158

    def test_minimal_value(self):
        assert zst_byte_sum_div_compressed_size_plus_1_plus_compressed_size_div_10(MINIMAL) == 1

    def test_random_value(self):
        assert zst_byte_sum_div_compressed_size_plus_1_plus_compressed_size_div_10(RANDOM) == 498

    def test_returns_int(self):
        assert isinstance(zst_byte_sum_div_compressed_size_plus_1_plus_compressed_size_div_10(TEXT), int)

    def test_all_distinct(self):
        vals = [
            zst_byte_sum_div_compressed_size_plus_1_plus_compressed_size_div_10(TEXT),
            zst_byte_sum_div_compressed_size_plus_1_plus_compressed_size_div_10(MINIMAL),
            zst_byte_sum_div_compressed_size_plus_1_plus_compressed_size_div_10(RANDOM),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert zst_byte_sum_div_compressed_size_plus_1_plus_compressed_size_div_10(TEXT) > 0


class TestZstMaxByteTimesMinBytePlusCompressedSizeTimes10:
    def test_text_value(self):
        assert zst_max_byte_times_min_byte_plus_compressed_size_times_10(TEXT) == 6592

    def test_minimal_value(self):
        assert zst_max_byte_times_min_byte_plus_compressed_size_times_10(MINIMAL) == 100

    def test_random_value(self):
        assert zst_max_byte_times_min_byte_plus_compressed_size_times_10(RANDOM) == 2760

    def test_returns_int(self):
        assert isinstance(zst_max_byte_times_min_byte_plus_compressed_size_times_10(TEXT), int)

    def test_all_distinct(self):
        vals = [
            zst_max_byte_times_min_byte_plus_compressed_size_times_10(TEXT),
            zst_max_byte_times_min_byte_plus_compressed_size_times_10(MINIMAL),
            zst_max_byte_times_min_byte_plus_compressed_size_times_10(RANDOM),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert zst_max_byte_times_min_byte_plus_compressed_size_times_10(TEXT) > 0
