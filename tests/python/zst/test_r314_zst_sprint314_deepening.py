"""Sprint 314 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINIMAL = _ZST / "minimal-synthetic.zst"
RANDOM = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_229_times_950_plus_decompressed_size_mod_3300_plus_max_byte_value_times_195,
    zst_compressed_size_mod_233_times_875_plus_decompressed_size_mod_3400_plus_min_byte_value_times_1750,
)


# --- F1: zst_file_size_mod_229_times_950_plus_decompressed_size_mod_3300_plus_max_byte_value_times_195 ---

class TestZstFileSizeMod229Times950PlusDecompressedMod3300PlusMaxByte195:
    def test_text_returns_64835(self):
        assert zst_file_size_mod_229_times_950_plus_decompressed_size_mod_3300_plus_max_byte_value_times_195(TEXT) == 64835

    def test_minimal_returns_9501(self):
        assert zst_file_size_mod_229_times_950_plus_decompressed_size_mod_3300_plus_max_byte_value_times_195(MINIMAL) == 9501

    def test_random_returns_95399(self):
        assert zst_file_size_mod_229_times_950_plus_decompressed_size_mod_3300_plus_max_byte_value_times_195(RANDOM) == 95399

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_229_times_950_plus_decompressed_size_mod_3300_plus_max_byte_value_times_195(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_file_size_mod_229_times_950_plus_decompressed_size_mod_3300_plus_max_byte_value_times_195(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_file_size_mod_229_times_950_plus_decompressed_size_mod_3300_plus_max_byte_value_times_195(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_229_times_950_plus_decompressed_size_mod_3300_plus_max_byte_value_times_195(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_file_size_mod_229_times_950_plus_decompressed_size_mod_3300_plus_max_byte_value_times_195(MINIMAL) >= 0

    def test_random_greater_than_text(self):
        assert (zst_file_size_mod_229_times_950_plus_decompressed_size_mod_3300_plus_max_byte_value_times_195(RANDOM) >
                zst_file_size_mod_229_times_950_plus_decompressed_size_mod_3300_plus_max_byte_value_times_195(TEXT))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_229_times_950_plus_decompressed_size_mod_3300_plus_max_byte_value_times_195(str(TEXT)) == 64835


# --- F2: zst_compressed_size_mod_233_times_875_plus_decompressed_size_mod_3400_plus_min_byte_value_times_1750 ---

class TestZstCompressedSizeMod233Times875PlusDecompressedMod3400PlusMinByte1750:
    def test_text_returns_90515(self):
        assert zst_compressed_size_mod_233_times_875_plus_decompressed_size_mod_3400_plus_min_byte_value_times_1750(TEXT) == 90515

    def test_minimal_returns_8751(self):
        assert zst_compressed_size_mod_233_times_875_plus_decompressed_size_mod_3400_plus_min_byte_value_times_1750(MINIMAL) == 8751

    def test_random_returns_38649(self):
        assert zst_compressed_size_mod_233_times_875_plus_decompressed_size_mod_3400_plus_min_byte_value_times_1750(RANDOM) == 38649

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_233_times_875_plus_decompressed_size_mod_3400_plus_min_byte_value_times_1750(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_compressed_size_mod_233_times_875_plus_decompressed_size_mod_3400_plus_min_byte_value_times_1750(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_compressed_size_mod_233_times_875_plus_decompressed_size_mod_3400_plus_min_byte_value_times_1750(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_233_times_875_plus_decompressed_size_mod_3400_plus_min_byte_value_times_1750(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_compressed_size_mod_233_times_875_plus_decompressed_size_mod_3400_plus_min_byte_value_times_1750(MINIMAL) >= 0

    def test_text_greater_than_random(self):
        assert (zst_compressed_size_mod_233_times_875_plus_decompressed_size_mod_3400_plus_min_byte_value_times_1750(TEXT) >
                zst_compressed_size_mod_233_times_875_plus_decompressed_size_mod_3400_plus_min_byte_value_times_1750(RANDOM))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_233_times_875_plus_decompressed_size_mod_3400_plus_min_byte_value_times_1750(str(TEXT)) == 90515
