"""Sprint 407 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINI = _ZST / "minimal-synthetic.zst"
RAND = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_631_times_2250_plus_decompressed_size_mod_9400_plus_max_byte_value_times_500,
    zst_compressed_size_mod_641_times_2200_plus_decompressed_size_mod_9500_plus_min_byte_value_times_3300,
)


# --- F1: zst_file_size_mod_631_times_2250_plus_decompressed_size_mod_9400_plus_max_byte_value_times_500 ---

class TestZstFileSizeMod631Times2250PlusDecompressed9400PlusMaxByte500:
    def test_text_returns_672890(self):
        assert zst_file_size_mod_631_times_2250_plus_decompressed_size_mod_9400_plus_max_byte_value_times_500(TEXT) == 672890

    def test_mini_returns_22501(self):
        assert zst_file_size_mod_631_times_2250_plus_decompressed_size_mod_9400_plus_max_byte_value_times_500(MINI) == 22501

    def test_rand_returns_749524(self):
        assert zst_file_size_mod_631_times_2250_plus_decompressed_size_mod_9400_plus_max_byte_value_times_500(RAND) == 749524

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_631_times_2250_plus_decompressed_size_mod_9400_plus_max_byte_value_times_500(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_file_size_mod_631_times_2250_plus_decompressed_size_mod_9400_plus_max_byte_value_times_500(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_file_size_mod_631_times_2250_plus_decompressed_size_mod_9400_plus_max_byte_value_times_500(RAND), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_631_times_2250_plus_decompressed_size_mod_9400_plus_max_byte_value_times_500(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_file_size_mod_631_times_2250_plus_decompressed_size_mod_9400_plus_max_byte_value_times_500(MINI) >= 0

    def test_rand_greater_than_mini(self):
        assert (zst_file_size_mod_631_times_2250_plus_decompressed_size_mod_9400_plus_max_byte_value_times_500(RAND) >
                zst_file_size_mod_631_times_2250_plus_decompressed_size_mod_9400_plus_max_byte_value_times_500(MINI))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_631_times_2250_plus_decompressed_size_mod_9400_plus_max_byte_value_times_500(str(TEXT)) == 672890


# --- F2: zst_compressed_size_mod_641_times_2200_plus_decompressed_size_mod_9500_plus_min_byte_value_times_3300 ---

class TestZstCompressedSizeMod641Times2200PlusDecompressed9500PlusMinByte3300:
    def test_text_returns_704390(self):
        assert zst_compressed_size_mod_641_times_2200_plus_decompressed_size_mod_9500_plus_min_byte_value_times_3300(TEXT) == 704390

    def test_mini_returns_22001(self):
        assert zst_compressed_size_mod_641_times_2200_plus_decompressed_size_mod_9500_plus_min_byte_value_times_3300(MINI) == 22001

    def test_rand_returns_608224(self):
        assert zst_compressed_size_mod_641_times_2200_plus_decompressed_size_mod_9500_plus_min_byte_value_times_3300(RAND) == 608224

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_641_times_2200_plus_decompressed_size_mod_9500_plus_min_byte_value_times_3300(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_compressed_size_mod_641_times_2200_plus_decompressed_size_mod_9500_plus_min_byte_value_times_3300(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_compressed_size_mod_641_times_2200_plus_decompressed_size_mod_9500_plus_min_byte_value_times_3300(RAND), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_641_times_2200_plus_decompressed_size_mod_9500_plus_min_byte_value_times_3300(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_compressed_size_mod_641_times_2200_plus_decompressed_size_mod_9500_plus_min_byte_value_times_3300(MINI) >= 0

    def test_text_greater_than_mini(self):
        assert (zst_compressed_size_mod_641_times_2200_plus_decompressed_size_mod_9500_plus_min_byte_value_times_3300(TEXT) >
                zst_compressed_size_mod_641_times_2200_plus_decompressed_size_mod_9500_plus_min_byte_value_times_3300(MINI))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_641_times_2200_plus_decompressed_size_mod_9500_plus_min_byte_value_times_3300(str(TEXT)) == 704390
