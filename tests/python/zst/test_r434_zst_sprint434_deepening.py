"""Sprint 434 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINI = _ZST / "minimal-synthetic.zst"
RAND = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_751_times_2700_plus_decompressed_size_mod_8700_plus_max_byte_value_times_590,
    zst_compressed_size_mod_757_times_2650_plus_decompressed_size_mod_8600_plus_min_byte_value_times_3750,
)


class TestZstFileSizeMod751Times2700PlusDecompressedMod8700PlusMaxByte590:
    def test_text_returns_806180(self):
        assert zst_file_size_mod_751_times_2700_plus_decompressed_size_mod_8700_plus_max_byte_value_times_590(TEXT) == 806180

    def test_mini_returns_27001(self):
        assert zst_file_size_mod_751_times_2700_plus_decompressed_size_mod_8700_plus_max_byte_value_times_590(MINI) == 27001

    def test_rand_returns_896674(self):
        assert zst_file_size_mod_751_times_2700_plus_decompressed_size_mod_8700_plus_max_byte_value_times_590(RAND) == 896674

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_751_times_2700_plus_decompressed_size_mod_8700_plus_max_byte_value_times_590(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_file_size_mod_751_times_2700_plus_decompressed_size_mod_8700_plus_max_byte_value_times_590(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_file_size_mod_751_times_2700_plus_decompressed_size_mod_8700_plus_max_byte_value_times_590(RAND), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_751_times_2700_plus_decompressed_size_mod_8700_plus_max_byte_value_times_590(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_file_size_mod_751_times_2700_plus_decompressed_size_mod_8700_plus_max_byte_value_times_590(MINI) >= 0

    def test_rand_greater_than_mini(self):
        assert (zst_file_size_mod_751_times_2700_plus_decompressed_size_mod_8700_plus_max_byte_value_times_590(RAND) >
                zst_file_size_mod_751_times_2700_plus_decompressed_size_mod_8700_plus_max_byte_value_times_590(MINI))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_751_times_2700_plus_decompressed_size_mod_8700_plus_max_byte_value_times_590(str(TEXT)) == 806180


class TestZstCompressedSizeMod757Times2650PlusDecompressedMod8600PlusMinByte3750:
    def test_text_returns_841190(self):
        assert zst_compressed_size_mod_757_times_2650_plus_decompressed_size_mod_8600_plus_min_byte_value_times_3750(TEXT) == 841190

    def test_mini_returns_26501(self):
        assert zst_compressed_size_mod_757_times_2650_plus_decompressed_size_mod_8600_plus_min_byte_value_times_3750(MINI) == 26501

    def test_rand_returns_732424(self):
        assert zst_compressed_size_mod_757_times_2650_plus_decompressed_size_mod_8600_plus_min_byte_value_times_3750(RAND) == 732424

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_757_times_2650_plus_decompressed_size_mod_8600_plus_min_byte_value_times_3750(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_compressed_size_mod_757_times_2650_plus_decompressed_size_mod_8600_plus_min_byte_value_times_3750(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_compressed_size_mod_757_times_2650_plus_decompressed_size_mod_8600_plus_min_byte_value_times_3750(RAND), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_757_times_2650_plus_decompressed_size_mod_8600_plus_min_byte_value_times_3750(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_compressed_size_mod_757_times_2650_plus_decompressed_size_mod_8600_plus_min_byte_value_times_3750(MINI) >= 0

    def test_text_greater_than_mini(self):
        assert (zst_compressed_size_mod_757_times_2650_plus_decompressed_size_mod_8600_plus_min_byte_value_times_3750(TEXT) >
                zst_compressed_size_mod_757_times_2650_plus_decompressed_size_mod_8600_plus_min_byte_value_times_3750(MINI))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_757_times_2650_plus_decompressed_size_mod_8600_plus_min_byte_value_times_3750(str(TEXT)) == 841190
