"""Sprint 323 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINIMAL = _ZST / "minimal-synthetic.zst"
RANDOM = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_271_times_1100_plus_decompressed_size_mod_3800_plus_max_byte_value_times_220,
    zst_compressed_size_mod_277_times_1025_plus_decompressed_size_mod_3900_plus_min_byte_value_times_1900,
)


# --- F1: zst_file_size_mod_271_times_1100_plus_decompressed_size_mod_3800_plus_max_byte_value_times_220 ---

class TestZstFileSizeMod271Times1100PlusDecomp3800PlusMax220:
    def test_text_returns_28110(self):
        assert zst_file_size_mod_271_times_1100_plus_decompressed_size_mod_3800_plus_max_byte_value_times_220(TEXT) == 28110

    def test_minimal_returns_11001(self):
        assert zst_file_size_mod_271_times_1100_plus_decompressed_size_mod_3800_plus_max_byte_value_times_220(MINIMAL) == 11001

    def test_random_returns_62624(self):
        assert zst_file_size_mod_271_times_1100_plus_decompressed_size_mod_3800_plus_max_byte_value_times_220(RANDOM) == 62624

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_271_times_1100_plus_decompressed_size_mod_3800_plus_max_byte_value_times_220(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_file_size_mod_271_times_1100_plus_decompressed_size_mod_3800_plus_max_byte_value_times_220(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_file_size_mod_271_times_1100_plus_decompressed_size_mod_3800_plus_max_byte_value_times_220(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_271_times_1100_plus_decompressed_size_mod_3800_plus_max_byte_value_times_220(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_file_size_mod_271_times_1100_plus_decompressed_size_mod_3800_plus_max_byte_value_times_220(MINIMAL) >= 0

    def test_random_greater_than_minimal(self):
        assert (zst_file_size_mod_271_times_1100_plus_decompressed_size_mod_3800_plus_max_byte_value_times_220(RANDOM) >
                zst_file_size_mod_271_times_1100_plus_decompressed_size_mod_3800_plus_max_byte_value_times_220(MINIMAL))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_271_times_1100_plus_decompressed_size_mod_3800_plus_max_byte_value_times_220(str(TEXT)) == 28110


# --- F2: zst_compressed_size_mod_277_times_1025_plus_decompressed_size_mod_3900_plus_min_byte_value_times_1900 ---

class TestZstCompressedSizeMod277Times1025PlusDecomp3900PlusMin1900:
    def test_text_returns_339990(self):
        assert zst_compressed_size_mod_277_times_1025_plus_decompressed_size_mod_3900_plus_min_byte_value_times_1900(TEXT) == 339990

    def test_minimal_returns_10251(self):
        assert zst_compressed_size_mod_277_times_1025_plus_decompressed_size_mod_3900_plus_min_byte_value_times_1900(MINIMAL) == 10251

    def test_random_returns_283924(self):
        assert zst_compressed_size_mod_277_times_1025_plus_decompressed_size_mod_3900_plus_min_byte_value_times_1900(RANDOM) == 283924

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_277_times_1025_plus_decompressed_size_mod_3900_plus_min_byte_value_times_1900(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_compressed_size_mod_277_times_1025_plus_decompressed_size_mod_3900_plus_min_byte_value_times_1900(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_compressed_size_mod_277_times_1025_plus_decompressed_size_mod_3900_plus_min_byte_value_times_1900(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_277_times_1025_plus_decompressed_size_mod_3900_plus_min_byte_value_times_1900(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_compressed_size_mod_277_times_1025_plus_decompressed_size_mod_3900_plus_min_byte_value_times_1900(MINIMAL) >= 0

    def test_text_greater_than_minimal(self):
        assert (zst_compressed_size_mod_277_times_1025_plus_decompressed_size_mod_3900_plus_min_byte_value_times_1900(TEXT) >
                zst_compressed_size_mod_277_times_1025_plus_decompressed_size_mod_3900_plus_min_byte_value_times_1900(MINIMAL))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_277_times_1025_plus_decompressed_size_mod_3900_plus_min_byte_value_times_1900(str(TEXT)) == 339990
