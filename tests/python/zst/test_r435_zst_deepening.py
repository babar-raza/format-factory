"""Sprint 206 ZST deepening — 2 new analytics functions, 12 tests.

Functions:
  zst_compressed_size_plus_max_byte_minus_min_byte
  zst_byte_sum_div_decompressed_size

Samples (samples/by-format/zst/valid/):
  text-compressed.zst   cs=272, ds=390, bs=35803, mx=121, mn=32
  minimal-synthetic.zst cs=10,  ds=1,   bs=0,     mx=0,   mn=0
  random-data.zst       cs=276, ds=1024, bs=130560, mx=255, mn=0

Expected:
  zst_compressed_size_plus_max_byte_minus_min_byte:
    text    = 272 + 121 - 32  = 361
    minimal = 10 + 0 - 0      = 10
    random  = 276 + 255 - 0   = 531

  zst_byte_sum_div_decompressed_size:
    text    = 35803 // 390    = 91
    minimal = 0 // 1          = 0
    random  = 130560 // 1024  = 127
"""
from pathlib import Path

import pytest

from src.python.zst import (
    zst_compressed_size_plus_max_byte_minus_min_byte,
    zst_byte_sum_div_decompressed_size,
)

_VALID = Path("samples/by-format/zst/valid")
TEXT = _VALID / "text-compressed.zst"
MINIMAL = _VALID / "minimal-synthetic.zst"
RANDOM = _VALID / "random-data.zst"


class TestZstCompressedSizePlusMaxByteMinusMinByte:
    def test_text_value(self):
        assert zst_compressed_size_plus_max_byte_minus_min_byte(TEXT) == 361

    def test_minimal_value(self):
        assert zst_compressed_size_plus_max_byte_minus_min_byte(MINIMAL) == 10

    def test_random_value(self):
        assert zst_compressed_size_plus_max_byte_minus_min_byte(RANDOM) == 531

    def test_returns_int(self):
        assert isinstance(zst_compressed_size_plus_max_byte_minus_min_byte(TEXT), int)

    def test_all_distinct(self):
        vals = [
            zst_compressed_size_plus_max_byte_minus_min_byte(TEXT),
            zst_compressed_size_plus_max_byte_minus_min_byte(MINIMAL),
            zst_compressed_size_plus_max_byte_minus_min_byte(RANDOM),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert zst_compressed_size_plus_max_byte_minus_min_byte(TEXT) > 0


class TestZstByteSumDivDecompressedSize:
    def test_text_value(self):
        assert zst_byte_sum_div_decompressed_size(TEXT) == 91

    def test_minimal_value(self):
        assert zst_byte_sum_div_decompressed_size(MINIMAL) == 0

    def test_random_value(self):
        assert zst_byte_sum_div_decompressed_size(RANDOM) == 127

    def test_returns_int(self):
        assert isinstance(zst_byte_sum_div_decompressed_size(TEXT), int)

    def test_all_distinct(self):
        vals = [
            zst_byte_sum_div_decompressed_size(TEXT),
            zst_byte_sum_div_decompressed_size(MINIMAL),
            zst_byte_sum_div_decompressed_size(RANDOM),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert zst_byte_sum_div_decompressed_size(TEXT) > 0
