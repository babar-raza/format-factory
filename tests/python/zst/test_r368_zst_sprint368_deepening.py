"""Sprint 368 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINI = _ZST / "minimal-synthetic.zst"
RAND = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_461_times_1850_plus_decompressed_size_mod_6800_plus_max_byte_value_times_370,
    zst_compressed_size_mod_463_times_1775_plus_decompressed_size_mod_6900_plus_min_byte_value_times_2650,
)


# --- F1: zst_file_size_mod_461_times_1850_plus_decompressed_size_mod_6800_plus_max_byte_value_times_370 ---

class TestZstFileSizeMod461Times1850PlusDecompressed6800PlusMaxByte370:
    def test_text_returns_548360(self):
        assert zst_file_size_mod_461_times_1850_plus_decompressed_size_mod_6800_plus_max_byte_value_times_370(TEXT) == 548360

    def test_mini_returns_18501(self):
        assert zst_file_size_mod_461_times_1850_plus_decompressed_size_mod_6800_plus_max_byte_value_times_370(MINI) == 18501

    def test_rand_returns_605974(self):
        assert zst_file_size_mod_461_times_1850_plus_decompressed_size_mod_6800_plus_max_byte_value_times_370(RAND) == 605974

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_461_times_1850_plus_decompressed_size_mod_6800_plus_max_byte_value_times_370(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_file_size_mod_461_times_1850_plus_decompressed_size_mod_6800_plus_max_byte_value_times_370(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_file_size_mod_461_times_1850_plus_decompressed_size_mod_6800_plus_max_byte_value_times_370(RAND), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_461_times_1850_plus_decompressed_size_mod_6800_plus_max_byte_value_times_370(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_file_size_mod_461_times_1850_plus_decompressed_size_mod_6800_plus_max_byte_value_times_370(MINI) >= 0

    def test_rand_greater_than_mini(self):
        assert (zst_file_size_mod_461_times_1850_plus_decompressed_size_mod_6800_plus_max_byte_value_times_370(RAND) >
                zst_file_size_mod_461_times_1850_plus_decompressed_size_mod_6800_plus_max_byte_value_times_370(MINI))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_461_times_1850_plus_decompressed_size_mod_6800_plus_max_byte_value_times_370(str(TEXT)) == 548360


# --- F2: zst_compressed_size_mod_463_times_1775_plus_decompressed_size_mod_6900_plus_min_byte_value_times_2650 ---

class TestZstCompressedSizeMod463Times1775PlusDecompressed6900PlusMinByte2650:
    def test_text_returns_567990(self):
        assert zst_compressed_size_mod_463_times_1775_plus_decompressed_size_mod_6900_plus_min_byte_value_times_2650(TEXT) == 567990

    def test_mini_returns_17751(self):
        assert zst_compressed_size_mod_463_times_1775_plus_decompressed_size_mod_6900_plus_min_byte_value_times_2650(MINI) == 17751

    def test_rand_returns_490924(self):
        assert zst_compressed_size_mod_463_times_1775_plus_decompressed_size_mod_6900_plus_min_byte_value_times_2650(RAND) == 490924

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_463_times_1775_plus_decompressed_size_mod_6900_plus_min_byte_value_times_2650(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_compressed_size_mod_463_times_1775_plus_decompressed_size_mod_6900_plus_min_byte_value_times_2650(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_compressed_size_mod_463_times_1775_plus_decompressed_size_mod_6900_plus_min_byte_value_times_2650(RAND), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_463_times_1775_plus_decompressed_size_mod_6900_plus_min_byte_value_times_2650(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_compressed_size_mod_463_times_1775_plus_decompressed_size_mod_6900_plus_min_byte_value_times_2650(MINI) >= 0

    def test_text_greater_than_mini(self):
        assert (zst_compressed_size_mod_463_times_1775_plus_decompressed_size_mod_6900_plus_min_byte_value_times_2650(TEXT) >
                zst_compressed_size_mod_463_times_1775_plus_decompressed_size_mod_6900_plus_min_byte_value_times_2650(MINI))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_463_times_1775_plus_decompressed_size_mod_6900_plus_min_byte_value_times_2650(str(TEXT)) == 567990
