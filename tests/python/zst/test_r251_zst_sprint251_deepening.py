"""Sprint 251 ZST analytics deepening tests.

Functions:
- zst_file_size_mod_19_times_200_plus_decompressed_size_mod_300_plus_max_byte_value_times_5
- zst_compressed_size_mod_11_times_300_plus_decompressed_size_mod_400_plus_min_byte_value_times_100
"""
import pytest
from pathlib import Path

REPO = Path(__file__).parent.parent.parent.parent
ZST = REPO / "samples/by-format/zst/valid"
TEXT = ZST / "text-compressed.zst"     # cs=272, ds=390, max_b=121, min_b=32, fs=272
MINIMAL = ZST / "minimal-synthetic.zst"  # cs=10, ds=1, max_b=0, min_b=0, fs=10
RANDOM = ZST / "random-data.zst"         # cs=276, ds=1024, max_b=255, min_b=0, fs=276

from src.python.zst import (
    zst_file_size_mod_19_times_200_plus_decompressed_size_mod_300_plus_max_byte_value_times_5 as f1,
    zst_compressed_size_mod_11_times_300_plus_decompressed_size_mod_400_plus_min_byte_value_times_100 as f2,
)


class TestZstFileSizeMod19Times200PlusDecompressedSizeMod300PlusMaxByteValueTimes5:
    def test_text_compressed(self):
        assert f1(TEXT) == 1895

    def test_minimal_synthetic(self):
        assert f1(MINIMAL) == 2001

    def test_random_data(self):
        assert f1(RANDOM) == 3399

    def test_returns_int(self):
        assert isinstance(f1(TEXT), int)

    def test_nonnegative(self):
        assert f1(MINIMAL) >= 0

    def test_distinct_text_minimal(self):
        assert f1(TEXT) != f1(MINIMAL)

    def test_distinct_minimal_random(self):
        assert f1(MINIMAL) != f1(RANDOM)

    def test_random_largest(self):
        assert f1(RANDOM) > f1(TEXT)

    def test_text_smaller_than_minimal(self):
        assert f1(TEXT) < f1(MINIMAL)

    def test_path_object(self):
        assert f1(Path(TEXT)) == 1895


class TestZstCompressedSizeMod11Times300PlusDecompressedSizeMod400PlusMinByteValueTimes100:
    def test_text_compressed(self):
        assert f2(TEXT) == 5990

    def test_minimal_synthetic(self):
        assert f2(MINIMAL) == 3001

    def test_random_data(self):
        assert f2(RANDOM) == 524

    def test_returns_int(self):
        assert isinstance(f2(TEXT), int)

    def test_nonnegative(self):
        assert f2(RANDOM) >= 0

    def test_distinct_text_minimal(self):
        assert f2(TEXT) != f2(MINIMAL)

    def test_distinct_minimal_random(self):
        assert f2(MINIMAL) != f2(RANDOM)

    def test_text_largest(self):
        assert f2(TEXT) > f2(MINIMAL)

    def test_minimal_larger_than_random(self):
        assert f2(MINIMAL) > f2(RANDOM)

    def test_path_object(self):
        assert f2(Path(TEXT)) == 5990
