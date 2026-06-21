"""Sprint 272 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINIMAL = _ZST / "minimal-synthetic.zst"
RANDOM = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_67_times_300_plus_decompressed_size_mod_400_plus_max_byte_value_times_50,
    zst_compressed_size_mod_71_times_200_plus_decompressed_size_mod_600_plus_min_byte_value_times_400,
)


# --- F1: zst_file_size_mod_67_times_300_plus_decompressed_size_mod_400_plus_max_byte_value_times_50 ---

class TestZstFileSizeMod67Times300PlusDecompressedMod400PlusMaxByte50:
    def test_text_returns_7640(self):
        assert zst_file_size_mod_67_times_300_plus_decompressed_size_mod_400_plus_max_byte_value_times_50(TEXT) == 7640

    def test_minimal_returns_3001(self):
        assert zst_file_size_mod_67_times_300_plus_decompressed_size_mod_400_plus_max_byte_value_times_50(MINIMAL) == 3001

    def test_random_returns_15374(self):
        assert zst_file_size_mod_67_times_300_plus_decompressed_size_mod_400_plus_max_byte_value_times_50(RANDOM) == 15374

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_67_times_300_plus_decompressed_size_mod_400_plus_max_byte_value_times_50(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_file_size_mod_67_times_300_plus_decompressed_size_mod_400_plus_max_byte_value_times_50(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_file_size_mod_67_times_300_plus_decompressed_size_mod_400_plus_max_byte_value_times_50(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_67_times_300_plus_decompressed_size_mod_400_plus_max_byte_value_times_50(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_file_size_mod_67_times_300_plus_decompressed_size_mod_400_plus_max_byte_value_times_50(MINIMAL) >= 0

    def test_random_greater_than_text(self):
        assert (zst_file_size_mod_67_times_300_plus_decompressed_size_mod_400_plus_max_byte_value_times_50(RANDOM) >
                zst_file_size_mod_67_times_300_plus_decompressed_size_mod_400_plus_max_byte_value_times_50(TEXT))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_67_times_300_plus_decompressed_size_mod_400_plus_max_byte_value_times_50(str(TEXT)) == 7640


# --- F2: zst_compressed_size_mod_71_times_200_plus_decompressed_size_mod_600_plus_min_byte_value_times_400 ---

class TestZstCompressedSizeMod71Times200PlusDecompressedMod600PlusMinByte400:
    def test_text_returns_24990(self):
        assert zst_compressed_size_mod_71_times_200_plus_decompressed_size_mod_600_plus_min_byte_value_times_400(TEXT) == 24990

    def test_minimal_returns_2001(self):
        assert zst_compressed_size_mod_71_times_200_plus_decompressed_size_mod_600_plus_min_byte_value_times_400(MINIMAL) == 2001

    def test_random_returns_13024(self):
        assert zst_compressed_size_mod_71_times_200_plus_decompressed_size_mod_600_plus_min_byte_value_times_400(RANDOM) == 13024

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_71_times_200_plus_decompressed_size_mod_600_plus_min_byte_value_times_400(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_compressed_size_mod_71_times_200_plus_decompressed_size_mod_600_plus_min_byte_value_times_400(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_compressed_size_mod_71_times_200_plus_decompressed_size_mod_600_plus_min_byte_value_times_400(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_71_times_200_plus_decompressed_size_mod_600_plus_min_byte_value_times_400(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_compressed_size_mod_71_times_200_plus_decompressed_size_mod_600_plus_min_byte_value_times_400(MINIMAL) >= 0

    def test_text_greater_than_random(self):
        assert (zst_compressed_size_mod_71_times_200_plus_decompressed_size_mod_600_plus_min_byte_value_times_400(TEXT) >
                zst_compressed_size_mod_71_times_200_plus_decompressed_size_mod_600_plus_min_byte_value_times_400(RANDOM))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_71_times_200_plus_decompressed_size_mod_600_plus_min_byte_value_times_400(str(TEXT)) == 24990
