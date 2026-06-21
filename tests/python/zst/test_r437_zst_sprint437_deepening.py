"""Sprint 437 ZST analytics deepening tests."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINI = _ZST / "minimal-synthetic.zst"
RAND = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_761_times_2750_plus_decompressed_size_mod_8500_plus_max_byte_value_times_600,
    zst_compressed_size_mod_769_times_2700_plus_decompressed_size_mod_8400_plus_min_byte_value_times_3800,
)


class TestZstFileSizeMod761Times2750PlusDecompressedMod8500PlusMaxByte600:
    def test_text_returns_820990(self):
        assert zst_file_size_mod_761_times_2750_plus_decompressed_size_mod_8500_plus_max_byte_value_times_600(TEXT) == 820990

    def test_mini_returns_27501(self):
        assert zst_file_size_mod_761_times_2750_plus_decompressed_size_mod_8500_plus_max_byte_value_times_600(MINI) == 27501

    def test_rand_returns_913024(self):
        assert zst_file_size_mod_761_times_2750_plus_decompressed_size_mod_8500_plus_max_byte_value_times_600(RAND) == 913024

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_761_times_2750_plus_decompressed_size_mod_8500_plus_max_byte_value_times_600(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_file_size_mod_761_times_2750_plus_decompressed_size_mod_8500_plus_max_byte_value_times_600(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_file_size_mod_761_times_2750_plus_decompressed_size_mod_8500_plus_max_byte_value_times_600(RAND), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_761_times_2750_plus_decompressed_size_mod_8500_plus_max_byte_value_times_600(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_file_size_mod_761_times_2750_plus_decompressed_size_mod_8500_plus_max_byte_value_times_600(MINI) >= 0

    def test_rand_greater_than_mini(self):
        assert (zst_file_size_mod_761_times_2750_plus_decompressed_size_mod_8500_plus_max_byte_value_times_600(RAND) >
                zst_file_size_mod_761_times_2750_plus_decompressed_size_mod_8500_plus_max_byte_value_times_600(MINI))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_761_times_2750_plus_decompressed_size_mod_8500_plus_max_byte_value_times_600(str(TEXT)) == 820990


class TestZstCompressedSizeMod769Times2700PlusDecompressedMod8400PlusMinByte3800:
    def test_text_returns_856390(self):
        assert zst_compressed_size_mod_769_times_2700_plus_decompressed_size_mod_8400_plus_min_byte_value_times_3800(TEXT) == 856390

    def test_mini_returns_27001(self):
        assert zst_compressed_size_mod_769_times_2700_plus_decompressed_size_mod_8400_plus_min_byte_value_times_3800(MINI) == 27001

    def test_rand_returns_746224(self):
        assert zst_compressed_size_mod_769_times_2700_plus_decompressed_size_mod_8400_plus_min_byte_value_times_3800(RAND) == 746224

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_769_times_2700_plus_decompressed_size_mod_8400_plus_min_byte_value_times_3800(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_compressed_size_mod_769_times_2700_plus_decompressed_size_mod_8400_plus_min_byte_value_times_3800(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_compressed_size_mod_769_times_2700_plus_decompressed_size_mod_8400_plus_min_byte_value_times_3800(RAND), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_769_times_2700_plus_decompressed_size_mod_8400_plus_min_byte_value_times_3800(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_compressed_size_mod_769_times_2700_plus_decompressed_size_mod_8400_plus_min_byte_value_times_3800(MINI) >= 0

    def test_text_greater_than_mini(self):
        assert (zst_compressed_size_mod_769_times_2700_plus_decompressed_size_mod_8400_plus_min_byte_value_times_3800(TEXT) >
                zst_compressed_size_mod_769_times_2700_plus_decompressed_size_mod_8400_plus_min_byte_value_times_3800(MINI))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_769_times_2700_plus_decompressed_size_mod_8400_plus_min_byte_value_times_3800(str(TEXT)) == 856390
