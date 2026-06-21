"""Sprint 311 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINIMAL = _ZST / "minimal-synthetic.zst"
RANDOM = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_223_times_900_plus_decompressed_size_mod_3100_plus_max_byte_value_times_190,
    zst_compressed_size_mod_227_times_850_plus_decompressed_size_mod_3200_plus_min_byte_value_times_1700,
)


# --- F1: zst_file_size_mod_223_times_900_plus_decompressed_size_mod_3100_plus_max_byte_value_times_190 ---

class TestZstFileSizeMod223Times900PlusDecompressedMod3100PlusMaxByte190:
    def test_text_returns_67480(self):
        assert zst_file_size_mod_223_times_900_plus_decompressed_size_mod_3100_plus_max_byte_value_times_190(TEXT) == 67480

    def test_minimal_returns_9001(self):
        assert zst_file_size_mod_223_times_900_plus_decompressed_size_mod_3100_plus_max_byte_value_times_190(MINIMAL) == 9001

    def test_random_returns_97174(self):
        assert zst_file_size_mod_223_times_900_plus_decompressed_size_mod_3100_plus_max_byte_value_times_190(RANDOM) == 97174

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_223_times_900_plus_decompressed_size_mod_3100_plus_max_byte_value_times_190(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_file_size_mod_223_times_900_plus_decompressed_size_mod_3100_plus_max_byte_value_times_190(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_file_size_mod_223_times_900_plus_decompressed_size_mod_3100_plus_max_byte_value_times_190(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_223_times_900_plus_decompressed_size_mod_3100_plus_max_byte_value_times_190(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_file_size_mod_223_times_900_plus_decompressed_size_mod_3100_plus_max_byte_value_times_190(MINIMAL) >= 0

    def test_random_greater_than_text(self):
        assert (zst_file_size_mod_223_times_900_plus_decompressed_size_mod_3100_plus_max_byte_value_times_190(RANDOM) >
                zst_file_size_mod_223_times_900_plus_decompressed_size_mod_3100_plus_max_byte_value_times_190(TEXT))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_223_times_900_plus_decompressed_size_mod_3100_plus_max_byte_value_times_190(str(TEXT)) == 67480


# --- F2: zst_compressed_size_mod_227_times_850_plus_decompressed_size_mod_3200_plus_min_byte_value_times_1700 ---

class TestZstCompressedSizeMod227Times850PlusDecompressedMod3200PlusMinByte1700:
    def test_text_returns_93040(self):
        assert zst_compressed_size_mod_227_times_850_plus_decompressed_size_mod_3200_plus_min_byte_value_times_1700(TEXT) == 93040

    def test_minimal_returns_8501(self):
        assert zst_compressed_size_mod_227_times_850_plus_decompressed_size_mod_3200_plus_min_byte_value_times_1700(MINIMAL) == 8501

    def test_random_returns_42674(self):
        assert zst_compressed_size_mod_227_times_850_plus_decompressed_size_mod_3200_plus_min_byte_value_times_1700(RANDOM) == 42674

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_227_times_850_plus_decompressed_size_mod_3200_plus_min_byte_value_times_1700(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_compressed_size_mod_227_times_850_plus_decompressed_size_mod_3200_plus_min_byte_value_times_1700(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_compressed_size_mod_227_times_850_plus_decompressed_size_mod_3200_plus_min_byte_value_times_1700(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_227_times_850_plus_decompressed_size_mod_3200_plus_min_byte_value_times_1700(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_compressed_size_mod_227_times_850_plus_decompressed_size_mod_3200_plus_min_byte_value_times_1700(MINIMAL) >= 0

    def test_text_greater_than_random(self):
        assert (zst_compressed_size_mod_227_times_850_plus_decompressed_size_mod_3200_plus_min_byte_value_times_1700(TEXT) >
                zst_compressed_size_mod_227_times_850_plus_decompressed_size_mod_3200_plus_min_byte_value_times_1700(RANDOM))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_227_times_850_plus_decompressed_size_mod_3200_plus_min_byte_value_times_1700(str(TEXT)) == 93040
