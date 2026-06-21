"""Sprint 308 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINIMAL = _ZST / "minimal-synthetic.zst"
RANDOM = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_197_times_850_plus_decompressed_size_mod_2900_plus_max_byte_value_times_180,
    zst_compressed_size_mod_199_times_800_plus_decompressed_size_mod_3000_plus_min_byte_value_times_1600,
)


# --- F1: zst_file_size_mod_197_times_850_plus_decompressed_size_mod_2900_plus_max_byte_value_times_180 ---

class TestZstFileSizeMod197Times850PlusDecompressedMod2900PlusMaxByte180:
    def test_text_returns_85920(self):
        assert zst_file_size_mod_197_times_850_plus_decompressed_size_mod_2900_plus_max_byte_value_times_180(TEXT) == 85920

    def test_minimal_returns_8501(self):
        assert zst_file_size_mod_197_times_850_plus_decompressed_size_mod_2900_plus_max_byte_value_times_180(MINIMAL) == 8501

    def test_random_returns_114074(self):
        assert zst_file_size_mod_197_times_850_plus_decompressed_size_mod_2900_plus_max_byte_value_times_180(RANDOM) == 114074

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_197_times_850_plus_decompressed_size_mod_2900_plus_max_byte_value_times_180(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_file_size_mod_197_times_850_plus_decompressed_size_mod_2900_plus_max_byte_value_times_180(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_file_size_mod_197_times_850_plus_decompressed_size_mod_2900_plus_max_byte_value_times_180(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_197_times_850_plus_decompressed_size_mod_2900_plus_max_byte_value_times_180(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_file_size_mod_197_times_850_plus_decompressed_size_mod_2900_plus_max_byte_value_times_180(MINIMAL) >= 0

    def test_random_greater_than_text(self):
        assert (zst_file_size_mod_197_times_850_plus_decompressed_size_mod_2900_plus_max_byte_value_times_180(RANDOM) >
                zst_file_size_mod_197_times_850_plus_decompressed_size_mod_2900_plus_max_byte_value_times_180(TEXT))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_197_times_850_plus_decompressed_size_mod_2900_plus_max_byte_value_times_180(str(TEXT)) == 85920


# --- F2: zst_compressed_size_mod_199_times_800_plus_decompressed_size_mod_3000_plus_min_byte_value_times_1600 ---

class TestZstCompressedSizeMod199Times800PlusDecompressedMod3000PlusMinByte1600:
    def test_text_returns_109990(self):
        assert zst_compressed_size_mod_199_times_800_plus_decompressed_size_mod_3000_plus_min_byte_value_times_1600(TEXT) == 109990

    def test_minimal_returns_8001(self):
        assert zst_compressed_size_mod_199_times_800_plus_decompressed_size_mod_3000_plus_min_byte_value_times_1600(MINIMAL) == 8001

    def test_random_returns_62624(self):
        assert zst_compressed_size_mod_199_times_800_plus_decompressed_size_mod_3000_plus_min_byte_value_times_1600(RANDOM) == 62624

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_199_times_800_plus_decompressed_size_mod_3000_plus_min_byte_value_times_1600(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_compressed_size_mod_199_times_800_plus_decompressed_size_mod_3000_plus_min_byte_value_times_1600(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_compressed_size_mod_199_times_800_plus_decompressed_size_mod_3000_plus_min_byte_value_times_1600(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_199_times_800_plus_decompressed_size_mod_3000_plus_min_byte_value_times_1600(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_compressed_size_mod_199_times_800_plus_decompressed_size_mod_3000_plus_min_byte_value_times_1600(MINIMAL) >= 0

    def test_text_greater_than_random(self):
        assert (zst_compressed_size_mod_199_times_800_plus_decompressed_size_mod_3000_plus_min_byte_value_times_1600(TEXT) >
                zst_compressed_size_mod_199_times_800_plus_decompressed_size_mod_3000_plus_min_byte_value_times_1600(RANDOM))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_199_times_800_plus_decompressed_size_mod_3000_plus_min_byte_value_times_1600(str(TEXT)) == 109990
