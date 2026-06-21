"""Sprint 326 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINIMAL = _ZST / "minimal-synthetic.zst"
RANDOM = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_283_times_1150_plus_decompressed_size_mod_4000_plus_max_byte_value_times_230,
    zst_compressed_size_mod_293_times_1075_plus_decompressed_size_mod_4100_plus_min_byte_value_times_1950,
)


# --- F1: zst_file_size_mod_283_times_1150_plus_decompressed_size_mod_4000_plus_max_byte_value_times_230 ---

class TestZstFileSizeMod283Times1150PlusDecomp4000PlusMax230:
    def test_text_returns_341020(self):
        assert zst_file_size_mod_283_times_1150_plus_decompressed_size_mod_4000_plus_max_byte_value_times_230(TEXT) == 341020

    def test_minimal_returns_11501(self):
        assert zst_file_size_mod_283_times_1150_plus_decompressed_size_mod_4000_plus_max_byte_value_times_230(MINIMAL) == 11501

    def test_random_returns_377074(self):
        assert zst_file_size_mod_283_times_1150_plus_decompressed_size_mod_4000_plus_max_byte_value_times_230(RANDOM) == 377074

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_283_times_1150_plus_decompressed_size_mod_4000_plus_max_byte_value_times_230(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_file_size_mod_283_times_1150_plus_decompressed_size_mod_4000_plus_max_byte_value_times_230(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_file_size_mod_283_times_1150_plus_decompressed_size_mod_4000_plus_max_byte_value_times_230(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_283_times_1150_plus_decompressed_size_mod_4000_plus_max_byte_value_times_230(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_file_size_mod_283_times_1150_plus_decompressed_size_mod_4000_plus_max_byte_value_times_230(MINIMAL) >= 0

    def test_random_greater_than_text(self):
        assert (zst_file_size_mod_283_times_1150_plus_decompressed_size_mod_4000_plus_max_byte_value_times_230(RANDOM) >
                zst_file_size_mod_283_times_1150_plus_decompressed_size_mod_4000_plus_max_byte_value_times_230(TEXT))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_283_times_1150_plus_decompressed_size_mod_4000_plus_max_byte_value_times_230(str(TEXT)) == 341020


# --- F2: zst_compressed_size_mod_293_times_1075_plus_decompressed_size_mod_4100_plus_min_byte_value_times_1950 ---

class TestZstCompressedSizeMod293Times1075PlusDecomp4100PlusMin1950:
    def test_text_returns_355190(self):
        assert zst_compressed_size_mod_293_times_1075_plus_decompressed_size_mod_4100_plus_min_byte_value_times_1950(TEXT) == 355190

    def test_minimal_returns_10751(self):
        assert zst_compressed_size_mod_293_times_1075_plus_decompressed_size_mod_4100_plus_min_byte_value_times_1950(MINIMAL) == 10751

    def test_random_returns_297724(self):
        assert zst_compressed_size_mod_293_times_1075_plus_decompressed_size_mod_4100_plus_min_byte_value_times_1950(RANDOM) == 297724

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_293_times_1075_plus_decompressed_size_mod_4100_plus_min_byte_value_times_1950(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_compressed_size_mod_293_times_1075_plus_decompressed_size_mod_4100_plus_min_byte_value_times_1950(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_compressed_size_mod_293_times_1075_plus_decompressed_size_mod_4100_plus_min_byte_value_times_1950(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_293_times_1075_plus_decompressed_size_mod_4100_plus_min_byte_value_times_1950(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_compressed_size_mod_293_times_1075_plus_decompressed_size_mod_4100_plus_min_byte_value_times_1950(MINIMAL) >= 0

    def test_text_greater_than_minimal(self):
        assert (zst_compressed_size_mod_293_times_1075_plus_decompressed_size_mod_4100_plus_min_byte_value_times_1950(TEXT) >
                zst_compressed_size_mod_293_times_1075_plus_decompressed_size_mod_4100_plus_min_byte_value_times_1950(MINIMAL))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_293_times_1075_plus_decompressed_size_mod_4100_plus_min_byte_value_times_1950(str(TEXT)) == 355190
