"""Sprint 302 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINIMAL = _ZST / "minimal-synthetic.zst"
RANDOM = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_167_times_750_plus_decompressed_size_mod_2500_plus_max_byte_value_times_160,
    zst_compressed_size_mod_173_times_700_plus_decompressed_size_mod_2600_plus_min_byte_value_times_1400,
)


# --- F1: zst_file_size_mod_167_times_750_plus_decompressed_size_mod_2500_plus_max_byte_value_times_160 ---

class TestZstFileSizeMod167Times750PlusDecompressedMod2500PlusMaxByte160:
    def test_text_returns_98500(self):
        assert zst_file_size_mod_167_times_750_plus_decompressed_size_mod_2500_plus_max_byte_value_times_160(TEXT) == 98500

    def test_minimal_returns_7501(self):
        assert zst_file_size_mod_167_times_750_plus_decompressed_size_mod_2500_plus_max_byte_value_times_160(MINIMAL) == 7501

    def test_random_returns_123574(self):
        assert zst_file_size_mod_167_times_750_plus_decompressed_size_mod_2500_plus_max_byte_value_times_160(RANDOM) == 123574

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_167_times_750_plus_decompressed_size_mod_2500_plus_max_byte_value_times_160(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_file_size_mod_167_times_750_plus_decompressed_size_mod_2500_plus_max_byte_value_times_160(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_file_size_mod_167_times_750_plus_decompressed_size_mod_2500_plus_max_byte_value_times_160(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_167_times_750_plus_decompressed_size_mod_2500_plus_max_byte_value_times_160(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_file_size_mod_167_times_750_plus_decompressed_size_mod_2500_plus_max_byte_value_times_160(MINIMAL) >= 0

    def test_random_greater_than_text(self):
        assert (zst_file_size_mod_167_times_750_plus_decompressed_size_mod_2500_plus_max_byte_value_times_160(RANDOM) >
                zst_file_size_mod_167_times_750_plus_decompressed_size_mod_2500_plus_max_byte_value_times_160(TEXT))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_167_times_750_plus_decompressed_size_mod_2500_plus_max_byte_value_times_160(str(TEXT)) == 98500


# --- F2: zst_compressed_size_mod_173_times_700_plus_decompressed_size_mod_2600_plus_min_byte_value_times_1400 ---

class TestZstCompressedSizeMod173Times700PlusDecompressedMod2600PlusMinByte1400:
    def test_text_returns_114490(self):
        assert zst_compressed_size_mod_173_times_700_plus_decompressed_size_mod_2600_plus_min_byte_value_times_1400(TEXT) == 114490

    def test_minimal_returns_7001(self):
        assert zst_compressed_size_mod_173_times_700_plus_decompressed_size_mod_2600_plus_min_byte_value_times_1400(MINIMAL) == 7001

    def test_random_returns_73124(self):
        assert zst_compressed_size_mod_173_times_700_plus_decompressed_size_mod_2600_plus_min_byte_value_times_1400(RANDOM) == 73124

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_173_times_700_plus_decompressed_size_mod_2600_plus_min_byte_value_times_1400(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_compressed_size_mod_173_times_700_plus_decompressed_size_mod_2600_plus_min_byte_value_times_1400(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_compressed_size_mod_173_times_700_plus_decompressed_size_mod_2600_plus_min_byte_value_times_1400(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_173_times_700_plus_decompressed_size_mod_2600_plus_min_byte_value_times_1400(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_compressed_size_mod_173_times_700_plus_decompressed_size_mod_2600_plus_min_byte_value_times_1400(MINIMAL) >= 0

    def test_text_greater_than_random(self):
        assert (zst_compressed_size_mod_173_times_700_plus_decompressed_size_mod_2600_plus_min_byte_value_times_1400(TEXT) >
                zst_compressed_size_mod_173_times_700_plus_decompressed_size_mod_2600_plus_min_byte_value_times_1400(RANDOM))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_173_times_700_plus_decompressed_size_mod_2600_plus_min_byte_value_times_1400(str(TEXT)) == 114490
