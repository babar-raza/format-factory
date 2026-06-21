"""Sprint 392 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINI = _ZST / "minimal-synthetic.zst"
RAND = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_571_times_2100_plus_decompressed_size_mod_8400_plus_max_byte_value_times_450,
    zst_compressed_size_mod_577_times_2050_plus_decompressed_size_mod_8500_plus_min_byte_value_times_3050,
)


# --- F1: zst_file_size_mod_571_times_2100_plus_decompressed_size_mod_8400_plus_max_byte_value_times_450 ---

class TestZstFileSizeMod571Times2100PlusDecompressed8400PlusMaxByte450:
    def test_text_returns_626040(self):
        assert zst_file_size_mod_571_times_2100_plus_decompressed_size_mod_8400_plus_max_byte_value_times_450(TEXT) == 626040

    def test_mini_returns_21001(self):
        assert zst_file_size_mod_571_times_2100_plus_decompressed_size_mod_8400_plus_max_byte_value_times_450(MINI) == 21001

    def test_rand_returns_695374(self):
        assert zst_file_size_mod_571_times_2100_plus_decompressed_size_mod_8400_plus_max_byte_value_times_450(RAND) == 695374

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_571_times_2100_plus_decompressed_size_mod_8400_plus_max_byte_value_times_450(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_file_size_mod_571_times_2100_plus_decompressed_size_mod_8400_plus_max_byte_value_times_450(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_file_size_mod_571_times_2100_plus_decompressed_size_mod_8400_plus_max_byte_value_times_450(RAND), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_571_times_2100_plus_decompressed_size_mod_8400_plus_max_byte_value_times_450(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_file_size_mod_571_times_2100_plus_decompressed_size_mod_8400_plus_max_byte_value_times_450(MINI) >= 0

    def test_rand_greater_than_mini(self):
        assert (zst_file_size_mod_571_times_2100_plus_decompressed_size_mod_8400_plus_max_byte_value_times_450(RAND) >
                zst_file_size_mod_571_times_2100_plus_decompressed_size_mod_8400_plus_max_byte_value_times_450(MINI))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_571_times_2100_plus_decompressed_size_mod_8400_plus_max_byte_value_times_450(str(TEXT)) == 626040


# --- F2: zst_compressed_size_mod_577_times_2050_plus_decompressed_size_mod_8500_plus_min_byte_value_times_3050 ---

class TestZstCompressedSizeMod577Times2050PlusDecompressed8500PlusMinByte3050:
    def test_text_returns_655590(self):
        assert zst_compressed_size_mod_577_times_2050_plus_decompressed_size_mod_8500_plus_min_byte_value_times_3050(TEXT) == 655590

    def test_mini_returns_20501(self):
        assert zst_compressed_size_mod_577_times_2050_plus_decompressed_size_mod_8500_plus_min_byte_value_times_3050(MINI) == 20501

    def test_rand_returns_566824(self):
        assert zst_compressed_size_mod_577_times_2050_plus_decompressed_size_mod_8500_plus_min_byte_value_times_3050(RAND) == 566824

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_577_times_2050_plus_decompressed_size_mod_8500_plus_min_byte_value_times_3050(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_compressed_size_mod_577_times_2050_plus_decompressed_size_mod_8500_plus_min_byte_value_times_3050(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_compressed_size_mod_577_times_2050_plus_decompressed_size_mod_8500_plus_min_byte_value_times_3050(RAND), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_577_times_2050_plus_decompressed_size_mod_8500_plus_min_byte_value_times_3050(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_compressed_size_mod_577_times_2050_plus_decompressed_size_mod_8500_plus_min_byte_value_times_3050(MINI) >= 0

    def test_text_greater_than_mini(self):
        assert (zst_compressed_size_mod_577_times_2050_plus_decompressed_size_mod_8500_plus_min_byte_value_times_3050(TEXT) >
                zst_compressed_size_mod_577_times_2050_plus_decompressed_size_mod_8500_plus_min_byte_value_times_3050(MINI))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_577_times_2050_plus_decompressed_size_mod_8500_plus_min_byte_value_times_3050(str(TEXT)) == 655590
