"""Sprint 422 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINI = _ZST / "minimal-synthetic.zst"
RAND = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_691_times_2500_plus_decompressed_size_mod_9500_plus_max_byte_value_times_550,
    zst_compressed_size_mod_701_times_2450_plus_decompressed_size_mod_9400_plus_min_byte_value_times_3550,
)


# --- F1: zst_file_size_mod_691_times_2500_plus_decompressed_size_mod_9500_plus_max_byte_value_times_550 ---

class TestZstFileSizeMod691Times2500PlusDecompressedMod9500PlusMaxByte550:
    def test_text_returns_746940(self):
        assert zst_file_size_mod_691_times_2500_plus_decompressed_size_mod_9500_plus_max_byte_value_times_550(TEXT) == 746940

    def test_mini_returns_25001(self):
        assert zst_file_size_mod_691_times_2500_plus_decompressed_size_mod_9500_plus_max_byte_value_times_550(MINI) == 25001

    def test_rand_returns_831274(self):
        assert zst_file_size_mod_691_times_2500_plus_decompressed_size_mod_9500_plus_max_byte_value_times_550(RAND) == 831274

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_691_times_2500_plus_decompressed_size_mod_9500_plus_max_byte_value_times_550(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_file_size_mod_691_times_2500_plus_decompressed_size_mod_9500_plus_max_byte_value_times_550(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_file_size_mod_691_times_2500_plus_decompressed_size_mod_9500_plus_max_byte_value_times_550(RAND), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_691_times_2500_plus_decompressed_size_mod_9500_plus_max_byte_value_times_550(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_file_size_mod_691_times_2500_plus_decompressed_size_mod_9500_plus_max_byte_value_times_550(MINI) >= 0

    def test_rand_greater_than_mini(self):
        assert (zst_file_size_mod_691_times_2500_plus_decompressed_size_mod_9500_plus_max_byte_value_times_550(RAND) >
                zst_file_size_mod_691_times_2500_plus_decompressed_size_mod_9500_plus_max_byte_value_times_550(MINI))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_691_times_2500_plus_decompressed_size_mod_9500_plus_max_byte_value_times_550(str(TEXT)) == 746940


# --- F2: zst_compressed_size_mod_701_times_2450_plus_decompressed_size_mod_9400_plus_min_byte_value_times_3550 ---

class TestZstCompressedSizeMod701Times2450PlusDecompressedMod9400PlusMinByte3550:
    def test_text_returns_780390(self):
        assert zst_compressed_size_mod_701_times_2450_plus_decompressed_size_mod_9400_plus_min_byte_value_times_3550(TEXT) == 780390

    def test_mini_returns_24501(self):
        assert zst_compressed_size_mod_701_times_2450_plus_decompressed_size_mod_9400_plus_min_byte_value_times_3550(MINI) == 24501

    def test_rand_returns_677224(self):
        assert zst_compressed_size_mod_701_times_2450_plus_decompressed_size_mod_9400_plus_min_byte_value_times_3550(RAND) == 677224

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_701_times_2450_plus_decompressed_size_mod_9400_plus_min_byte_value_times_3550(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_compressed_size_mod_701_times_2450_plus_decompressed_size_mod_9400_plus_min_byte_value_times_3550(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_compressed_size_mod_701_times_2450_plus_decompressed_size_mod_9400_plus_min_byte_value_times_3550(RAND), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_701_times_2450_plus_decompressed_size_mod_9400_plus_min_byte_value_times_3550(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_compressed_size_mod_701_times_2450_plus_decompressed_size_mod_9400_plus_min_byte_value_times_3550(MINI) >= 0

    def test_text_greater_than_mini(self):
        assert (zst_compressed_size_mod_701_times_2450_plus_decompressed_size_mod_9400_plus_min_byte_value_times_3550(TEXT) >
                zst_compressed_size_mod_701_times_2450_plus_decompressed_size_mod_9400_plus_min_byte_value_times_3550(MINI))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_701_times_2450_plus_decompressed_size_mod_9400_plus_min_byte_value_times_3550(str(TEXT)) == 780390
