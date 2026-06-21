"""Sprint 254 ZST analytics deepening tests.

Samples: text-compressed.zst (cs=272, ds=390, max_b=121, min_b=32, fs=272)
         minimal-synthetic.zst (cs=10, ds=1, max_b=0, min_b=0, fs=10)
         random-data.zst (cs=276, ds=1024, max_b=255, min_b=0, fs=276)

F1: zst_file_size_mod_13_times_300_plus_decompressed_size_mod_100_plus_max_byte_value_times_20
    TEXT=6110, MINIMAL=3001, RANDOM=6024
F2: zst_compressed_size_mod_29_times_100_plus_decompressed_size_mod_500_plus_min_byte_value_times_200
    TEXT=7890, MINIMAL=1001, RANDOM=1524
"""
from pathlib import Path

from src.python.zst import (
    zst_file_size_mod_13_times_300_plus_decompressed_size_mod_100_plus_max_byte_value_times_20,
    zst_compressed_size_mod_29_times_100_plus_decompressed_size_mod_500_plus_min_byte_value_times_200,
)

_REPO = Path(__file__).parent.parent.parent.parent
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"

TEXT = str(_ZST / "text-compressed.zst")
MINIMAL = str(_ZST / "minimal-synthetic.zst")
RANDOM = str(_ZST / "random-data.zst")


# --- F1 tests ---

class TestF1Text:
    def test_returns_int(self):
        assert isinstance(zst_file_size_mod_13_times_300_plus_decompressed_size_mod_100_plus_max_byte_value_times_20(TEXT), int)

    def test_value(self):
        assert zst_file_size_mod_13_times_300_plus_decompressed_size_mod_100_plus_max_byte_value_times_20(TEXT) == 6110

    def test_nonnegative(self):
        assert zst_file_size_mod_13_times_300_plus_decompressed_size_mod_100_plus_max_byte_value_times_20(TEXT) >= 0


class TestF1Minimal:
    def test_returns_int(self):
        assert isinstance(zst_file_size_mod_13_times_300_plus_decompressed_size_mod_100_plus_max_byte_value_times_20(MINIMAL), int)

    def test_value(self):
        assert zst_file_size_mod_13_times_300_plus_decompressed_size_mod_100_plus_max_byte_value_times_20(MINIMAL) == 3001

    def test_nonnegative(self):
        assert zst_file_size_mod_13_times_300_plus_decompressed_size_mod_100_plus_max_byte_value_times_20(MINIMAL) >= 0


class TestF1Random:
    def test_returns_int(self):
        assert isinstance(zst_file_size_mod_13_times_300_plus_decompressed_size_mod_100_plus_max_byte_value_times_20(RANDOM), int)

    def test_value(self):
        assert zst_file_size_mod_13_times_300_plus_decompressed_size_mod_100_plus_max_byte_value_times_20(RANDOM) == 6024

    def test_nonnegative(self):
        assert zst_file_size_mod_13_times_300_plus_decompressed_size_mod_100_plus_max_byte_value_times_20(RANDOM) >= 0

    def test_random_greater_than_minimal(self):
        assert (zst_file_size_mod_13_times_300_plus_decompressed_size_mod_100_plus_max_byte_value_times_20(RANDOM) >
                zst_file_size_mod_13_times_300_plus_decompressed_size_mod_100_plus_max_byte_value_times_20(MINIMAL))


# --- F2 tests ---

class TestF2Text:
    def test_returns_int(self):
        assert isinstance(zst_compressed_size_mod_29_times_100_plus_decompressed_size_mod_500_plus_min_byte_value_times_200(TEXT), int)

    def test_value(self):
        assert zst_compressed_size_mod_29_times_100_plus_decompressed_size_mod_500_plus_min_byte_value_times_200(TEXT) == 7890

    def test_nonnegative(self):
        assert zst_compressed_size_mod_29_times_100_plus_decompressed_size_mod_500_plus_min_byte_value_times_200(TEXT) >= 0

    def test_text_greater_than_random(self):
        assert (zst_compressed_size_mod_29_times_100_plus_decompressed_size_mod_500_plus_min_byte_value_times_200(TEXT) >
                zst_compressed_size_mod_29_times_100_plus_decompressed_size_mod_500_plus_min_byte_value_times_200(RANDOM))


class TestF2Minimal:
    def test_returns_int(self):
        assert isinstance(zst_compressed_size_mod_29_times_100_plus_decompressed_size_mod_500_plus_min_byte_value_times_200(MINIMAL), int)

    def test_value(self):
        assert zst_compressed_size_mod_29_times_100_plus_decompressed_size_mod_500_plus_min_byte_value_times_200(MINIMAL) == 1001

    def test_nonnegative(self):
        assert zst_compressed_size_mod_29_times_100_plus_decompressed_size_mod_500_plus_min_byte_value_times_200(MINIMAL) >= 0


class TestF2Random:
    def test_returns_int(self):
        assert isinstance(zst_compressed_size_mod_29_times_100_plus_decompressed_size_mod_500_plus_min_byte_value_times_200(RANDOM), int)

    def test_value(self):
        assert zst_compressed_size_mod_29_times_100_plus_decompressed_size_mod_500_plus_min_byte_value_times_200(RANDOM) == 1524

    def test_nonnegative(self):
        assert zst_compressed_size_mod_29_times_100_plus_decompressed_size_mod_500_plus_min_byte_value_times_200(RANDOM) >= 0
