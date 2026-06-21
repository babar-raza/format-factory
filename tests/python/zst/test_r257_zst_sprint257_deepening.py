"""Sprint 257 ZST analytics deepening tests.

F1: zst_file_size_mod_23_times_200_plus_decompressed_size_mod_300_plus_max_byte_value_times_15
    TEXT=5705, MINIMAL=2001, RANDOM=3949
F2: zst_compressed_size_mod_31_times_150_plus_decompressed_size_mod_200_plus_min_byte_value_times_50
    TEXT=5390, MINIMAL=1501, RANDOM=4224
"""
from pathlib import Path

from src.python.zst import (
    zst_file_size_mod_23_times_200_plus_decompressed_size_mod_300_plus_max_byte_value_times_15,
    zst_compressed_size_mod_31_times_150_plus_decompressed_size_mod_200_plus_min_byte_value_times_50,
)

_REPO = Path(__file__).parent.parent.parent.parent
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"

TEXT = str(_ZST / "text-compressed.zst")
MINIMAL = str(_ZST / "minimal-synthetic.zst")
RANDOM = str(_ZST / "random-data.zst")


# --- F1 tests ---

class TestF1Text:
    def test_returns_int(self):
        assert isinstance(zst_file_size_mod_23_times_200_plus_decompressed_size_mod_300_plus_max_byte_value_times_15(TEXT), int)

    def test_value(self):
        assert zst_file_size_mod_23_times_200_plus_decompressed_size_mod_300_plus_max_byte_value_times_15(TEXT) == 5705

    def test_nonnegative(self):
        assert zst_file_size_mod_23_times_200_plus_decompressed_size_mod_300_plus_max_byte_value_times_15(TEXT) >= 0

    def test_text_greater_than_random(self):
        assert (zst_file_size_mod_23_times_200_plus_decompressed_size_mod_300_plus_max_byte_value_times_15(TEXT) >
                zst_file_size_mod_23_times_200_plus_decompressed_size_mod_300_plus_max_byte_value_times_15(RANDOM))


class TestF1Minimal:
    def test_returns_int(self):
        assert isinstance(zst_file_size_mod_23_times_200_plus_decompressed_size_mod_300_plus_max_byte_value_times_15(MINIMAL), int)

    def test_value(self):
        assert zst_file_size_mod_23_times_200_plus_decompressed_size_mod_300_plus_max_byte_value_times_15(MINIMAL) == 2001

    def test_nonnegative(self):
        assert zst_file_size_mod_23_times_200_plus_decompressed_size_mod_300_plus_max_byte_value_times_15(MINIMAL) >= 0


class TestF1Random:
    def test_returns_int(self):
        assert isinstance(zst_file_size_mod_23_times_200_plus_decompressed_size_mod_300_plus_max_byte_value_times_15(RANDOM), int)

    def test_value(self):
        assert zst_file_size_mod_23_times_200_plus_decompressed_size_mod_300_plus_max_byte_value_times_15(RANDOM) == 3949

    def test_nonnegative(self):
        assert zst_file_size_mod_23_times_200_plus_decompressed_size_mod_300_plus_max_byte_value_times_15(RANDOM) >= 0


# --- F2 tests ---

class TestF2Text:
    def test_returns_int(self):
        assert isinstance(zst_compressed_size_mod_31_times_150_plus_decompressed_size_mod_200_plus_min_byte_value_times_50(TEXT), int)

    def test_value(self):
        assert zst_compressed_size_mod_31_times_150_plus_decompressed_size_mod_200_plus_min_byte_value_times_50(TEXT) == 5390

    def test_nonnegative(self):
        assert zst_compressed_size_mod_31_times_150_plus_decompressed_size_mod_200_plus_min_byte_value_times_50(TEXT) >= 0

    def test_text_greater_than_minimal(self):
        assert (zst_compressed_size_mod_31_times_150_plus_decompressed_size_mod_200_plus_min_byte_value_times_50(TEXT) >
                zst_compressed_size_mod_31_times_150_plus_decompressed_size_mod_200_plus_min_byte_value_times_50(MINIMAL))


class TestF2Minimal:
    def test_returns_int(self):
        assert isinstance(zst_compressed_size_mod_31_times_150_plus_decompressed_size_mod_200_plus_min_byte_value_times_50(MINIMAL), int)

    def test_value(self):
        assert zst_compressed_size_mod_31_times_150_plus_decompressed_size_mod_200_plus_min_byte_value_times_50(MINIMAL) == 1501

    def test_nonnegative(self):
        assert zst_compressed_size_mod_31_times_150_plus_decompressed_size_mod_200_plus_min_byte_value_times_50(MINIMAL) >= 0


class TestF2Random:
    def test_returns_int(self):
        assert isinstance(zst_compressed_size_mod_31_times_150_plus_decompressed_size_mod_200_plus_min_byte_value_times_50(RANDOM), int)

    def test_value(self):
        assert zst_compressed_size_mod_31_times_150_plus_decompressed_size_mod_200_plus_min_byte_value_times_50(RANDOM) == 4224

    def test_nonnegative(self):
        assert zst_compressed_size_mod_31_times_150_plus_decompressed_size_mod_200_plus_min_byte_value_times_50(RANDOM) >= 0
