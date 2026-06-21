"""Sprint 386 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINI = _ZST / "minimal-synthetic.zst"
RAND = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_547_times_2050_plus_decompressed_size_mod_8000_plus_max_byte_value_times_430,
    zst_compressed_size_mod_557_times_2000_plus_decompressed_size_mod_8100_plus_min_byte_value_times_2950,
)


# --- F1: zst_file_size_mod_547_times_2050_plus_decompressed_size_mod_8000_plus_max_byte_value_times_430 ---

class TestZstFileSizeMod547Times2050PlusDecompressed8000PlusMaxByte430:
    def test_text_returns_610020(self):
        assert zst_file_size_mod_547_times_2050_plus_decompressed_size_mod_8000_plus_max_byte_value_times_430(TEXT) == 610020

    def test_mini_returns_20501(self):
        assert zst_file_size_mod_547_times_2050_plus_decompressed_size_mod_8000_plus_max_byte_value_times_430(MINI) == 20501

    def test_rand_returns_676474(self):
        assert zst_file_size_mod_547_times_2050_plus_decompressed_size_mod_8000_plus_max_byte_value_times_430(RAND) == 676474

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_547_times_2050_plus_decompressed_size_mod_8000_plus_max_byte_value_times_430(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_file_size_mod_547_times_2050_plus_decompressed_size_mod_8000_plus_max_byte_value_times_430(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_file_size_mod_547_times_2050_plus_decompressed_size_mod_8000_plus_max_byte_value_times_430(RAND), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_547_times_2050_plus_decompressed_size_mod_8000_plus_max_byte_value_times_430(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_file_size_mod_547_times_2050_plus_decompressed_size_mod_8000_plus_max_byte_value_times_430(MINI) >= 0

    def test_rand_greater_than_mini(self):
        assert (zst_file_size_mod_547_times_2050_plus_decompressed_size_mod_8000_plus_max_byte_value_times_430(RAND) >
                zst_file_size_mod_547_times_2050_plus_decompressed_size_mod_8000_plus_max_byte_value_times_430(MINI))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_547_times_2050_plus_decompressed_size_mod_8000_plus_max_byte_value_times_430(str(TEXT)) == 610020


# --- F2: zst_compressed_size_mod_557_times_2000_plus_decompressed_size_mod_8100_plus_min_byte_value_times_2950 ---

class TestZstCompressedSizeMod557Times2000PlusDecompressed8100PlusMinByte2950:
    def test_text_returns_638790(self):
        assert zst_compressed_size_mod_557_times_2000_plus_decompressed_size_mod_8100_plus_min_byte_value_times_2950(TEXT) == 638790

    def test_mini_returns_20001(self):
        assert zst_compressed_size_mod_557_times_2000_plus_decompressed_size_mod_8100_plus_min_byte_value_times_2950(MINI) == 20001

    def test_rand_returns_553024(self):
        assert zst_compressed_size_mod_557_times_2000_plus_decompressed_size_mod_8100_plus_min_byte_value_times_2950(RAND) == 553024

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_557_times_2000_plus_decompressed_size_mod_8100_plus_min_byte_value_times_2950(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_compressed_size_mod_557_times_2000_plus_decompressed_size_mod_8100_plus_min_byte_value_times_2950(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_compressed_size_mod_557_times_2000_plus_decompressed_size_mod_8100_plus_min_byte_value_times_2950(RAND), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_557_times_2000_plus_decompressed_size_mod_8100_plus_min_byte_value_times_2950(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_compressed_size_mod_557_times_2000_plus_decompressed_size_mod_8100_plus_min_byte_value_times_2950(MINI) >= 0

    def test_text_greater_than_mini(self):
        assert (zst_compressed_size_mod_557_times_2000_plus_decompressed_size_mod_8100_plus_min_byte_value_times_2950(TEXT) >
                zst_compressed_size_mod_557_times_2000_plus_decompressed_size_mod_8100_plus_min_byte_value_times_2950(MINI))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_557_times_2000_plus_decompressed_size_mod_8100_plus_min_byte_value_times_2950(str(TEXT)) == 638790
