"""Sprint 356 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINI = _ZST / "minimal-synthetic.zst"
RAND = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_419_times_1650_plus_decompressed_size_mod_6000_plus_max_byte_value_times_330,
    zst_compressed_size_mod_421_times_1575_plus_decompressed_size_mod_6100_plus_min_byte_value_times_2450,
)


# --- F1: zst_file_size_mod_419_times_1650_plus_decompressed_size_mod_6000_plus_max_byte_value_times_330 ---

class TestZstFileSizeMod419Times1650PlusDecompressed6000PlusMaxByte330:
    def test_text_returns_489120(self):
        assert zst_file_size_mod_419_times_1650_plus_decompressed_size_mod_6000_plus_max_byte_value_times_330(TEXT) == 489120

    def test_mini_returns_16501(self):
        assert zst_file_size_mod_419_times_1650_plus_decompressed_size_mod_6000_plus_max_byte_value_times_330(MINI) == 16501

    def test_rand_returns_540574(self):
        assert zst_file_size_mod_419_times_1650_plus_decompressed_size_mod_6000_plus_max_byte_value_times_330(RAND) == 540574

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_419_times_1650_plus_decompressed_size_mod_6000_plus_max_byte_value_times_330(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_file_size_mod_419_times_1650_plus_decompressed_size_mod_6000_plus_max_byte_value_times_330(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_file_size_mod_419_times_1650_plus_decompressed_size_mod_6000_plus_max_byte_value_times_330(RAND), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_419_times_1650_plus_decompressed_size_mod_6000_plus_max_byte_value_times_330(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_file_size_mod_419_times_1650_plus_decompressed_size_mod_6000_plus_max_byte_value_times_330(MINI) >= 0

    def test_rand_greater_than_mini(self):
        assert (zst_file_size_mod_419_times_1650_plus_decompressed_size_mod_6000_plus_max_byte_value_times_330(RAND) >
                zst_file_size_mod_419_times_1650_plus_decompressed_size_mod_6000_plus_max_byte_value_times_330(MINI))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_419_times_1650_plus_decompressed_size_mod_6000_plus_max_byte_value_times_330(str(TEXT)) == 489120


# --- F2: zst_compressed_size_mod_421_times_1575_plus_decompressed_size_mod_6100_plus_min_byte_value_times_2450 ---

class TestZstCompressedSizeMod421Times1575PlusDecompressed6100PlusMinByte2450:
    def test_text_returns_507190(self):
        assert zst_compressed_size_mod_421_times_1575_plus_decompressed_size_mod_6100_plus_min_byte_value_times_2450(TEXT) == 507190

    def test_mini_returns_15751(self):
        assert zst_compressed_size_mod_421_times_1575_plus_decompressed_size_mod_6100_plus_min_byte_value_times_2450(MINI) == 15751

    def test_rand_returns_435724(self):
        assert zst_compressed_size_mod_421_times_1575_plus_decompressed_size_mod_6100_plus_min_byte_value_times_2450(RAND) == 435724

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_421_times_1575_plus_decompressed_size_mod_6100_plus_min_byte_value_times_2450(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_compressed_size_mod_421_times_1575_plus_decompressed_size_mod_6100_plus_min_byte_value_times_2450(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_compressed_size_mod_421_times_1575_plus_decompressed_size_mod_6100_plus_min_byte_value_times_2450(RAND), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_421_times_1575_plus_decompressed_size_mod_6100_plus_min_byte_value_times_2450(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_compressed_size_mod_421_times_1575_plus_decompressed_size_mod_6100_plus_min_byte_value_times_2450(MINI) >= 0

    def test_rand_greater_than_mini(self):
        assert (zst_compressed_size_mod_421_times_1575_plus_decompressed_size_mod_6100_plus_min_byte_value_times_2450(RAND) >
                zst_compressed_size_mod_421_times_1575_plus_decompressed_size_mod_6100_plus_min_byte_value_times_2450(MINI))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_421_times_1575_plus_decompressed_size_mod_6100_plus_min_byte_value_times_2450(str(TEXT)) == 507190
