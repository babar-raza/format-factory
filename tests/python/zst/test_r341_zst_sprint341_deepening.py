"""Sprint 341 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINIMAL = _ZST / "minimal-synthetic.zst"
RANDOM = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_353_times_1400_plus_decompressed_size_mod_5000_plus_max_byte_value_times_280,
    zst_compressed_size_mod_359_times_1325_plus_decompressed_size_mod_5100_plus_min_byte_value_times_2200,
)


# --- F1: zst_file_size_mod_353_times_1400_plus_decompressed_size_mod_5000_plus_max_byte_value_times_280 ---

class TestZstFileSizeMod353Times1400PlusDecomp5000PlusMax280:
    def test_text_returns_415070(self):
        assert zst_file_size_mod_353_times_1400_plus_decompressed_size_mod_5000_plus_max_byte_value_times_280(TEXT) == 415070

    def test_minimal_returns_14001(self):
        assert zst_file_size_mod_353_times_1400_plus_decompressed_size_mod_5000_plus_max_byte_value_times_280(MINIMAL) == 14001

    def test_random_returns_458824(self):
        assert zst_file_size_mod_353_times_1400_plus_decompressed_size_mod_5000_plus_max_byte_value_times_280(RANDOM) == 458824

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_353_times_1400_plus_decompressed_size_mod_5000_plus_max_byte_value_times_280(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_file_size_mod_353_times_1400_plus_decompressed_size_mod_5000_plus_max_byte_value_times_280(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_file_size_mod_353_times_1400_plus_decompressed_size_mod_5000_plus_max_byte_value_times_280(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_353_times_1400_plus_decompressed_size_mod_5000_plus_max_byte_value_times_280(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_file_size_mod_353_times_1400_plus_decompressed_size_mod_5000_plus_max_byte_value_times_280(MINIMAL) >= 0

    def test_random_greater_than_text(self):
        assert (zst_file_size_mod_353_times_1400_plus_decompressed_size_mod_5000_plus_max_byte_value_times_280(RANDOM) >
                zst_file_size_mod_353_times_1400_plus_decompressed_size_mod_5000_plus_max_byte_value_times_280(TEXT))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_353_times_1400_plus_decompressed_size_mod_5000_plus_max_byte_value_times_280(str(TEXT)) == 415070


# --- F2: zst_compressed_size_mod_359_times_1325_plus_decompressed_size_mod_5100_plus_min_byte_value_times_2200 ---

class TestZstCompressedSizeMod359Times1325PlusDecomp5100PlusMin2200:
    def test_text_returns_431190(self):
        assert zst_compressed_size_mod_359_times_1325_plus_decompressed_size_mod_5100_plus_min_byte_value_times_2200(TEXT) == 431190

    def test_minimal_returns_13251(self):
        assert zst_compressed_size_mod_359_times_1325_plus_decompressed_size_mod_5100_plus_min_byte_value_times_2200(MINIMAL) == 13251

    def test_random_returns_366724(self):
        assert zst_compressed_size_mod_359_times_1325_plus_decompressed_size_mod_5100_plus_min_byte_value_times_2200(RANDOM) == 366724

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_359_times_1325_plus_decompressed_size_mod_5100_plus_min_byte_value_times_2200(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_compressed_size_mod_359_times_1325_plus_decompressed_size_mod_5100_plus_min_byte_value_times_2200(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_compressed_size_mod_359_times_1325_plus_decompressed_size_mod_5100_plus_min_byte_value_times_2200(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_359_times_1325_plus_decompressed_size_mod_5100_plus_min_byte_value_times_2200(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_compressed_size_mod_359_times_1325_plus_decompressed_size_mod_5100_plus_min_byte_value_times_2200(MINIMAL) >= 0

    def test_text_greater_than_minimal(self):
        assert (zst_compressed_size_mod_359_times_1325_plus_decompressed_size_mod_5100_plus_min_byte_value_times_2200(TEXT) >
                zst_compressed_size_mod_359_times_1325_plus_decompressed_size_mod_5100_plus_min_byte_value_times_2200(MINIMAL))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_359_times_1325_plus_decompressed_size_mod_5100_plus_min_byte_value_times_2200(str(TEXT)) == 431190
