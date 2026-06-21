"""Sprint 221 ZST deepening — 2 new analytics functions, 12 tests.

Functions:
  zst_compressed_size_times_max_byte_plus_1_plus_min_byte_times_10
  zst_decompressed_size_times_compressed_size_mod_10000_plus_max_byte

Samples (samples/by-format/zst/valid/):
  text-compressed.zst   cs=272, ds=390, bs=35803, mx=121, mn=32
  minimal-synthetic.zst cs=10,  ds=1,   bs=0,     mx=0,   mn=0
  random-data.zst       cs=276, ds=1024, bs=130560, mx=255, mn=0

Expected:
  zst_compressed_size_times_max_byte_plus_1_plus_min_byte_times_10:
    text    = 272*(121+1) + 32*10  = 33184 + 320 = 33504
    minimal = 10*(0+1) + 0*10      = 10
    random  = 276*(255+1) + 0*10   = 70656

  zst_decompressed_size_times_compressed_size_mod_10000_plus_max_byte:
    text    = (390*272) % 10000 + 121  = 6080 + 121 = 6201
    minimal = (1*10) % 10000 + 0       = 10
    random  = (1024*276) % 10000 + 255 = 2624 + 255 = 2879
"""
from pathlib import Path

import pytest

from src.python.zst import (
    zst_compressed_size_times_max_byte_plus_1_plus_min_byte_times_10,
    zst_decompressed_size_times_compressed_size_mod_10000_plus_max_byte,
)

_VALID = Path("samples/by-format/zst/valid")
TEXT = _VALID / "text-compressed.zst"
MINIMAL = _VALID / "minimal-synthetic.zst"
RANDOM = _VALID / "random-data.zst"


class TestZstCompressedSizeTimesMaxBytePlus1PlusMinByteTimesTen:
    def test_text_value(self):
        assert zst_compressed_size_times_max_byte_plus_1_plus_min_byte_times_10(TEXT) == 33504

    def test_minimal_value(self):
        assert zst_compressed_size_times_max_byte_plus_1_plus_min_byte_times_10(MINIMAL) == 10

    def test_random_value(self):
        assert zst_compressed_size_times_max_byte_plus_1_plus_min_byte_times_10(RANDOM) == 70656

    def test_returns_int(self):
        assert isinstance(zst_compressed_size_times_max_byte_plus_1_plus_min_byte_times_10(TEXT), int)

    def test_all_distinct(self):
        vals = [
            zst_compressed_size_times_max_byte_plus_1_plus_min_byte_times_10(TEXT),
            zst_compressed_size_times_max_byte_plus_1_plus_min_byte_times_10(MINIMAL),
            zst_compressed_size_times_max_byte_plus_1_plus_min_byte_times_10(RANDOM),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert zst_compressed_size_times_max_byte_plus_1_plus_min_byte_times_10(TEXT) > 0


class TestZstDecompressedSizeTimesCompressedSizeMod10000PlusMaxByte:
    def test_text_value(self):
        assert zst_decompressed_size_times_compressed_size_mod_10000_plus_max_byte(TEXT) == 6201

    def test_minimal_value(self):
        assert zst_decompressed_size_times_compressed_size_mod_10000_plus_max_byte(MINIMAL) == 10

    def test_random_value(self):
        assert zst_decompressed_size_times_compressed_size_mod_10000_plus_max_byte(RANDOM) == 2879

    def test_returns_int(self):
        assert isinstance(zst_decompressed_size_times_compressed_size_mod_10000_plus_max_byte(TEXT), int)

    def test_all_distinct(self):
        vals = [
            zst_decompressed_size_times_compressed_size_mod_10000_plus_max_byte(TEXT),
            zst_decompressed_size_times_compressed_size_mod_10000_plus_max_byte(MINIMAL),
            zst_decompressed_size_times_compressed_size_mod_10000_plus_max_byte(RANDOM),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert zst_decompressed_size_times_compressed_size_mod_10000_plus_max_byte(TEXT) > 0
