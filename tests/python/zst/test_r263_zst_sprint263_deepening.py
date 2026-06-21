"""Sprint 263 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINIMAL = _ZST / "minimal-synthetic.zst"
RANDOM = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_43_times_100_plus_decompressed_size_mod_500_plus_max_byte_value_times_30,
    zst_compressed_size_mod_37_times_150_plus_decompressed_size_mod_300_plus_min_byte_value_times_50,
)


# --- F1: zst_file_size_mod_43_times_100_plus_decompressed_size_mod_500_plus_max_byte_value_times_30 ---

class TestZstFileSizeMod43Times100PlusDecompressedMod500PlusMaxByte30:
    def test_text_returns_5420(self):
        assert zst_file_size_mod_43_times_100_plus_decompressed_size_mod_500_plus_max_byte_value_times_30(TEXT) == 5420

    def test_minimal_returns_1001(self):
        assert zst_file_size_mod_43_times_100_plus_decompressed_size_mod_500_plus_max_byte_value_times_30(MINIMAL) == 1001

    def test_random_returns_9474(self):
        assert zst_file_size_mod_43_times_100_plus_decompressed_size_mod_500_plus_max_byte_value_times_30(RANDOM) == 9474

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_43_times_100_plus_decompressed_size_mod_500_plus_max_byte_value_times_30(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_file_size_mod_43_times_100_plus_decompressed_size_mod_500_plus_max_byte_value_times_30(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_file_size_mod_43_times_100_plus_decompressed_size_mod_500_plus_max_byte_value_times_30(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_43_times_100_plus_decompressed_size_mod_500_plus_max_byte_value_times_30(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_file_size_mod_43_times_100_plus_decompressed_size_mod_500_plus_max_byte_value_times_30(MINIMAL) >= 0

    def test_random_greater_than_text(self):
        assert (zst_file_size_mod_43_times_100_plus_decompressed_size_mod_500_plus_max_byte_value_times_30(RANDOM) >
                zst_file_size_mod_43_times_100_plus_decompressed_size_mod_500_plus_max_byte_value_times_30(TEXT))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_43_times_100_plus_decompressed_size_mod_500_plus_max_byte_value_times_30(str(TEXT)) == 5420


# --- F2: zst_compressed_size_mod_37_times_150_plus_decompressed_size_mod_300_plus_min_byte_value_times_50 ---

class TestZstCompressedSizeMod37Times150PlusDecompressedMod300PlusMinByte50:
    def test_text_returns_3640(self):
        assert zst_compressed_size_mod_37_times_150_plus_decompressed_size_mod_300_plus_min_byte_value_times_50(TEXT) == 3640

    def test_minimal_returns_1501(self):
        assert zst_compressed_size_mod_37_times_150_plus_decompressed_size_mod_300_plus_min_byte_value_times_50(MINIMAL) == 1501

    def test_random_returns_2674(self):
        assert zst_compressed_size_mod_37_times_150_plus_decompressed_size_mod_300_plus_min_byte_value_times_50(RANDOM) == 2674

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_37_times_150_plus_decompressed_size_mod_300_plus_min_byte_value_times_50(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_compressed_size_mod_37_times_150_plus_decompressed_size_mod_300_plus_min_byte_value_times_50(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_compressed_size_mod_37_times_150_plus_decompressed_size_mod_300_plus_min_byte_value_times_50(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_37_times_150_plus_decompressed_size_mod_300_plus_min_byte_value_times_50(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_compressed_size_mod_37_times_150_plus_decompressed_size_mod_300_plus_min_byte_value_times_50(MINIMAL) >= 0

    def test_text_greater_than_minimal(self):
        assert (zst_compressed_size_mod_37_times_150_plus_decompressed_size_mod_300_plus_min_byte_value_times_50(TEXT) >
                zst_compressed_size_mod_37_times_150_plus_decompressed_size_mod_300_plus_min_byte_value_times_50(MINIMAL))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_37_times_150_plus_decompressed_size_mod_300_plus_min_byte_value_times_50(str(TEXT)) == 3640
