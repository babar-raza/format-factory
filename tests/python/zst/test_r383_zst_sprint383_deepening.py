"""Sprint 383 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINI = _ZST / "minimal-synthetic.zst"
RAND = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_523_times_2025_plus_decompressed_size_mod_7800_plus_max_byte_value_times_420,
    zst_compressed_size_mod_541_times_1975_plus_decompressed_size_mod_7900_plus_min_byte_value_times_2900,
)


# --- F1: zst_file_size_mod_523_times_2025_plus_decompressed_size_mod_7800_plus_max_byte_value_times_420 ---

class TestZstFileSizeMod523Times2025PlusDecompressed7800PlusMaxByte420:
    def test_text_returns_602010(self):
        assert zst_file_size_mod_523_times_2025_plus_decompressed_size_mod_7800_plus_max_byte_value_times_420(TEXT) == 602010

    def test_mini_returns_20251(self):
        assert zst_file_size_mod_523_times_2025_plus_decompressed_size_mod_7800_plus_max_byte_value_times_420(MINI) == 20251

    def test_rand_returns_667024(self):
        assert zst_file_size_mod_523_times_2025_plus_decompressed_size_mod_7800_plus_max_byte_value_times_420(RAND) == 667024

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_523_times_2025_plus_decompressed_size_mod_7800_plus_max_byte_value_times_420(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_file_size_mod_523_times_2025_plus_decompressed_size_mod_7800_plus_max_byte_value_times_420(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_file_size_mod_523_times_2025_plus_decompressed_size_mod_7800_plus_max_byte_value_times_420(RAND), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_523_times_2025_plus_decompressed_size_mod_7800_plus_max_byte_value_times_420(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_file_size_mod_523_times_2025_plus_decompressed_size_mod_7800_plus_max_byte_value_times_420(MINI) >= 0

    def test_rand_greater_than_mini(self):
        assert (zst_file_size_mod_523_times_2025_plus_decompressed_size_mod_7800_plus_max_byte_value_times_420(RAND) >
                zst_file_size_mod_523_times_2025_plus_decompressed_size_mod_7800_plus_max_byte_value_times_420(MINI))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_523_times_2025_plus_decompressed_size_mod_7800_plus_max_byte_value_times_420(str(TEXT)) == 602010


# --- F2: zst_compressed_size_mod_541_times_1975_plus_decompressed_size_mod_7900_plus_min_byte_value_times_2900 ---

class TestZstCompressedSizeMod541Times1975PlusDecompressed7900PlusMinByte2900:
    def test_text_returns_630390(self):
        assert zst_compressed_size_mod_541_times_1975_plus_decompressed_size_mod_7900_plus_min_byte_value_times_2900(TEXT) == 630390

    def test_mini_returns_19751(self):
        assert zst_compressed_size_mod_541_times_1975_plus_decompressed_size_mod_7900_plus_min_byte_value_times_2900(MINI) == 19751

    def test_rand_returns_546124(self):
        assert zst_compressed_size_mod_541_times_1975_plus_decompressed_size_mod_7900_plus_min_byte_value_times_2900(RAND) == 546124

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_541_times_1975_plus_decompressed_size_mod_7900_plus_min_byte_value_times_2900(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_compressed_size_mod_541_times_1975_plus_decompressed_size_mod_7900_plus_min_byte_value_times_2900(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_compressed_size_mod_541_times_1975_plus_decompressed_size_mod_7900_plus_min_byte_value_times_2900(RAND), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_541_times_1975_plus_decompressed_size_mod_7900_plus_min_byte_value_times_2900(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_compressed_size_mod_541_times_1975_plus_decompressed_size_mod_7900_plus_min_byte_value_times_2900(MINI) >= 0

    def test_text_greater_than_mini(self):
        assert (zst_compressed_size_mod_541_times_1975_plus_decompressed_size_mod_7900_plus_min_byte_value_times_2900(TEXT) >
                zst_compressed_size_mod_541_times_1975_plus_decompressed_size_mod_7900_plus_min_byte_value_times_2900(MINI))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_541_times_1975_plus_decompressed_size_mod_7900_plus_min_byte_value_times_2900(str(TEXT)) == 630390
