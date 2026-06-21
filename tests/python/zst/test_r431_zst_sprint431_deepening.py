"""Sprint 431 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINI = _ZST / "minimal-synthetic.zst"
RAND = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_739_times_2650_plus_decompressed_size_mod_8900_plus_max_byte_value_times_580,
    zst_compressed_size_mod_743_times_2600_plus_decompressed_size_mod_8800_plus_min_byte_value_times_3700,
)


# --- F1: zst_file_size_mod_739_times_2650_plus_decompressed_size_mod_8900_plus_max_byte_value_times_580 ---

class TestZstFileSizeMod739Times2650PlusDecompressedMod8900PlusMaxByte580:
    def test_text_returns_791370(self):
        assert zst_file_size_mod_739_times_2650_plus_decompressed_size_mod_8900_plus_max_byte_value_times_580(TEXT) == 791370

    def test_mini_returns_26501(self):
        assert zst_file_size_mod_739_times_2650_plus_decompressed_size_mod_8900_plus_max_byte_value_times_580(MINI) == 26501

    def test_rand_returns_880324(self):
        assert zst_file_size_mod_739_times_2650_plus_decompressed_size_mod_8900_plus_max_byte_value_times_580(RAND) == 880324

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_739_times_2650_plus_decompressed_size_mod_8900_plus_max_byte_value_times_580(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_file_size_mod_739_times_2650_plus_decompressed_size_mod_8900_plus_max_byte_value_times_580(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_file_size_mod_739_times_2650_plus_decompressed_size_mod_8900_plus_max_byte_value_times_580(RAND), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_739_times_2650_plus_decompressed_size_mod_8900_plus_max_byte_value_times_580(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_file_size_mod_739_times_2650_plus_decompressed_size_mod_8900_plus_max_byte_value_times_580(MINI) >= 0

    def test_rand_greater_than_mini(self):
        assert (zst_file_size_mod_739_times_2650_plus_decompressed_size_mod_8900_plus_max_byte_value_times_580(RAND) >
                zst_file_size_mod_739_times_2650_plus_decompressed_size_mod_8900_plus_max_byte_value_times_580(MINI))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_739_times_2650_plus_decompressed_size_mod_8900_plus_max_byte_value_times_580(str(TEXT)) == 791370


# --- F2: zst_compressed_size_mod_743_times_2600_plus_decompressed_size_mod_8800_plus_min_byte_value_times_3700 ---

class TestZstCompressedSizeMod743Times2600PlusDecompressedMod8800PlusMinByte3700:
    def test_text_returns_825990(self):
        assert zst_compressed_size_mod_743_times_2600_plus_decompressed_size_mod_8800_plus_min_byte_value_times_3700(TEXT) == 825990

    def test_mini_returns_26001(self):
        assert zst_compressed_size_mod_743_times_2600_plus_decompressed_size_mod_8800_plus_min_byte_value_times_3700(MINI) == 26001

    def test_rand_returns_718624(self):
        assert zst_compressed_size_mod_743_times_2600_plus_decompressed_size_mod_8800_plus_min_byte_value_times_3700(RAND) == 718624

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_743_times_2600_plus_decompressed_size_mod_8800_plus_min_byte_value_times_3700(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_compressed_size_mod_743_times_2600_plus_decompressed_size_mod_8800_plus_min_byte_value_times_3700(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_compressed_size_mod_743_times_2600_plus_decompressed_size_mod_8800_plus_min_byte_value_times_3700(RAND), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_743_times_2600_plus_decompressed_size_mod_8800_plus_min_byte_value_times_3700(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_compressed_size_mod_743_times_2600_plus_decompressed_size_mod_8800_plus_min_byte_value_times_3700(MINI) >= 0

    def test_text_greater_than_mini(self):
        assert (zst_compressed_size_mod_743_times_2600_plus_decompressed_size_mod_8800_plus_min_byte_value_times_3700(TEXT) >
                zst_compressed_size_mod_743_times_2600_plus_decompressed_size_mod_8800_plus_min_byte_value_times_3700(MINI))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_743_times_2600_plus_decompressed_size_mod_8800_plus_min_byte_value_times_3700(str(TEXT)) == 825990
