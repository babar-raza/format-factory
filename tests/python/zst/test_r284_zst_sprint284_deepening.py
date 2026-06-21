"""Sprint 284 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINIMAL = _ZST / "minimal-synthetic.zst"
RANDOM = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_103_times_700_plus_decompressed_size_mod_1300_plus_max_byte_value_times_90,
    zst_compressed_size_mod_107_times_400_plus_decompressed_size_mod_1400_plus_min_byte_value_times_800,
)


# --- F1: zst_file_size_mod_103_times_700_plus_decompressed_size_mod_1300_plus_max_byte_value_times_90 ---

class TestZstFileSizeMod103Times700PlusDecompressedMod1300PlusMaxByte90:
    def test_text_returns_57480(self):
        assert zst_file_size_mod_103_times_700_plus_decompressed_size_mod_1300_plus_max_byte_value_times_90(TEXT) == 57480

    def test_minimal_returns_7001(self):
        assert zst_file_size_mod_103_times_700_plus_decompressed_size_mod_1300_plus_max_byte_value_times_90(MINIMAL) == 7001

    def test_random_returns_72974(self):
        assert zst_file_size_mod_103_times_700_plus_decompressed_size_mod_1300_plus_max_byte_value_times_90(RANDOM) == 72974

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_103_times_700_plus_decompressed_size_mod_1300_plus_max_byte_value_times_90(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_file_size_mod_103_times_700_plus_decompressed_size_mod_1300_plus_max_byte_value_times_90(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_file_size_mod_103_times_700_plus_decompressed_size_mod_1300_plus_max_byte_value_times_90(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_103_times_700_plus_decompressed_size_mod_1300_plus_max_byte_value_times_90(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_file_size_mod_103_times_700_plus_decompressed_size_mod_1300_plus_max_byte_value_times_90(MINIMAL) >= 0

    def test_random_greater_than_text(self):
        assert (zst_file_size_mod_103_times_700_plus_decompressed_size_mod_1300_plus_max_byte_value_times_90(RANDOM) >
                zst_file_size_mod_103_times_700_plus_decompressed_size_mod_1300_plus_max_byte_value_times_90(TEXT))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_103_times_700_plus_decompressed_size_mod_1300_plus_max_byte_value_times_90(str(TEXT)) == 57480


# --- F2: zst_compressed_size_mod_107_times_400_plus_decompressed_size_mod_1400_plus_min_byte_value_times_800 ---

class TestZstCompressedSizeMod107Times400PlusDecompressedMod1400PlusMinByte800:
    def test_text_returns_49190(self):
        assert zst_compressed_size_mod_107_times_400_plus_decompressed_size_mod_1400_plus_min_byte_value_times_800(TEXT) == 49190

    def test_minimal_returns_4001(self):
        assert zst_compressed_size_mod_107_times_400_plus_decompressed_size_mod_1400_plus_min_byte_value_times_800(MINIMAL) == 4001

    def test_random_returns_25824(self):
        assert zst_compressed_size_mod_107_times_400_plus_decompressed_size_mod_1400_plus_min_byte_value_times_800(RANDOM) == 25824

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_107_times_400_plus_decompressed_size_mod_1400_plus_min_byte_value_times_800(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_compressed_size_mod_107_times_400_plus_decompressed_size_mod_1400_plus_min_byte_value_times_800(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_compressed_size_mod_107_times_400_plus_decompressed_size_mod_1400_plus_min_byte_value_times_800(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_107_times_400_plus_decompressed_size_mod_1400_plus_min_byte_value_times_800(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_compressed_size_mod_107_times_400_plus_decompressed_size_mod_1400_plus_min_byte_value_times_800(MINIMAL) >= 0

    def test_text_greater_than_random(self):
        assert (zst_compressed_size_mod_107_times_400_plus_decompressed_size_mod_1400_plus_min_byte_value_times_800(TEXT) >
                zst_compressed_size_mod_107_times_400_plus_decompressed_size_mod_1400_plus_min_byte_value_times_800(RANDOM))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_107_times_400_plus_decompressed_size_mod_1400_plus_min_byte_value_times_800(str(TEXT)) == 49190
