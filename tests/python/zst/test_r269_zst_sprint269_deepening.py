"""Sprint 269 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINIMAL = _ZST / "minimal-synthetic.zst"
RANDOM = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_59_times_200_plus_decompressed_size_mod_300_plus_max_byte_value_times_40,
    zst_compressed_size_mod_61_times_150_plus_decompressed_size_mod_500_plus_min_byte_value_times_300,
)


# --- F1: zst_file_size_mod_59_times_200_plus_decompressed_size_mod_300_plus_max_byte_value_times_40 ---

class TestZstFileSizeMod59Times200PlusDecompressedMod300PlusMaxByte40:
    def test_text_returns_12130(self):
        assert zst_file_size_mod_59_times_200_plus_decompressed_size_mod_300_plus_max_byte_value_times_40(TEXT) == 12130

    def test_minimal_returns_2001(self):
        assert zst_file_size_mod_59_times_200_plus_decompressed_size_mod_300_plus_max_byte_value_times_40(MINIMAL) == 2001

    def test_random_returns_18324(self):
        assert zst_file_size_mod_59_times_200_plus_decompressed_size_mod_300_plus_max_byte_value_times_40(RANDOM) == 18324

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_59_times_200_plus_decompressed_size_mod_300_plus_max_byte_value_times_40(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_file_size_mod_59_times_200_plus_decompressed_size_mod_300_plus_max_byte_value_times_40(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_file_size_mod_59_times_200_plus_decompressed_size_mod_300_plus_max_byte_value_times_40(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_59_times_200_plus_decompressed_size_mod_300_plus_max_byte_value_times_40(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_file_size_mod_59_times_200_plus_decompressed_size_mod_300_plus_max_byte_value_times_40(MINIMAL) >= 0

    def test_random_greater_than_text(self):
        assert (zst_file_size_mod_59_times_200_plus_decompressed_size_mod_300_plus_max_byte_value_times_40(RANDOM) >
                zst_file_size_mod_59_times_200_plus_decompressed_size_mod_300_plus_max_byte_value_times_40(TEXT))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_59_times_200_plus_decompressed_size_mod_300_plus_max_byte_value_times_40(str(TEXT)) == 12130


# --- F2: zst_compressed_size_mod_61_times_150_plus_decompressed_size_mod_500_plus_min_byte_value_times_300 ---

class TestZstCompressedSizeMod61Times150PlusDecompressedMod500PlusMinByte300:
    def test_text_returns_14190(self):
        assert zst_compressed_size_mod_61_times_150_plus_decompressed_size_mod_500_plus_min_byte_value_times_300(TEXT) == 14190

    def test_minimal_returns_1501(self):
        assert zst_compressed_size_mod_61_times_150_plus_decompressed_size_mod_500_plus_min_byte_value_times_300(MINIMAL) == 1501

    def test_random_returns_4824(self):
        assert zst_compressed_size_mod_61_times_150_plus_decompressed_size_mod_500_plus_min_byte_value_times_300(RANDOM) == 4824

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_61_times_150_plus_decompressed_size_mod_500_plus_min_byte_value_times_300(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_compressed_size_mod_61_times_150_plus_decompressed_size_mod_500_plus_min_byte_value_times_300(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_compressed_size_mod_61_times_150_plus_decompressed_size_mod_500_plus_min_byte_value_times_300(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_61_times_150_plus_decompressed_size_mod_500_plus_min_byte_value_times_300(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_compressed_size_mod_61_times_150_plus_decompressed_size_mod_500_plus_min_byte_value_times_300(MINIMAL) >= 0

    def test_text_greater_than_random(self):
        assert (zst_compressed_size_mod_61_times_150_plus_decompressed_size_mod_500_plus_min_byte_value_times_300(TEXT) >
                zst_compressed_size_mod_61_times_150_plus_decompressed_size_mod_500_plus_min_byte_value_times_300(RANDOM))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_61_times_150_plus_decompressed_size_mod_500_plus_min_byte_value_times_300(str(TEXT)) == 14190
