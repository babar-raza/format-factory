"""Sprint 290 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINIMAL = _ZST / "minimal-synthetic.zst"
RANDOM = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_127_times_550_plus_decompressed_size_mod_1700_plus_max_byte_value_times_110,
    zst_compressed_size_mod_131_times_500_plus_decompressed_size_mod_1800_plus_min_byte_value_times_1000,
)


# --- F1: zst_file_size_mod_127_times_550_plus_decompressed_size_mod_1700_plus_max_byte_value_times_110 ---

class TestZstFileSizeMod127Times550PlusDecompressedMod1700PlusMaxByte110:
    def test_text_returns_23600(self):
        assert zst_file_size_mod_127_times_550_plus_decompressed_size_mod_1700_plus_max_byte_value_times_110(TEXT) == 23600

    def test_minimal_returns_5501(self):
        assert zst_file_size_mod_127_times_550_plus_decompressed_size_mod_1700_plus_max_byte_value_times_110(MINIMAL) == 5501

    def test_random_returns_41174(self):
        assert zst_file_size_mod_127_times_550_plus_decompressed_size_mod_1700_plus_max_byte_value_times_110(RANDOM) == 41174

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_127_times_550_plus_decompressed_size_mod_1700_plus_max_byte_value_times_110(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_file_size_mod_127_times_550_plus_decompressed_size_mod_1700_plus_max_byte_value_times_110(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_file_size_mod_127_times_550_plus_decompressed_size_mod_1700_plus_max_byte_value_times_110(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_127_times_550_plus_decompressed_size_mod_1700_plus_max_byte_value_times_110(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_file_size_mod_127_times_550_plus_decompressed_size_mod_1700_plus_max_byte_value_times_110(MINIMAL) >= 0

    def test_random_greater_than_text(self):
        assert (zst_file_size_mod_127_times_550_plus_decompressed_size_mod_1700_plus_max_byte_value_times_110(RANDOM) >
                zst_file_size_mod_127_times_550_plus_decompressed_size_mod_1700_plus_max_byte_value_times_110(TEXT))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_127_times_550_plus_decompressed_size_mod_1700_plus_max_byte_value_times_110(str(TEXT)) == 23600


# --- F2: zst_compressed_size_mod_131_times_500_plus_decompressed_size_mod_1800_plus_min_byte_value_times_1000 ---

class TestZstCompressedSizeMod131Times500PlusDecompressedMod1800PlusMinByte1000:
    def test_text_returns_37390(self):
        assert zst_compressed_size_mod_131_times_500_plus_decompressed_size_mod_1800_plus_min_byte_value_times_1000(TEXT) == 37390

    def test_minimal_returns_5001(self):
        assert zst_compressed_size_mod_131_times_500_plus_decompressed_size_mod_1800_plus_min_byte_value_times_1000(MINIMAL) == 5001

    def test_random_returns_8024(self):
        assert zst_compressed_size_mod_131_times_500_plus_decompressed_size_mod_1800_plus_min_byte_value_times_1000(RANDOM) == 8024

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_131_times_500_plus_decompressed_size_mod_1800_plus_min_byte_value_times_1000(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_compressed_size_mod_131_times_500_plus_decompressed_size_mod_1800_plus_min_byte_value_times_1000(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_compressed_size_mod_131_times_500_plus_decompressed_size_mod_1800_plus_min_byte_value_times_1000(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_131_times_500_plus_decompressed_size_mod_1800_plus_min_byte_value_times_1000(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_compressed_size_mod_131_times_500_plus_decompressed_size_mod_1800_plus_min_byte_value_times_1000(MINIMAL) >= 0

    def test_text_greater_than_random(self):
        assert (zst_compressed_size_mod_131_times_500_plus_decompressed_size_mod_1800_plus_min_byte_value_times_1000(TEXT) >
                zst_compressed_size_mod_131_times_500_plus_decompressed_size_mod_1800_plus_min_byte_value_times_1000(RANDOM))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_131_times_500_plus_decompressed_size_mod_1800_plus_min_byte_value_times_1000(str(TEXT)) == 37390
