"""Sprint 305 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINIMAL = _ZST / "minimal-synthetic.zst"
RANDOM = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_191_times_800_plus_decompressed_size_mod_2700_plus_max_byte_value_times_170,
    zst_compressed_size_mod_193_times_750_plus_decompressed_size_mod_2800_plus_min_byte_value_times_1500,
)


# --- F1: zst_file_size_mod_191_times_800_plus_decompressed_size_mod_2700_plus_max_byte_value_times_170 ---

class TestZstFileSizeMod191Times800PlusDecompressedMod2700PlusMaxByte170:
    def test_text_returns_85760(self):
        assert zst_file_size_mod_191_times_800_plus_decompressed_size_mod_2700_plus_max_byte_value_times_170(TEXT) == 85760

    def test_minimal_returns_8001(self):
        assert zst_file_size_mod_191_times_800_plus_decompressed_size_mod_2700_plus_max_byte_value_times_170(MINIMAL) == 8001

    def test_random_returns_112374(self):
        assert zst_file_size_mod_191_times_800_plus_decompressed_size_mod_2700_plus_max_byte_value_times_170(RANDOM) == 112374

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_191_times_800_plus_decompressed_size_mod_2700_plus_max_byte_value_times_170(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_file_size_mod_191_times_800_plus_decompressed_size_mod_2700_plus_max_byte_value_times_170(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_file_size_mod_191_times_800_plus_decompressed_size_mod_2700_plus_max_byte_value_times_170(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_191_times_800_plus_decompressed_size_mod_2700_plus_max_byte_value_times_170(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_file_size_mod_191_times_800_plus_decompressed_size_mod_2700_plus_max_byte_value_times_170(MINIMAL) >= 0

    def test_random_greater_than_text(self):
        assert (zst_file_size_mod_191_times_800_plus_decompressed_size_mod_2700_plus_max_byte_value_times_170(RANDOM) >
                zst_file_size_mod_191_times_800_plus_decompressed_size_mod_2700_plus_max_byte_value_times_170(TEXT))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_191_times_800_plus_decompressed_size_mod_2700_plus_max_byte_value_times_170(str(TEXT)) == 85760


# --- F2: zst_compressed_size_mod_193_times_750_plus_decompressed_size_mod_2800_plus_min_byte_value_times_1500 ---

class TestZstCompressedSizeMod193Times750PlusDecompressedMod2800PlusMinByte1500:
    def test_text_returns_107640(self):
        assert zst_compressed_size_mod_193_times_750_plus_decompressed_size_mod_2800_plus_min_byte_value_times_1500(TEXT) == 107640

    def test_minimal_returns_7501(self):
        assert zst_compressed_size_mod_193_times_750_plus_decompressed_size_mod_2800_plus_min_byte_value_times_1500(MINIMAL) == 7501

    def test_random_returns_63274(self):
        assert zst_compressed_size_mod_193_times_750_plus_decompressed_size_mod_2800_plus_min_byte_value_times_1500(RANDOM) == 63274

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_193_times_750_plus_decompressed_size_mod_2800_plus_min_byte_value_times_1500(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_compressed_size_mod_193_times_750_plus_decompressed_size_mod_2800_plus_min_byte_value_times_1500(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_compressed_size_mod_193_times_750_plus_decompressed_size_mod_2800_plus_min_byte_value_times_1500(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_193_times_750_plus_decompressed_size_mod_2800_plus_min_byte_value_times_1500(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_compressed_size_mod_193_times_750_plus_decompressed_size_mod_2800_plus_min_byte_value_times_1500(MINIMAL) >= 0

    def test_text_greater_than_random(self):
        assert (zst_compressed_size_mod_193_times_750_plus_decompressed_size_mod_2800_plus_min_byte_value_times_1500(TEXT) >
                zst_compressed_size_mod_193_times_750_plus_decompressed_size_mod_2800_plus_min_byte_value_times_1500(RANDOM))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_193_times_750_plus_decompressed_size_mod_2800_plus_min_byte_value_times_1500(str(TEXT)) == 107640
