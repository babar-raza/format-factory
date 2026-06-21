"""Sprint 338 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINIMAL = _ZST / "minimal-synthetic.zst"
RANDOM = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_347_times_1350_plus_decompressed_size_mod_4800_plus_max_byte_value_times_270,
    zst_compressed_size_mod_349_times_1275_plus_decompressed_size_mod_4900_plus_min_byte_value_times_2150,
)


# --- F1: zst_file_size_mod_347_times_1350_plus_decompressed_size_mod_4800_plus_max_byte_value_times_270 ---

class TestZstFileSizeMod347Times1350PlusDecomp4800PlusMax270:
    def test_text_returns_400260(self):
        assert zst_file_size_mod_347_times_1350_plus_decompressed_size_mod_4800_plus_max_byte_value_times_270(TEXT) == 400260

    def test_minimal_returns_13501(self):
        assert zst_file_size_mod_347_times_1350_plus_decompressed_size_mod_4800_plus_max_byte_value_times_270(MINIMAL) == 13501

    def test_random_returns_442474(self):
        assert zst_file_size_mod_347_times_1350_plus_decompressed_size_mod_4800_plus_max_byte_value_times_270(RANDOM) == 442474

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_347_times_1350_plus_decompressed_size_mod_4800_plus_max_byte_value_times_270(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_file_size_mod_347_times_1350_plus_decompressed_size_mod_4800_plus_max_byte_value_times_270(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_file_size_mod_347_times_1350_plus_decompressed_size_mod_4800_plus_max_byte_value_times_270(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_347_times_1350_plus_decompressed_size_mod_4800_plus_max_byte_value_times_270(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_file_size_mod_347_times_1350_plus_decompressed_size_mod_4800_plus_max_byte_value_times_270(MINIMAL) >= 0

    def test_random_greater_than_text(self):
        assert (zst_file_size_mod_347_times_1350_plus_decompressed_size_mod_4800_plus_max_byte_value_times_270(RANDOM) >
                zst_file_size_mod_347_times_1350_plus_decompressed_size_mod_4800_plus_max_byte_value_times_270(TEXT))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_347_times_1350_plus_decompressed_size_mod_4800_plus_max_byte_value_times_270(str(TEXT)) == 400260


# --- F2: zst_compressed_size_mod_349_times_1275_plus_decompressed_size_mod_4900_plus_min_byte_value_times_2150 ---

class TestZstCompressedSizeMod349Times1275PlusDecomp4900PlusMin2150:
    def test_text_returns_415990(self):
        assert zst_compressed_size_mod_349_times_1275_plus_decompressed_size_mod_4900_plus_min_byte_value_times_2150(TEXT) == 415990

    def test_minimal_returns_12751(self):
        assert zst_compressed_size_mod_349_times_1275_plus_decompressed_size_mod_4900_plus_min_byte_value_times_2150(MINIMAL) == 12751

    def test_random_returns_352924(self):
        assert zst_compressed_size_mod_349_times_1275_plus_decompressed_size_mod_4900_plus_min_byte_value_times_2150(RANDOM) == 352924

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_349_times_1275_plus_decompressed_size_mod_4900_plus_min_byte_value_times_2150(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_compressed_size_mod_349_times_1275_plus_decompressed_size_mod_4900_plus_min_byte_value_times_2150(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_compressed_size_mod_349_times_1275_plus_decompressed_size_mod_4900_plus_min_byte_value_times_2150(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_349_times_1275_plus_decompressed_size_mod_4900_plus_min_byte_value_times_2150(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_compressed_size_mod_349_times_1275_plus_decompressed_size_mod_4900_plus_min_byte_value_times_2150(MINIMAL) >= 0

    def test_text_greater_than_minimal(self):
        assert (zst_compressed_size_mod_349_times_1275_plus_decompressed_size_mod_4900_plus_min_byte_value_times_2150(TEXT) >
                zst_compressed_size_mod_349_times_1275_plus_decompressed_size_mod_4900_plus_min_byte_value_times_2150(MINIMAL))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_349_times_1275_plus_decompressed_size_mod_4900_plus_min_byte_value_times_2150(str(TEXT)) == 415990
