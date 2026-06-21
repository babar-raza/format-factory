"""Sprint 398 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINI = _ZST / "minimal-synthetic.zst"
RAND = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_599_times_2150_plus_decompressed_size_mod_8800_plus_max_byte_value_times_470,
    zst_compressed_size_mod_601_times_2100_plus_decompressed_size_mod_8900_plus_min_byte_value_times_3150,
)


# --- F1: zst_file_size_mod_599_times_2150_plus_decompressed_size_mod_8800_plus_max_byte_value_times_470 ---

class TestZstFileSizeMod599Times2150PlusDecompressed8800PlusMaxByte470:
    def test_text_returns_642060(self):
        assert zst_file_size_mod_599_times_2150_plus_decompressed_size_mod_8800_plus_max_byte_value_times_470(TEXT) == 642060

    def test_mini_returns_21501(self):
        assert zst_file_size_mod_599_times_2150_plus_decompressed_size_mod_8800_plus_max_byte_value_times_470(MINI) == 21501

    def test_rand_returns_714274(self):
        assert zst_file_size_mod_599_times_2150_plus_decompressed_size_mod_8800_plus_max_byte_value_times_470(RAND) == 714274

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_599_times_2150_plus_decompressed_size_mod_8800_plus_max_byte_value_times_470(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_file_size_mod_599_times_2150_plus_decompressed_size_mod_8800_plus_max_byte_value_times_470(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_file_size_mod_599_times_2150_plus_decompressed_size_mod_8800_plus_max_byte_value_times_470(RAND), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_599_times_2150_plus_decompressed_size_mod_8800_plus_max_byte_value_times_470(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_file_size_mod_599_times_2150_plus_decompressed_size_mod_8800_plus_max_byte_value_times_470(MINI) >= 0

    def test_rand_greater_than_mini(self):
        assert (zst_file_size_mod_599_times_2150_plus_decompressed_size_mod_8800_plus_max_byte_value_times_470(RAND) >
                zst_file_size_mod_599_times_2150_plus_decompressed_size_mod_8800_plus_max_byte_value_times_470(MINI))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_599_times_2150_plus_decompressed_size_mod_8800_plus_max_byte_value_times_470(str(TEXT)) == 642060


# --- F2: zst_compressed_size_mod_601_times_2100_plus_decompressed_size_mod_8900_plus_min_byte_value_times_3150 ---

class TestZstCompressedSizeMod601Times2100PlusDecompressed8900PlusMinByte3150:
    def test_text_returns_672390(self):
        assert zst_compressed_size_mod_601_times_2100_plus_decompressed_size_mod_8900_plus_min_byte_value_times_3150(TEXT) == 672390

    def test_mini_returns_21001(self):
        assert zst_compressed_size_mod_601_times_2100_plus_decompressed_size_mod_8900_plus_min_byte_value_times_3150(MINI) == 21001

    def test_rand_returns_580624(self):
        assert zst_compressed_size_mod_601_times_2100_plus_decompressed_size_mod_8900_plus_min_byte_value_times_3150(RAND) == 580624

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_601_times_2100_plus_decompressed_size_mod_8900_plus_min_byte_value_times_3150(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_compressed_size_mod_601_times_2100_plus_decompressed_size_mod_8900_plus_min_byte_value_times_3150(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_compressed_size_mod_601_times_2100_plus_decompressed_size_mod_8900_plus_min_byte_value_times_3150(RAND), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_601_times_2100_plus_decompressed_size_mod_8900_plus_min_byte_value_times_3150(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_compressed_size_mod_601_times_2100_plus_decompressed_size_mod_8900_plus_min_byte_value_times_3150(MINI) >= 0

    def test_text_greater_than_mini(self):
        assert (zst_compressed_size_mod_601_times_2100_plus_decompressed_size_mod_8900_plus_min_byte_value_times_3150(TEXT) >
                zst_compressed_size_mod_601_times_2100_plus_decompressed_size_mod_8900_plus_min_byte_value_times_3150(MINI))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_601_times_2100_plus_decompressed_size_mod_8900_plus_min_byte_value_times_3150(str(TEXT)) == 672390
