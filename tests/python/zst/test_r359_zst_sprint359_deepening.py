"""Sprint 359 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINI = _ZST / "minimal-synthetic.zst"
RAND = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_431_times_1700_plus_decompressed_size_mod_6200_plus_max_byte_value_times_340,
    zst_compressed_size_mod_433_times_1625_plus_decompressed_size_mod_6300_plus_min_byte_value_times_2500,
)


# --- F1: zst_file_size_mod_431_times_1700_plus_decompressed_size_mod_6200_plus_max_byte_value_times_340 ---

class TestZstFileSizeMod431Times1700PlusDecompressed6200PlusMaxByte340:
    def test_text_returns_503930(self):
        assert zst_file_size_mod_431_times_1700_plus_decompressed_size_mod_6200_plus_max_byte_value_times_340(TEXT) == 503930

    def test_mini_returns_17001(self):
        assert zst_file_size_mod_431_times_1700_plus_decompressed_size_mod_6200_plus_max_byte_value_times_340(MINI) == 17001

    def test_rand_returns_556924(self):
        assert zst_file_size_mod_431_times_1700_plus_decompressed_size_mod_6200_plus_max_byte_value_times_340(RAND) == 556924

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_431_times_1700_plus_decompressed_size_mod_6200_plus_max_byte_value_times_340(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_file_size_mod_431_times_1700_plus_decompressed_size_mod_6200_plus_max_byte_value_times_340(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_file_size_mod_431_times_1700_plus_decompressed_size_mod_6200_plus_max_byte_value_times_340(RAND), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_431_times_1700_plus_decompressed_size_mod_6200_plus_max_byte_value_times_340(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_file_size_mod_431_times_1700_plus_decompressed_size_mod_6200_plus_max_byte_value_times_340(MINI) >= 0

    def test_rand_greater_than_mini(self):
        assert (zst_file_size_mod_431_times_1700_plus_decompressed_size_mod_6200_plus_max_byte_value_times_340(RAND) >
                zst_file_size_mod_431_times_1700_plus_decompressed_size_mod_6200_plus_max_byte_value_times_340(MINI))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_431_times_1700_plus_decompressed_size_mod_6200_plus_max_byte_value_times_340(str(TEXT)) == 503930


# --- F2: zst_compressed_size_mod_433_times_1625_plus_decompressed_size_mod_6300_plus_min_byte_value_times_2500 ---

class TestZstCompressedSizeMod433Times1625PlusDecompressed6300PlusMinByte2500:
    def test_text_returns_522390(self):
        assert zst_compressed_size_mod_433_times_1625_plus_decompressed_size_mod_6300_plus_min_byte_value_times_2500(TEXT) == 522390

    def test_mini_returns_16251(self):
        assert zst_compressed_size_mod_433_times_1625_plus_decompressed_size_mod_6300_plus_min_byte_value_times_2500(MINI) == 16251

    def test_rand_returns_449524(self):
        assert zst_compressed_size_mod_433_times_1625_plus_decompressed_size_mod_6300_plus_min_byte_value_times_2500(RAND) == 449524

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_433_times_1625_plus_decompressed_size_mod_6300_plus_min_byte_value_times_2500(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_compressed_size_mod_433_times_1625_plus_decompressed_size_mod_6300_plus_min_byte_value_times_2500(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_compressed_size_mod_433_times_1625_plus_decompressed_size_mod_6300_plus_min_byte_value_times_2500(RAND), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_433_times_1625_plus_decompressed_size_mod_6300_plus_min_byte_value_times_2500(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_compressed_size_mod_433_times_1625_plus_decompressed_size_mod_6300_plus_min_byte_value_times_2500(MINI) >= 0

    def test_rand_greater_than_mini(self):
        assert (zst_compressed_size_mod_433_times_1625_plus_decompressed_size_mod_6300_plus_min_byte_value_times_2500(RAND) >
                zst_compressed_size_mod_433_times_1625_plus_decompressed_size_mod_6300_plus_min_byte_value_times_2500(MINI))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_433_times_1625_plus_decompressed_size_mod_6300_plus_min_byte_value_times_2500(str(TEXT)) == 522390
