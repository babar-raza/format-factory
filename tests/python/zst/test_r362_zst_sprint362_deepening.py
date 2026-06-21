"""Sprint 362 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINI = _ZST / "minimal-synthetic.zst"
RAND = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_439_times_1750_plus_decompressed_size_mod_6400_plus_max_byte_value_times_350,
    zst_compressed_size_mod_443_times_1675_plus_decompressed_size_mod_6500_plus_min_byte_value_times_2550,
)


# --- F1: zst_file_size_mod_439_times_1750_plus_decompressed_size_mod_6400_plus_max_byte_value_times_350 ---

class TestZstFileSizeMod439Times1750PlusDecompressed6400PlusMaxByte350:
    def test_text_returns_518740(self):
        assert zst_file_size_mod_439_times_1750_plus_decompressed_size_mod_6400_plus_max_byte_value_times_350(TEXT) == 518740

    def test_mini_returns_17501(self):
        assert zst_file_size_mod_439_times_1750_plus_decompressed_size_mod_6400_plus_max_byte_value_times_350(MINI) == 17501

    def test_rand_returns_573274(self):
        assert zst_file_size_mod_439_times_1750_plus_decompressed_size_mod_6400_plus_max_byte_value_times_350(RAND) == 573274

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_439_times_1750_plus_decompressed_size_mod_6400_plus_max_byte_value_times_350(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_file_size_mod_439_times_1750_plus_decompressed_size_mod_6400_plus_max_byte_value_times_350(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_file_size_mod_439_times_1750_plus_decompressed_size_mod_6400_plus_max_byte_value_times_350(RAND), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_439_times_1750_plus_decompressed_size_mod_6400_plus_max_byte_value_times_350(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_file_size_mod_439_times_1750_plus_decompressed_size_mod_6400_plus_max_byte_value_times_350(MINI) >= 0

    def test_rand_greater_than_mini(self):
        assert (zst_file_size_mod_439_times_1750_plus_decompressed_size_mod_6400_plus_max_byte_value_times_350(RAND) >
                zst_file_size_mod_439_times_1750_plus_decompressed_size_mod_6400_plus_max_byte_value_times_350(MINI))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_439_times_1750_plus_decompressed_size_mod_6400_plus_max_byte_value_times_350(str(TEXT)) == 518740


# --- F2: zst_compressed_size_mod_443_times_1675_plus_decompressed_size_mod_6500_plus_min_byte_value_times_2550 ---

class TestZstCompressedSizeMod443Times1675PlusDecompressed6500PlusMinByte2550:
    def test_text_returns_537590(self):
        assert zst_compressed_size_mod_443_times_1675_plus_decompressed_size_mod_6500_plus_min_byte_value_times_2550(TEXT) == 537590

    def test_mini_returns_16751(self):
        assert zst_compressed_size_mod_443_times_1675_plus_decompressed_size_mod_6500_plus_min_byte_value_times_2550(MINI) == 16751

    def test_rand_returns_463324(self):
        assert zst_compressed_size_mod_443_times_1675_plus_decompressed_size_mod_6500_plus_min_byte_value_times_2550(RAND) == 463324

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_443_times_1675_plus_decompressed_size_mod_6500_plus_min_byte_value_times_2550(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_compressed_size_mod_443_times_1675_plus_decompressed_size_mod_6500_plus_min_byte_value_times_2550(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_compressed_size_mod_443_times_1675_plus_decompressed_size_mod_6500_plus_min_byte_value_times_2550(RAND), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_443_times_1675_plus_decompressed_size_mod_6500_plus_min_byte_value_times_2550(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_compressed_size_mod_443_times_1675_plus_decompressed_size_mod_6500_plus_min_byte_value_times_2550(MINI) >= 0

    def test_text_greater_than_mini(self):
        assert (zst_compressed_size_mod_443_times_1675_plus_decompressed_size_mod_6500_plus_min_byte_value_times_2550(TEXT) >
                zst_compressed_size_mod_443_times_1675_plus_decompressed_size_mod_6500_plus_min_byte_value_times_2550(MINI))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_443_times_1675_plus_decompressed_size_mod_6500_plus_min_byte_value_times_2550(str(TEXT)) == 537590
