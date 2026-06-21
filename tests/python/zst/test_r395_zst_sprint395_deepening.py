"""Sprint 395 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINI = _ZST / "minimal-synthetic.zst"
RAND = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_587_times_2125_plus_decompressed_size_mod_8600_plus_max_byte_value_times_460,
    zst_compressed_size_mod_593_times_2075_plus_decompressed_size_mod_8700_plus_min_byte_value_times_3100,
)


# --- F1: zst_file_size_mod_587_times_2125_plus_decompressed_size_mod_8600_plus_max_byte_value_times_460 ---

class TestZstFileSizeMod587Times2125PlusDecompressed8600PlusMaxByte460:
    def test_text_returns_634050(self):
        assert zst_file_size_mod_587_times_2125_plus_decompressed_size_mod_8600_plus_max_byte_value_times_460(TEXT) == 634050

    def test_mini_returns_21251(self):
        assert zst_file_size_mod_587_times_2125_plus_decompressed_size_mod_8600_plus_max_byte_value_times_460(MINI) == 21251

    def test_rand_returns_704824(self):
        assert zst_file_size_mod_587_times_2125_plus_decompressed_size_mod_8600_plus_max_byte_value_times_460(RAND) == 704824

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_587_times_2125_plus_decompressed_size_mod_8600_plus_max_byte_value_times_460(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_file_size_mod_587_times_2125_plus_decompressed_size_mod_8600_plus_max_byte_value_times_460(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_file_size_mod_587_times_2125_plus_decompressed_size_mod_8600_plus_max_byte_value_times_460(RAND), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_587_times_2125_plus_decompressed_size_mod_8600_plus_max_byte_value_times_460(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_file_size_mod_587_times_2125_plus_decompressed_size_mod_8600_plus_max_byte_value_times_460(MINI) >= 0

    def test_rand_greater_than_mini(self):
        assert (zst_file_size_mod_587_times_2125_plus_decompressed_size_mod_8600_plus_max_byte_value_times_460(RAND) >
                zst_file_size_mod_587_times_2125_plus_decompressed_size_mod_8600_plus_max_byte_value_times_460(MINI))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_587_times_2125_plus_decompressed_size_mod_8600_plus_max_byte_value_times_460(str(TEXT)) == 634050


# --- F2: zst_compressed_size_mod_593_times_2075_plus_decompressed_size_mod_8700_plus_min_byte_value_times_3100 ---

class TestZstCompressedSizeMod593Times2075PlusDecompressed8700PlusMinByte3100:
    def test_text_returns_663990(self):
        assert zst_compressed_size_mod_593_times_2075_plus_decompressed_size_mod_8700_plus_min_byte_value_times_3100(TEXT) == 663990

    def test_mini_returns_20751(self):
        assert zst_compressed_size_mod_593_times_2075_plus_decompressed_size_mod_8700_plus_min_byte_value_times_3100(MINI) == 20751

    def test_rand_returns_573724(self):
        assert zst_compressed_size_mod_593_times_2075_plus_decompressed_size_mod_8700_plus_min_byte_value_times_3100(RAND) == 573724

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_593_times_2075_plus_decompressed_size_mod_8700_plus_min_byte_value_times_3100(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_compressed_size_mod_593_times_2075_plus_decompressed_size_mod_8700_plus_min_byte_value_times_3100(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_compressed_size_mod_593_times_2075_plus_decompressed_size_mod_8700_plus_min_byte_value_times_3100(RAND), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_593_times_2075_plus_decompressed_size_mod_8700_plus_min_byte_value_times_3100(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_compressed_size_mod_593_times_2075_plus_decompressed_size_mod_8700_plus_min_byte_value_times_3100(MINI) >= 0

    def test_text_greater_than_mini(self):
        assert (zst_compressed_size_mod_593_times_2075_plus_decompressed_size_mod_8700_plus_min_byte_value_times_3100(TEXT) >
                zst_compressed_size_mod_593_times_2075_plus_decompressed_size_mod_8700_plus_min_byte_value_times_3100(MINI))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_593_times_2075_plus_decompressed_size_mod_8700_plus_min_byte_value_times_3100(str(TEXT)) == 663990
