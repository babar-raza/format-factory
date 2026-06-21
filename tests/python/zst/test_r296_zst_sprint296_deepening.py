"""Sprint 296 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINIMAL = _ZST / "minimal-synthetic.zst"
RANDOM = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_149_times_650_plus_decompressed_size_mod_2100_plus_max_byte_value_times_130,
    zst_compressed_size_mod_151_times_600_plus_decompressed_size_mod_2200_plus_min_byte_value_times_1200,
)


# --- F1: zst_file_size_mod_149_times_650_plus_decompressed_size_mod_2100_plus_max_byte_value_times_130 ---

class TestZstFileSizeMod149Times650PlusDecompressedMod2100PlusMaxByte130:
    def test_text_returns_96070(self):
        assert zst_file_size_mod_149_times_650_plus_decompressed_size_mod_2100_plus_max_byte_value_times_130(TEXT) == 96070

    def test_minimal_returns_6501(self):
        assert zst_file_size_mod_149_times_650_plus_decompressed_size_mod_2100_plus_max_byte_value_times_130(MINIMAL) == 6501

    def test_random_returns_116724(self):
        assert zst_file_size_mod_149_times_650_plus_decompressed_size_mod_2100_plus_max_byte_value_times_130(RANDOM) == 116724

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_149_times_650_plus_decompressed_size_mod_2100_plus_max_byte_value_times_130(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_file_size_mod_149_times_650_plus_decompressed_size_mod_2100_plus_max_byte_value_times_130(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_file_size_mod_149_times_650_plus_decompressed_size_mod_2100_plus_max_byte_value_times_130(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_149_times_650_plus_decompressed_size_mod_2100_plus_max_byte_value_times_130(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_file_size_mod_149_times_650_plus_decompressed_size_mod_2100_plus_max_byte_value_times_130(MINIMAL) >= 0

    def test_random_greater_than_text(self):
        assert (zst_file_size_mod_149_times_650_plus_decompressed_size_mod_2100_plus_max_byte_value_times_130(RANDOM) >
                zst_file_size_mod_149_times_650_plus_decompressed_size_mod_2100_plus_max_byte_value_times_130(TEXT))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_149_times_650_plus_decompressed_size_mod_2100_plus_max_byte_value_times_130(str(TEXT)) == 96070


# --- F2: zst_compressed_size_mod_151_times_600_plus_decompressed_size_mod_2200_plus_min_byte_value_times_1200 ---

class TestZstCompressedSizeMod151Times600PlusDecompressedMod2200PlusMinByte1200:
    def test_text_returns_111390(self):
        assert zst_compressed_size_mod_151_times_600_plus_decompressed_size_mod_2200_plus_min_byte_value_times_1200(TEXT) == 111390

    def test_minimal_returns_6001(self):
        assert zst_compressed_size_mod_151_times_600_plus_decompressed_size_mod_2200_plus_min_byte_value_times_1200(MINIMAL) == 6001

    def test_random_returns_76024(self):
        assert zst_compressed_size_mod_151_times_600_plus_decompressed_size_mod_2200_plus_min_byte_value_times_1200(RANDOM) == 76024

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_151_times_600_plus_decompressed_size_mod_2200_plus_min_byte_value_times_1200(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_compressed_size_mod_151_times_600_plus_decompressed_size_mod_2200_plus_min_byte_value_times_1200(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_compressed_size_mod_151_times_600_plus_decompressed_size_mod_2200_plus_min_byte_value_times_1200(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_151_times_600_plus_decompressed_size_mod_2200_plus_min_byte_value_times_1200(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_compressed_size_mod_151_times_600_plus_decompressed_size_mod_2200_plus_min_byte_value_times_1200(MINIMAL) >= 0

    def test_text_greater_than_random(self):
        assert (zst_compressed_size_mod_151_times_600_plus_decompressed_size_mod_2200_plus_min_byte_value_times_1200(TEXT) >
                zst_compressed_size_mod_151_times_600_plus_decompressed_size_mod_2200_plus_min_byte_value_times_1200(RANDOM))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_151_times_600_plus_decompressed_size_mod_2200_plus_min_byte_value_times_1200(str(TEXT)) == 111390
