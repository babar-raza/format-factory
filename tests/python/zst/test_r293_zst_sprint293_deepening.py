"""Sprint 293 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINIMAL = _ZST / "minimal-synthetic.zst"
RANDOM = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_137_times_600_plus_decompressed_size_mod_1900_plus_max_byte_value_times_120,
    zst_compressed_size_mod_139_times_550_plus_decompressed_size_mod_2000_plus_min_byte_value_times_1100,
)


# --- F1: zst_file_size_mod_137_times_600_plus_decompressed_size_mod_1900_plus_max_byte_value_times_120 ---

class TestZstFileSizeMod137Times600PlusDecompressedMod1900PlusMaxByte120:
    def test_text_returns_95910(self):
        assert zst_file_size_mod_137_times_600_plus_decompressed_size_mod_1900_plus_max_byte_value_times_120(TEXT) == 95910

    def test_minimal_returns_6001(self):
        assert zst_file_size_mod_137_times_600_plus_decompressed_size_mod_1900_plus_max_byte_value_times_120(MINIMAL) == 6001

    def test_random_returns_32824(self):
        assert zst_file_size_mod_137_times_600_plus_decompressed_size_mod_1900_plus_max_byte_value_times_120(RANDOM) == 32824

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_137_times_600_plus_decompressed_size_mod_1900_plus_max_byte_value_times_120(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_file_size_mod_137_times_600_plus_decompressed_size_mod_1900_plus_max_byte_value_times_120(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_file_size_mod_137_times_600_plus_decompressed_size_mod_1900_plus_max_byte_value_times_120(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_137_times_600_plus_decompressed_size_mod_1900_plus_max_byte_value_times_120(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_file_size_mod_137_times_600_plus_decompressed_size_mod_1900_plus_max_byte_value_times_120(MINIMAL) >= 0

    def test_text_greater_than_random(self):
        assert (zst_file_size_mod_137_times_600_plus_decompressed_size_mod_1900_plus_max_byte_value_times_120(TEXT) >
                zst_file_size_mod_137_times_600_plus_decompressed_size_mod_1900_plus_max_byte_value_times_120(RANDOM))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_137_times_600_plus_decompressed_size_mod_1900_plus_max_byte_value_times_120(str(TEXT)) == 95910


# --- F2: zst_compressed_size_mod_139_times_550_plus_decompressed_size_mod_2000_plus_min_byte_value_times_1100 ---

class TestZstCompressedSizeMod139Times550PlusDecompressedMod2000PlusMinByte1100:
    def test_text_returns_108740(self):
        assert zst_compressed_size_mod_139_times_550_plus_decompressed_size_mod_2000_plus_min_byte_value_times_1100(TEXT) == 108740

    def test_minimal_returns_5501(self):
        assert zst_compressed_size_mod_139_times_550_plus_decompressed_size_mod_2000_plus_min_byte_value_times_1100(MINIMAL) == 5501

    def test_random_returns_76374(self):
        assert zst_compressed_size_mod_139_times_550_plus_decompressed_size_mod_2000_plus_min_byte_value_times_1100(RANDOM) == 76374

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_139_times_550_plus_decompressed_size_mod_2000_plus_min_byte_value_times_1100(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_compressed_size_mod_139_times_550_plus_decompressed_size_mod_2000_plus_min_byte_value_times_1100(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_compressed_size_mod_139_times_550_plus_decompressed_size_mod_2000_plus_min_byte_value_times_1100(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_139_times_550_plus_decompressed_size_mod_2000_plus_min_byte_value_times_1100(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_compressed_size_mod_139_times_550_plus_decompressed_size_mod_2000_plus_min_byte_value_times_1100(MINIMAL) >= 0

    def test_text_greater_than_random(self):
        assert (zst_compressed_size_mod_139_times_550_plus_decompressed_size_mod_2000_plus_min_byte_value_times_1100(TEXT) >
                zst_compressed_size_mod_139_times_550_plus_decompressed_size_mod_2000_plus_min_byte_value_times_1100(RANDOM))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_139_times_550_plus_decompressed_size_mod_2000_plus_min_byte_value_times_1100(str(TEXT)) == 108740
