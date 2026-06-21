"""Sprint 401 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINI = _ZST / "minimal-synthetic.zst"
RAND = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_607_times_2175_plus_decompressed_size_mod_9000_plus_max_byte_value_times_480,
    zst_compressed_size_mod_613_times_2125_plus_decompressed_size_mod_9100_plus_min_byte_value_times_3200,
)


# --- F1: zst_file_size_mod_607_times_2175_plus_decompressed_size_mod_9000_plus_max_byte_value_times_480 ---

class TestZstFileSizeMod607Times2175PlusDecompressed9000PlusMaxByte480:
    def test_text_returns_650070(self):
        assert zst_file_size_mod_607_times_2175_plus_decompressed_size_mod_9000_plus_max_byte_value_times_480(TEXT) == 650070

    def test_mini_returns_21751(self):
        assert zst_file_size_mod_607_times_2175_plus_decompressed_size_mod_9000_plus_max_byte_value_times_480(MINI) == 21751

    def test_rand_returns_723724(self):
        assert zst_file_size_mod_607_times_2175_plus_decompressed_size_mod_9000_plus_max_byte_value_times_480(RAND) == 723724

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_607_times_2175_plus_decompressed_size_mod_9000_plus_max_byte_value_times_480(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_file_size_mod_607_times_2175_plus_decompressed_size_mod_9000_plus_max_byte_value_times_480(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_file_size_mod_607_times_2175_plus_decompressed_size_mod_9000_plus_max_byte_value_times_480(RAND), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_607_times_2175_plus_decompressed_size_mod_9000_plus_max_byte_value_times_480(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_file_size_mod_607_times_2175_plus_decompressed_size_mod_9000_plus_max_byte_value_times_480(MINI) >= 0

    def test_rand_greater_than_mini(self):
        assert (zst_file_size_mod_607_times_2175_plus_decompressed_size_mod_9000_plus_max_byte_value_times_480(RAND) >
                zst_file_size_mod_607_times_2175_plus_decompressed_size_mod_9000_plus_max_byte_value_times_480(MINI))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_607_times_2175_plus_decompressed_size_mod_9000_plus_max_byte_value_times_480(str(TEXT)) == 650070


# --- F2: zst_compressed_size_mod_613_times_2125_plus_decompressed_size_mod_9100_plus_min_byte_value_times_3200 ---

class TestZstCompressedSizeMod613Times2125PlusDecompressed9100PlusMinByte3200:
    def test_text_returns_680790(self):
        assert zst_compressed_size_mod_613_times_2125_plus_decompressed_size_mod_9100_plus_min_byte_value_times_3200(TEXT) == 680790

    def test_mini_returns_21251(self):
        assert zst_compressed_size_mod_613_times_2125_plus_decompressed_size_mod_9100_plus_min_byte_value_times_3200(MINI) == 21251

    def test_rand_returns_587524(self):
        assert zst_compressed_size_mod_613_times_2125_plus_decompressed_size_mod_9100_plus_min_byte_value_times_3200(RAND) == 587524

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_613_times_2125_plus_decompressed_size_mod_9100_plus_min_byte_value_times_3200(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_compressed_size_mod_613_times_2125_plus_decompressed_size_mod_9100_plus_min_byte_value_times_3200(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_compressed_size_mod_613_times_2125_plus_decompressed_size_mod_9100_plus_min_byte_value_times_3200(RAND), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_613_times_2125_plus_decompressed_size_mod_9100_plus_min_byte_value_times_3200(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_compressed_size_mod_613_times_2125_plus_decompressed_size_mod_9100_plus_min_byte_value_times_3200(MINI) >= 0

    def test_text_greater_than_mini(self):
        assert (zst_compressed_size_mod_613_times_2125_plus_decompressed_size_mod_9100_plus_min_byte_value_times_3200(TEXT) >
                zst_compressed_size_mod_613_times_2125_plus_decompressed_size_mod_9100_plus_min_byte_value_times_3200(MINI))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_613_times_2125_plus_decompressed_size_mod_9100_plus_min_byte_value_times_3200(str(TEXT)) == 680790
