"""Sprint 371 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINI = _ZST / "minimal-synthetic.zst"
RAND = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_467_times_1900_plus_decompressed_size_mod_7000_plus_max_byte_value_times_380,
    zst_compressed_size_mod_479_times_1825_plus_decompressed_size_mod_7100_plus_min_byte_value_times_2700,
)


# --- F1: zst_file_size_mod_467_times_1900_plus_decompressed_size_mod_7000_plus_max_byte_value_times_380 ---

class TestZstFileSizeMod467Times1900PlusDecompressed7000PlusMaxByte380:
    def test_text_returns_563170(self):
        assert zst_file_size_mod_467_times_1900_plus_decompressed_size_mod_7000_plus_max_byte_value_times_380(TEXT) == 563170

    def test_mini_returns_19001(self):
        assert zst_file_size_mod_467_times_1900_plus_decompressed_size_mod_7000_plus_max_byte_value_times_380(MINI) == 19001

    def test_rand_returns_622324(self):
        assert zst_file_size_mod_467_times_1900_plus_decompressed_size_mod_7000_plus_max_byte_value_times_380(RAND) == 622324

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_467_times_1900_plus_decompressed_size_mod_7000_plus_max_byte_value_times_380(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_file_size_mod_467_times_1900_plus_decompressed_size_mod_7000_plus_max_byte_value_times_380(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_file_size_mod_467_times_1900_plus_decompressed_size_mod_7000_plus_max_byte_value_times_380(RAND), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_467_times_1900_plus_decompressed_size_mod_7000_plus_max_byte_value_times_380(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_file_size_mod_467_times_1900_plus_decompressed_size_mod_7000_plus_max_byte_value_times_380(MINI) >= 0

    def test_rand_greater_than_mini(self):
        assert (zst_file_size_mod_467_times_1900_plus_decompressed_size_mod_7000_plus_max_byte_value_times_380(RAND) >
                zst_file_size_mod_467_times_1900_plus_decompressed_size_mod_7000_plus_max_byte_value_times_380(MINI))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_467_times_1900_plus_decompressed_size_mod_7000_plus_max_byte_value_times_380(str(TEXT)) == 563170


# --- F2: zst_compressed_size_mod_479_times_1825_plus_decompressed_size_mod_7100_plus_min_byte_value_times_2700 ---

class TestZstCompressedSizeMod479Times1825PlusDecompressed7100PlusMinByte2700:
    def test_text_returns_583190(self):
        assert zst_compressed_size_mod_479_times_1825_plus_decompressed_size_mod_7100_plus_min_byte_value_times_2700(TEXT) == 583190

    def test_mini_returns_18251(self):
        assert zst_compressed_size_mod_479_times_1825_plus_decompressed_size_mod_7100_plus_min_byte_value_times_2700(MINI) == 18251

    def test_rand_returns_504724(self):
        assert zst_compressed_size_mod_479_times_1825_plus_decompressed_size_mod_7100_plus_min_byte_value_times_2700(RAND) == 504724

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_479_times_1825_plus_decompressed_size_mod_7100_plus_min_byte_value_times_2700(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_compressed_size_mod_479_times_1825_plus_decompressed_size_mod_7100_plus_min_byte_value_times_2700(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_compressed_size_mod_479_times_1825_plus_decompressed_size_mod_7100_plus_min_byte_value_times_2700(RAND), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_479_times_1825_plus_decompressed_size_mod_7100_plus_min_byte_value_times_2700(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_compressed_size_mod_479_times_1825_plus_decompressed_size_mod_7100_plus_min_byte_value_times_2700(MINI) >= 0

    def test_text_greater_than_mini(self):
        assert (zst_compressed_size_mod_479_times_1825_plus_decompressed_size_mod_7100_plus_min_byte_value_times_2700(TEXT) >
                zst_compressed_size_mod_479_times_1825_plus_decompressed_size_mod_7100_plus_min_byte_value_times_2700(MINI))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_479_times_1825_plus_decompressed_size_mod_7100_plus_min_byte_value_times_2700(str(TEXT)) == 583190
