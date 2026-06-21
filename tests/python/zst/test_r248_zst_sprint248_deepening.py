"""Sprint 248 ZST analytics deepening tests.

Functions:
- zst_file_size_mod_17_times_100_plus_decompressed_size_mod_500_plus_max_byte_value_times_10
- zst_compressed_size_times_3_mod_1000_plus_decompressed_size_mod_200_plus_min_byte_value_times_50
"""
import pytest
from pathlib import Path

REPO = Path(__file__).parent.parent.parent.parent
ZST = REPO / "samples/by-format/zst/valid"
TEXT = ZST / "text-compressed.zst"     # cs=272, ds=390, max_b=121, min_b=32, fs=272
MINIMAL = ZST / "minimal-synthetic.zst"  # cs=10, ds=1, max_b=0, min_b=0, fs=10
RANDOM = ZST / "random-data.zst"         # cs=276, ds=1024, max_b=255, min_b=0, fs=276

from src.python.zst import (
    zst_file_size_mod_17_times_100_plus_decompressed_size_mod_500_plus_max_byte_value_times_10 as f1,
    zst_compressed_size_times_3_mod_1000_plus_decompressed_size_mod_200_plus_min_byte_value_times_50 as f2,
)


class TestZstFileSizeMod17Times100PlusDecompressedSizeMod500PlusMaxByteValueTimes10:
    def test_text_compressed(self):
        assert f1(TEXT) == 1600

    def test_minimal_synthetic(self):
        assert f1(MINIMAL) == 1001

    def test_random_data(self):
        assert f1(RANDOM) == 2974

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

    def test_text_larger_than_minimal(self):
        assert f1(TEXT) > f1(MINIMAL)

    def test_path_object(self):
        assert f1(Path(TEXT)) == 1600


class TestZstCompressedSizeTimes3Mod1000PlusDecompressedSizeMod200PlusMinByteValueTimes50:
    def test_text_compressed(self):
        assert f2(TEXT) == 2606

    def test_minimal_synthetic(self):
        assert f2(MINIMAL) == 31

    def test_random_data(self):
        assert f2(RANDOM) == 852

    def test_returns_int(self):
        assert isinstance(f2(TEXT), int)

    def test_nonnegative(self):
        assert f2(MINIMAL) >= 0

    def test_distinct_text_minimal(self):
        assert f2(TEXT) != f2(MINIMAL)

    def test_distinct_minimal_random(self):
        assert f2(MINIMAL) != f2(RANDOM)

    def test_text_largest(self):
        assert f2(TEXT) > f2(RANDOM)

    def test_random_larger_than_minimal(self):
        assert f2(RANDOM) > f2(MINIMAL)

    def test_path_object(self):
        assert f2(Path(TEXT)) == 2606
