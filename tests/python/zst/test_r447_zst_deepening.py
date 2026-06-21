"""Sprint 218 ZST deepening — 2 new analytics functions, 12 tests.

Functions:
  zst_max_byte_times_decompressed_size_plus_compressed_size_div_10
  zst_byte_sum_div_100_plus_max_byte_times_2_plus_compressed_size

Samples (samples/by-format/zst/valid/):
  text-compressed.zst   cs=272, ds=390, bs=35803, mx=121, mn=32
  minimal-synthetic.zst cs=10,  ds=1,   bs=0,     mx=0,   mn=0
  random-data.zst       cs=276, ds=1024, bs=130560, mx=255, mn=0

Expected:
  zst_max_byte_times_decompressed_size_plus_compressed_size_div_10:
    text    = 121*390 + 272//10  = 47217
    minimal = 0*1 + 10//10       = 1
    random  = 255*1024 + 276//10 = 261147

  zst_byte_sum_div_100_plus_max_byte_times_2_plus_compressed_size:
    text    = 35803//100 + 121*2 + 272 = 358 + 242 + 272 = 872
    minimal = 0//100 + 0*2 + 10       = 10
    random  = 130560//100 + 255*2 + 276 = 1305 + 510 + 276 = 2091
"""
from pathlib import Path

import pytest

from src.python.zst import (
    zst_max_byte_times_decompressed_size_plus_compressed_size_div_10,
    zst_byte_sum_div_100_plus_max_byte_times_2_plus_compressed_size,
)

_VALID = Path("samples/by-format/zst/valid")
TEXT = _VALID / "text-compressed.zst"
MINIMAL = _VALID / "minimal-synthetic.zst"
RANDOM = _VALID / "random-data.zst"


class TestZstMaxByteTimesDecompressedSizePlusCompressedSizeDiv10:
    def test_text_value(self):
        assert zst_max_byte_times_decompressed_size_plus_compressed_size_div_10(TEXT) == 47217

    def test_minimal_value(self):
        assert zst_max_byte_times_decompressed_size_plus_compressed_size_div_10(MINIMAL) == 1

    def test_random_value(self):
        assert zst_max_byte_times_decompressed_size_plus_compressed_size_div_10(RANDOM) == 261147

    def test_returns_int(self):
        assert isinstance(zst_max_byte_times_decompressed_size_plus_compressed_size_div_10(TEXT), int)

    def test_all_distinct(self):
        vals = [
            zst_max_byte_times_decompressed_size_plus_compressed_size_div_10(TEXT),
            zst_max_byte_times_decompressed_size_plus_compressed_size_div_10(MINIMAL),
            zst_max_byte_times_decompressed_size_plus_compressed_size_div_10(RANDOM),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert zst_max_byte_times_decompressed_size_plus_compressed_size_div_10(TEXT) > 0


class TestZstByteSumDiv100PlusMaxByteTimesT2PlusCompressedSize:
    def test_text_value(self):
        assert zst_byte_sum_div_100_plus_max_byte_times_2_plus_compressed_size(TEXT) == 872

    def test_minimal_value(self):
        assert zst_byte_sum_div_100_plus_max_byte_times_2_plus_compressed_size(MINIMAL) == 10

    def test_random_value(self):
        assert zst_byte_sum_div_100_plus_max_byte_times_2_plus_compressed_size(RANDOM) == 2091

    def test_returns_int(self):
        assert isinstance(zst_byte_sum_div_100_plus_max_byte_times_2_plus_compressed_size(TEXT), int)

    def test_all_distinct(self):
        vals = [
            zst_byte_sum_div_100_plus_max_byte_times_2_plus_compressed_size(TEXT),
            zst_byte_sum_div_100_plus_max_byte_times_2_plus_compressed_size(MINIMAL),
            zst_byte_sum_div_100_plus_max_byte_times_2_plus_compressed_size(RANDOM),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert zst_byte_sum_div_100_plus_max_byte_times_2_plus_compressed_size(TEXT) > 0
