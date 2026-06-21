"""Sprint 266 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINIMAL = _ZST / "minimal-synthetic.zst"
RANDOM = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_47_times_150_plus_decompressed_size_mod_400_plus_max_byte_value_times_20,
    zst_compressed_size_mod_53_times_100_plus_decompressed_size_mod_200_plus_min_byte_value_times_200,
)


# --- F1: zst_file_size_mod_47_times_150_plus_decompressed_size_mod_400_plus_max_byte_value_times_20 ---

class TestZstFileSizeMod47Times150PlusDecompressedMod400PlusMaxByte20:
    def test_text_returns_8360(self):
        assert zst_file_size_mod_47_times_150_plus_decompressed_size_mod_400_plus_max_byte_value_times_20(TEXT) == 8360

    def test_minimal_returns_1501(self):
        assert zst_file_size_mod_47_times_150_plus_decompressed_size_mod_400_plus_max_byte_value_times_20(MINIMAL) == 1501

    def test_random_returns_11474(self):
        assert zst_file_size_mod_47_times_150_plus_decompressed_size_mod_400_plus_max_byte_value_times_20(RANDOM) == 11474

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_47_times_150_plus_decompressed_size_mod_400_plus_max_byte_value_times_20(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_file_size_mod_47_times_150_plus_decompressed_size_mod_400_plus_max_byte_value_times_20(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_file_size_mod_47_times_150_plus_decompressed_size_mod_400_plus_max_byte_value_times_20(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_47_times_150_plus_decompressed_size_mod_400_plus_max_byte_value_times_20(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_file_size_mod_47_times_150_plus_decompressed_size_mod_400_plus_max_byte_value_times_20(MINIMAL) >= 0

    def test_random_greater_than_text(self):
        assert (zst_file_size_mod_47_times_150_plus_decompressed_size_mod_400_plus_max_byte_value_times_20(RANDOM) >
                zst_file_size_mod_47_times_150_plus_decompressed_size_mod_400_plus_max_byte_value_times_20(TEXT))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_47_times_150_plus_decompressed_size_mod_400_plus_max_byte_value_times_20(str(TEXT)) == 8360


# --- F2: zst_compressed_size_mod_53_times_100_plus_decompressed_size_mod_200_plus_min_byte_value_times_200 ---

class TestZstCompressedSizeMod53Times100PlusDecompressedMod200PlusMinByte200:
    def test_text_returns_7290(self):
        assert zst_compressed_size_mod_53_times_100_plus_decompressed_size_mod_200_plus_min_byte_value_times_200(TEXT) == 7290

    def test_minimal_returns_1001(self):
        assert zst_compressed_size_mod_53_times_100_plus_decompressed_size_mod_200_plus_min_byte_value_times_200(MINIMAL) == 1001

    def test_random_returns_1124(self):
        assert zst_compressed_size_mod_53_times_100_plus_decompressed_size_mod_200_plus_min_byte_value_times_200(RANDOM) == 1124

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_53_times_100_plus_decompressed_size_mod_200_plus_min_byte_value_times_200(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_compressed_size_mod_53_times_100_plus_decompressed_size_mod_200_plus_min_byte_value_times_200(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_compressed_size_mod_53_times_100_plus_decompressed_size_mod_200_plus_min_byte_value_times_200(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_53_times_100_plus_decompressed_size_mod_200_plus_min_byte_value_times_200(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_compressed_size_mod_53_times_100_plus_decompressed_size_mod_200_plus_min_byte_value_times_200(MINIMAL) >= 0

    def test_text_greater_than_minimal(self):
        assert (zst_compressed_size_mod_53_times_100_plus_decompressed_size_mod_200_plus_min_byte_value_times_200(TEXT) >
                zst_compressed_size_mod_53_times_100_plus_decompressed_size_mod_200_plus_min_byte_value_times_200(MINIMAL))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_53_times_100_plus_decompressed_size_mod_200_plus_min_byte_value_times_200(str(TEXT)) == 7290
