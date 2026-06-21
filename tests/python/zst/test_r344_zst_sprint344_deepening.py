"""Sprint 344 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINIMAL = _ZST / "minimal-synthetic.zst"
RANDOM = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_367_times_1450_plus_decompressed_size_mod_5200_plus_max_byte_value_times_290,
    zst_compressed_size_mod_373_times_1375_plus_decompressed_size_mod_5300_plus_min_byte_value_times_2250,
)


# --- F1: zst_file_size_mod_367_times_1450_plus_decompressed_size_mod_5200_plus_max_byte_value_times_290 ---

class TestZstFileSizeMod367Times1450PlusDecomp5200PlusMax290:
    def test_text_returns_429880(self):
        assert zst_file_size_mod_367_times_1450_plus_decompressed_size_mod_5200_plus_max_byte_value_times_290(TEXT) == 429880

    def test_minimal_returns_14501(self):
        assert zst_file_size_mod_367_times_1450_plus_decompressed_size_mod_5200_plus_max_byte_value_times_290(MINIMAL) == 14501

    def test_random_returns_475174(self):
        assert zst_file_size_mod_367_times_1450_plus_decompressed_size_mod_5200_plus_max_byte_value_times_290(RANDOM) == 475174

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_367_times_1450_plus_decompressed_size_mod_5200_plus_max_byte_value_times_290(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_file_size_mod_367_times_1450_plus_decompressed_size_mod_5200_plus_max_byte_value_times_290(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_file_size_mod_367_times_1450_plus_decompressed_size_mod_5200_plus_max_byte_value_times_290(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_367_times_1450_plus_decompressed_size_mod_5200_plus_max_byte_value_times_290(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_file_size_mod_367_times_1450_plus_decompressed_size_mod_5200_plus_max_byte_value_times_290(MINIMAL) >= 0

    def test_random_greater_than_text(self):
        assert (zst_file_size_mod_367_times_1450_plus_decompressed_size_mod_5200_plus_max_byte_value_times_290(RANDOM) >
                zst_file_size_mod_367_times_1450_plus_decompressed_size_mod_5200_plus_max_byte_value_times_290(TEXT))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_367_times_1450_plus_decompressed_size_mod_5200_plus_max_byte_value_times_290(str(TEXT)) == 429880


# --- F2: zst_compressed_size_mod_373_times_1375_plus_decompressed_size_mod_5300_plus_min_byte_value_times_2250 ---

class TestZstCompressedSizeMod373Times1375PlusDecomp5300PlusMin2250:
    def test_text_returns_446390(self):
        assert zst_compressed_size_mod_373_times_1375_plus_decompressed_size_mod_5300_plus_min_byte_value_times_2250(TEXT) == 446390

    def test_minimal_returns_13751(self):
        assert zst_compressed_size_mod_373_times_1375_plus_decompressed_size_mod_5300_plus_min_byte_value_times_2250(MINIMAL) == 13751

    def test_random_returns_380524(self):
        assert zst_compressed_size_mod_373_times_1375_plus_decompressed_size_mod_5300_plus_min_byte_value_times_2250(RANDOM) == 380524

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_373_times_1375_plus_decompressed_size_mod_5300_plus_min_byte_value_times_2250(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_compressed_size_mod_373_times_1375_plus_decompressed_size_mod_5300_plus_min_byte_value_times_2250(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_compressed_size_mod_373_times_1375_plus_decompressed_size_mod_5300_plus_min_byte_value_times_2250(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_373_times_1375_plus_decompressed_size_mod_5300_plus_min_byte_value_times_2250(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_compressed_size_mod_373_times_1375_plus_decompressed_size_mod_5300_plus_min_byte_value_times_2250(MINIMAL) >= 0

    def test_text_greater_than_minimal(self):
        assert (zst_compressed_size_mod_373_times_1375_plus_decompressed_size_mod_5300_plus_min_byte_value_times_2250(TEXT) >
                zst_compressed_size_mod_373_times_1375_plus_decompressed_size_mod_5300_plus_min_byte_value_times_2250(MINIMAL))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_373_times_1375_plus_decompressed_size_mod_5300_plus_min_byte_value_times_2250(str(TEXT)) == 446390
