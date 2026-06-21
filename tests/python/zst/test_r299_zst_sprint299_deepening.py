"""Sprint 299 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINIMAL = _ZST / "minimal-synthetic.zst"
RANDOM = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_157_times_700_plus_decompressed_size_mod_2300_plus_max_byte_value_times_150,
    zst_compressed_size_mod_163_times_650_plus_decompressed_size_mod_2400_plus_min_byte_value_times_1300,
)


# --- F1: zst_file_size_mod_157_times_700_plus_decompressed_size_mod_2300_plus_max_byte_value_times_150 ---

class TestZstFileSizeMod157Times700PlusDecompressedMod2300PlusMaxByte150:
    def test_text_returns_99040(self):
        assert zst_file_size_mod_157_times_700_plus_decompressed_size_mod_2300_plus_max_byte_value_times_150(TEXT) == 99040

    def test_minimal_returns_7001(self):
        assert zst_file_size_mod_157_times_700_plus_decompressed_size_mod_2300_plus_max_byte_value_times_150(MINIMAL) == 7001

    def test_random_returns_122574(self):
        assert zst_file_size_mod_157_times_700_plus_decompressed_size_mod_2300_plus_max_byte_value_times_150(RANDOM) == 122574

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_157_times_700_plus_decompressed_size_mod_2300_plus_max_byte_value_times_150(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_file_size_mod_157_times_700_plus_decompressed_size_mod_2300_plus_max_byte_value_times_150(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_file_size_mod_157_times_700_plus_decompressed_size_mod_2300_plus_max_byte_value_times_150(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_157_times_700_plus_decompressed_size_mod_2300_plus_max_byte_value_times_150(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_file_size_mod_157_times_700_plus_decompressed_size_mod_2300_plus_max_byte_value_times_150(MINIMAL) >= 0

    def test_random_greater_than_text(self):
        assert (zst_file_size_mod_157_times_700_plus_decompressed_size_mod_2300_plus_max_byte_value_times_150(RANDOM) >
                zst_file_size_mod_157_times_700_plus_decompressed_size_mod_2300_plus_max_byte_value_times_150(TEXT))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_157_times_700_plus_decompressed_size_mod_2300_plus_max_byte_value_times_150(str(TEXT)) == 99040


# --- F2: zst_compressed_size_mod_163_times_650_plus_decompressed_size_mod_2400_plus_min_byte_value_times_1300 ---

class TestZstCompressedSizeMod163Times650PlusDecompressedMod2400PlusMinByte1300:
    def test_text_returns_112840(self):
        assert zst_compressed_size_mod_163_times_650_plus_decompressed_size_mod_2400_plus_min_byte_value_times_1300(TEXT) == 112840

    def test_minimal_returns_6501(self):
        assert zst_compressed_size_mod_163_times_650_plus_decompressed_size_mod_2400_plus_min_byte_value_times_1300(MINIMAL) == 6501

    def test_random_returns_74474(self):
        assert zst_compressed_size_mod_163_times_650_plus_decompressed_size_mod_2400_plus_min_byte_value_times_1300(RANDOM) == 74474

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_163_times_650_plus_decompressed_size_mod_2400_plus_min_byte_value_times_1300(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_compressed_size_mod_163_times_650_plus_decompressed_size_mod_2400_plus_min_byte_value_times_1300(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_compressed_size_mod_163_times_650_plus_decompressed_size_mod_2400_plus_min_byte_value_times_1300(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_163_times_650_plus_decompressed_size_mod_2400_plus_min_byte_value_times_1300(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_compressed_size_mod_163_times_650_plus_decompressed_size_mod_2400_plus_min_byte_value_times_1300(MINIMAL) >= 0

    def test_text_greater_than_random(self):
        assert (zst_compressed_size_mod_163_times_650_plus_decompressed_size_mod_2400_plus_min_byte_value_times_1300(TEXT) >
                zst_compressed_size_mod_163_times_650_plus_decompressed_size_mod_2400_plus_min_byte_value_times_1300(RANDOM))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_163_times_650_plus_decompressed_size_mod_2400_plus_min_byte_value_times_1300(str(TEXT)) == 112840
