"""Sprint 200 ZST deepening — 2 new analytics functions, 12 tests.

Functions:
  zst_byte_sum_plus_decompressed_size_times_100
  zst_compressed_size_times_decompressed_size_div_100

Samples (samples/by-format/zst/valid/):
  text-compressed.zst   cs=272, ds=390, bs=35803
  minimal-synthetic.zst cs=10,  ds=1,   bs=0
  random-data.zst       cs=276, ds=1024, bs=130560

Expected:
  zst_byte_sum_plus_decompressed_size_times_100:
    text    = 35803 + 390*100  = 74803
    minimal = 0     + 1*100    = 100
    random  = 130560 + 1024*100 = 232960

  zst_compressed_size_times_decompressed_size_div_100:
    text    = 272*390//100   = 1060
    minimal = 10*1//100      = 0
    random  = 276*1024//100  = 2826
"""
from pathlib import Path

import pytest

from src.python.zst import (
    zst_byte_sum_plus_decompressed_size_times_100,
    zst_compressed_size_times_decompressed_size_div_100,
)

_VALID = Path("samples/by-format/zst/valid")
TEXT = _VALID / "text-compressed.zst"
MINIMAL = _VALID / "minimal-synthetic.zst"
RANDOM = _VALID / "random-data.zst"


class TestZstByteSumPlusDecompressedSizeTimes100:
    def test_text_value(self):
        assert zst_byte_sum_plus_decompressed_size_times_100(TEXT) == 74803

    def test_minimal_value(self):
        assert zst_byte_sum_plus_decompressed_size_times_100(MINIMAL) == 100

    def test_random_value(self):
        assert zst_byte_sum_plus_decompressed_size_times_100(RANDOM) == 232960

    def test_returns_int(self):
        assert isinstance(zst_byte_sum_plus_decompressed_size_times_100(TEXT), int)

    def test_random_largest(self):
        assert zst_byte_sum_plus_decompressed_size_times_100(RANDOM) > zst_byte_sum_plus_decompressed_size_times_100(TEXT)

    def test_positive(self):
        assert zst_byte_sum_plus_decompressed_size_times_100(TEXT) > 0


class TestZstCompressedSizeTimesDecompressedSizeDiv100:
    def test_text_value(self):
        assert zst_compressed_size_times_decompressed_size_div_100(TEXT) == 1060

    def test_minimal_value(self):
        assert zst_compressed_size_times_decompressed_size_div_100(MINIMAL) == 0

    def test_random_value(self):
        assert zst_compressed_size_times_decompressed_size_div_100(RANDOM) == 2826

    def test_returns_int(self):
        assert isinstance(zst_compressed_size_times_decompressed_size_div_100(TEXT), int)

    def test_all_distinct(self):
        vals = [
            zst_compressed_size_times_decompressed_size_div_100(TEXT),
            zst_compressed_size_times_decompressed_size_div_100(MINIMAL),
            zst_compressed_size_times_decompressed_size_div_100(RANDOM),
        ]
        assert len(set(vals)) == 3

    def test_random_largest(self):
        assert zst_compressed_size_times_decompressed_size_div_100(RANDOM) > zst_compressed_size_times_decompressed_size_div_100(TEXT)
