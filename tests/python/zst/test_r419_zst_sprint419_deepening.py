"""Sprint 419 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINI = _ZST / "minimal-synthetic.zst"
RAND = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_677_times_2450_plus_decompressed_size_mod_9700_plus_max_byte_value_times_540,
    zst_compressed_size_mod_683_times_2400_plus_decompressed_size_mod_9600_plus_min_byte_value_times_3500,
)


# --- F1: zst_file_size_mod_677_times_2450_plus_decompressed_size_mod_9700_plus_max_byte_value_times_540 ---

class TestZstFileSizeMod677Times2450PlusDecompressed9700PlusMaxByte540:
    def test_text_returns_732130(self):
        assert zst_file_size_mod_677_times_2450_plus_decompressed_size_mod_9700_plus_max_byte_value_times_540(TEXT) == 732130

    def test_mini_returns_24501(self):
        assert zst_file_size_mod_677_times_2450_plus_decompressed_size_mod_9700_plus_max_byte_value_times_540(MINI) == 24501

    def test_rand_returns_814924(self):
        assert zst_file_size_mod_677_times_2450_plus_decompressed_size_mod_9700_plus_max_byte_value_times_540(RAND) == 814924

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_677_times_2450_plus_decompressed_size_mod_9700_plus_max_byte_value_times_540(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_file_size_mod_677_times_2450_plus_decompressed_size_mod_9700_plus_max_byte_value_times_540(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_file_size_mod_677_times_2450_plus_decompressed_size_mod_9700_plus_max_byte_value_times_540(RAND), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_677_times_2450_plus_decompressed_size_mod_9700_plus_max_byte_value_times_540(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_file_size_mod_677_times_2450_plus_decompressed_size_mod_9700_plus_max_byte_value_times_540(MINI) >= 0

    def test_rand_greater_than_mini(self):
        assert (zst_file_size_mod_677_times_2450_plus_decompressed_size_mod_9700_plus_max_byte_value_times_540(RAND) >
                zst_file_size_mod_677_times_2450_plus_decompressed_size_mod_9700_plus_max_byte_value_times_540(MINI))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_677_times_2450_plus_decompressed_size_mod_9700_plus_max_byte_value_times_540(str(TEXT)) == 732130


# --- F2: zst_compressed_size_mod_683_times_2400_plus_decompressed_size_mod_9600_plus_min_byte_value_times_3500 ---

class TestZstCompressedSizeMod683Times2400PlusDecompressed9600PlusMinByte3500:
    def test_text_returns_765190(self):
        assert zst_compressed_size_mod_683_times_2400_plus_decompressed_size_mod_9600_plus_min_byte_value_times_3500(TEXT) == 765190

    def test_mini_returns_24001(self):
        assert zst_compressed_size_mod_683_times_2400_plus_decompressed_size_mod_9600_plus_min_byte_value_times_3500(MINI) == 24001

    def test_rand_returns_663424(self):
        assert zst_compressed_size_mod_683_times_2400_plus_decompressed_size_mod_9600_plus_min_byte_value_times_3500(RAND) == 663424

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_683_times_2400_plus_decompressed_size_mod_9600_plus_min_byte_value_times_3500(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_compressed_size_mod_683_times_2400_plus_decompressed_size_mod_9600_plus_min_byte_value_times_3500(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_compressed_size_mod_683_times_2400_plus_decompressed_size_mod_9600_plus_min_byte_value_times_3500(RAND), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_683_times_2400_plus_decompressed_size_mod_9600_plus_min_byte_value_times_3500(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_compressed_size_mod_683_times_2400_plus_decompressed_size_mod_9600_plus_min_byte_value_times_3500(MINI) >= 0

    def test_text_greater_than_mini(self):
        assert (zst_compressed_size_mod_683_times_2400_plus_decompressed_size_mod_9600_plus_min_byte_value_times_3500(TEXT) >
                zst_compressed_size_mod_683_times_2400_plus_decompressed_size_mod_9600_plus_min_byte_value_times_3500(MINI))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_683_times_2400_plus_decompressed_size_mod_9600_plus_min_byte_value_times_3500(str(TEXT)) == 765190
