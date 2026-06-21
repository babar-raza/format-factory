"""Sprint 278 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINIMAL = _ZST / "minimal-synthetic.zst"
RANDOM = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_83_times_500_plus_decompressed_size_mod_900_plus_max_byte_value_times_70,
    zst_compressed_size_mod_89_times_300_plus_decompressed_size_mod_1000_plus_min_byte_value_times_600,
)


# --- F1: zst_file_size_mod_83_times_500_plus_decompressed_size_mod_900_plus_max_byte_value_times_70 ---

class TestZstFileSizeMod83Times500PlusDecompressedMod900PlusMaxByte70:
    def test_text_returns_20360(self):
        assert zst_file_size_mod_83_times_500_plus_decompressed_size_mod_900_plus_max_byte_value_times_70(TEXT) == 20360

    def test_minimal_returns_5001(self):
        assert zst_file_size_mod_83_times_500_plus_decompressed_size_mod_900_plus_max_byte_value_times_70(MINIMAL) == 5001

    def test_random_returns_31474(self):
        assert zst_file_size_mod_83_times_500_plus_decompressed_size_mod_900_plus_max_byte_value_times_70(RANDOM) == 31474

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_83_times_500_plus_decompressed_size_mod_900_plus_max_byte_value_times_70(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_file_size_mod_83_times_500_plus_decompressed_size_mod_900_plus_max_byte_value_times_70(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_file_size_mod_83_times_500_plus_decompressed_size_mod_900_plus_max_byte_value_times_70(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_83_times_500_plus_decompressed_size_mod_900_plus_max_byte_value_times_70(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_file_size_mod_83_times_500_plus_decompressed_size_mod_900_plus_max_byte_value_times_70(MINIMAL) >= 0

    def test_random_greater_than_text(self):
        assert (zst_file_size_mod_83_times_500_plus_decompressed_size_mod_900_plus_max_byte_value_times_70(RANDOM) >
                zst_file_size_mod_83_times_500_plus_decompressed_size_mod_900_plus_max_byte_value_times_70(TEXT))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_83_times_500_plus_decompressed_size_mod_900_plus_max_byte_value_times_70(str(TEXT)) == 20360


# --- F2: zst_compressed_size_mod_89_times_300_plus_decompressed_size_mod_1000_plus_min_byte_value_times_600 ---

class TestZstCompressedSizeMod89Times300PlusDecompressedMod1000PlusMinByte600:
    def test_text_returns_21090(self):
        assert zst_compressed_size_mod_89_times_300_plus_decompressed_size_mod_1000_plus_min_byte_value_times_600(TEXT) == 21090

    def test_minimal_returns_3001(self):
        assert zst_compressed_size_mod_89_times_300_plus_decompressed_size_mod_1000_plus_min_byte_value_times_600(MINIMAL) == 3001

    def test_random_returns_2724(self):
        assert zst_compressed_size_mod_89_times_300_plus_decompressed_size_mod_1000_plus_min_byte_value_times_600(RANDOM) == 2724

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_89_times_300_plus_decompressed_size_mod_1000_plus_min_byte_value_times_600(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_compressed_size_mod_89_times_300_plus_decompressed_size_mod_1000_plus_min_byte_value_times_600(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_compressed_size_mod_89_times_300_plus_decompressed_size_mod_1000_plus_min_byte_value_times_600(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_89_times_300_plus_decompressed_size_mod_1000_plus_min_byte_value_times_600(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_compressed_size_mod_89_times_300_plus_decompressed_size_mod_1000_plus_min_byte_value_times_600(MINIMAL) >= 0

    def test_text_greater_than_random(self):
        assert (zst_compressed_size_mod_89_times_300_plus_decompressed_size_mod_1000_plus_min_byte_value_times_600(TEXT) >
                zst_compressed_size_mod_89_times_300_plus_decompressed_size_mod_1000_plus_min_byte_value_times_600(RANDOM))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_89_times_300_plus_decompressed_size_mod_1000_plus_min_byte_value_times_600(str(TEXT)) == 21090
