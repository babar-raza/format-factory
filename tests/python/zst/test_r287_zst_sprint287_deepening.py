"""Sprint 287 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINIMAL = _ZST / "minimal-synthetic.zst"
RANDOM = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_109_times_500_plus_decompressed_size_mod_1500_plus_max_byte_value_times_100,
    zst_compressed_size_mod_113_times_450_plus_decompressed_size_mod_1600_plus_min_byte_value_times_900,
)


# --- F1: zst_file_size_mod_109_times_500_plus_decompressed_size_mod_1500_plus_max_byte_value_times_100 ---

class TestZstFileSizeMod109Times500PlusDecompressedMod1500PlusMaxByte100:
    def test_text_returns_39490(self):
        assert zst_file_size_mod_109_times_500_plus_decompressed_size_mod_1500_plus_max_byte_value_times_100(TEXT) == 39490

    def test_minimal_returns_5001(self):
        assert zst_file_size_mod_109_times_500_plus_decompressed_size_mod_1500_plus_max_byte_value_times_100(MINIMAL) == 5001

    def test_random_returns_55524(self):
        assert zst_file_size_mod_109_times_500_plus_decompressed_size_mod_1500_plus_max_byte_value_times_100(RANDOM) == 55524

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_109_times_500_plus_decompressed_size_mod_1500_plus_max_byte_value_times_100(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_file_size_mod_109_times_500_plus_decompressed_size_mod_1500_plus_max_byte_value_times_100(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_file_size_mod_109_times_500_plus_decompressed_size_mod_1500_plus_max_byte_value_times_100(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_109_times_500_plus_decompressed_size_mod_1500_plus_max_byte_value_times_100(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_file_size_mod_109_times_500_plus_decompressed_size_mod_1500_plus_max_byte_value_times_100(MINIMAL) >= 0

    def test_random_greater_than_text(self):
        assert (zst_file_size_mod_109_times_500_plus_decompressed_size_mod_1500_plus_max_byte_value_times_100(RANDOM) >
                zst_file_size_mod_109_times_500_plus_decompressed_size_mod_1500_plus_max_byte_value_times_100(TEXT))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_109_times_500_plus_decompressed_size_mod_1500_plus_max_byte_value_times_100(str(TEXT)) == 39490


# --- F2: zst_compressed_size_mod_113_times_450_plus_decompressed_size_mod_1600_plus_min_byte_value_times_900 ---

class TestZstCompressedSizeMod113Times450PlusDecompressedMod1600PlusMinByte900:
    def test_text_returns_49890(self):
        assert zst_compressed_size_mod_113_times_450_plus_decompressed_size_mod_1600_plus_min_byte_value_times_900(TEXT) == 49890

    def test_minimal_returns_4501(self):
        assert zst_compressed_size_mod_113_times_450_plus_decompressed_size_mod_1600_plus_min_byte_value_times_900(MINIMAL) == 4501

    def test_random_returns_23524(self):
        assert zst_compressed_size_mod_113_times_450_plus_decompressed_size_mod_1600_plus_min_byte_value_times_900(RANDOM) == 23524

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_113_times_450_plus_decompressed_size_mod_1600_plus_min_byte_value_times_900(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_compressed_size_mod_113_times_450_plus_decompressed_size_mod_1600_plus_min_byte_value_times_900(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_compressed_size_mod_113_times_450_plus_decompressed_size_mod_1600_plus_min_byte_value_times_900(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_113_times_450_plus_decompressed_size_mod_1600_plus_min_byte_value_times_900(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_compressed_size_mod_113_times_450_plus_decompressed_size_mod_1600_plus_min_byte_value_times_900(MINIMAL) >= 0

    def test_text_greater_than_random(self):
        assert (zst_compressed_size_mod_113_times_450_plus_decompressed_size_mod_1600_plus_min_byte_value_times_900(TEXT) >
                zst_compressed_size_mod_113_times_450_plus_decompressed_size_mod_1600_plus_min_byte_value_times_900(RANDOM))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_113_times_450_plus_decompressed_size_mod_1600_plus_min_byte_value_times_900(str(TEXT)) == 49890
