"""Sprint 281 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINIMAL = _ZST / "minimal-synthetic.zst"
RANDOM = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_97_times_600_plus_decompressed_size_mod_1100_plus_max_byte_value_times_80,
    zst_compressed_size_mod_101_times_350_plus_decompressed_size_mod_1200_plus_min_byte_value_times_700,
)


# --- F1: zst_file_size_mod_97_times_600_plus_decompressed_size_mod_1100_plus_max_byte_value_times_80 ---

class TestZstFileSizeMod97Times600PlusDecompressedMod1100PlusMaxByte80:
    def test_text_returns_56870(self):
        assert zst_file_size_mod_97_times_600_plus_decompressed_size_mod_1100_plus_max_byte_value_times_80(TEXT) == 56870

    def test_minimal_returns_6001(self):
        assert zst_file_size_mod_97_times_600_plus_decompressed_size_mod_1100_plus_max_byte_value_times_80(MINIMAL) == 6001

    def test_random_returns_70624(self):
        assert zst_file_size_mod_97_times_600_plus_decompressed_size_mod_1100_plus_max_byte_value_times_80(RANDOM) == 70624

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_97_times_600_plus_decompressed_size_mod_1100_plus_max_byte_value_times_80(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_file_size_mod_97_times_600_plus_decompressed_size_mod_1100_plus_max_byte_value_times_80(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_file_size_mod_97_times_600_plus_decompressed_size_mod_1100_plus_max_byte_value_times_80(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_97_times_600_plus_decompressed_size_mod_1100_plus_max_byte_value_times_80(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_file_size_mod_97_times_600_plus_decompressed_size_mod_1100_plus_max_byte_value_times_80(MINIMAL) >= 0

    def test_random_greater_than_text(self):
        assert (zst_file_size_mod_97_times_600_plus_decompressed_size_mod_1100_plus_max_byte_value_times_80(RANDOM) >
                zst_file_size_mod_97_times_600_plus_decompressed_size_mod_1100_plus_max_byte_value_times_80(TEXT))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_97_times_600_plus_decompressed_size_mod_1100_plus_max_byte_value_times_80(str(TEXT)) == 56870


# --- F2: zst_compressed_size_mod_101_times_350_plus_decompressed_size_mod_1200_plus_min_byte_value_times_700 ---

class TestZstCompressedSizeMod101Times350PlusDecompressedMod1200PlusMinByte700:
    def test_text_returns_47290(self):
        assert zst_compressed_size_mod_101_times_350_plus_decompressed_size_mod_1200_plus_min_byte_value_times_700(TEXT) == 47290

    def test_minimal_returns_3501(self):
        assert zst_compressed_size_mod_101_times_350_plus_decompressed_size_mod_1200_plus_min_byte_value_times_700(MINIMAL) == 3501

    def test_random_returns_26924(self):
        assert zst_compressed_size_mod_101_times_350_plus_decompressed_size_mod_1200_plus_min_byte_value_times_700(RANDOM) == 26924

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_101_times_350_plus_decompressed_size_mod_1200_plus_min_byte_value_times_700(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_compressed_size_mod_101_times_350_plus_decompressed_size_mod_1200_plus_min_byte_value_times_700(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_compressed_size_mod_101_times_350_plus_decompressed_size_mod_1200_plus_min_byte_value_times_700(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_101_times_350_plus_decompressed_size_mod_1200_plus_min_byte_value_times_700(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_compressed_size_mod_101_times_350_plus_decompressed_size_mod_1200_plus_min_byte_value_times_700(MINIMAL) >= 0

    def test_text_greater_than_random(self):
        assert (zst_compressed_size_mod_101_times_350_plus_decompressed_size_mod_1200_plus_min_byte_value_times_700(TEXT) >
                zst_compressed_size_mod_101_times_350_plus_decompressed_size_mod_1200_plus_min_byte_value_times_700(RANDOM))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_101_times_350_plus_decompressed_size_mod_1200_plus_min_byte_value_times_700(str(TEXT)) == 47290
