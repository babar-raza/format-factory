"""Sprint 335 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINIMAL = _ZST / "minimal-synthetic.zst"
RANDOM = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_331_times_1300_plus_decompressed_size_mod_4600_plus_max_byte_value_times_260,
    zst_compressed_size_mod_337_times_1225_plus_decompressed_size_mod_4700_plus_min_byte_value_times_2100,
)


# --- F1: zst_file_size_mod_331_times_1300_plus_decompressed_size_mod_4600_plus_max_byte_value_times_260 ---

class TestZstFileSizeMod331Times1300PlusDecomp4600PlusMax260:
    def test_text_returns_385450(self):
        assert zst_file_size_mod_331_times_1300_plus_decompressed_size_mod_4600_plus_max_byte_value_times_260(TEXT) == 385450

    def test_minimal_returns_13001(self):
        assert zst_file_size_mod_331_times_1300_plus_decompressed_size_mod_4600_plus_max_byte_value_times_260(MINIMAL) == 13001

    def test_random_returns_426124(self):
        assert zst_file_size_mod_331_times_1300_plus_decompressed_size_mod_4600_plus_max_byte_value_times_260(RANDOM) == 426124

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_331_times_1300_plus_decompressed_size_mod_4600_plus_max_byte_value_times_260(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_file_size_mod_331_times_1300_plus_decompressed_size_mod_4600_plus_max_byte_value_times_260(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_file_size_mod_331_times_1300_plus_decompressed_size_mod_4600_plus_max_byte_value_times_260(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_331_times_1300_plus_decompressed_size_mod_4600_plus_max_byte_value_times_260(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_file_size_mod_331_times_1300_plus_decompressed_size_mod_4600_plus_max_byte_value_times_260(MINIMAL) >= 0

    def test_random_greater_than_text(self):
        assert (zst_file_size_mod_331_times_1300_plus_decompressed_size_mod_4600_plus_max_byte_value_times_260(RANDOM) >
                zst_file_size_mod_331_times_1300_plus_decompressed_size_mod_4600_plus_max_byte_value_times_260(TEXT))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_331_times_1300_plus_decompressed_size_mod_4600_plus_max_byte_value_times_260(str(TEXT)) == 385450


# --- F2: zst_compressed_size_mod_337_times_1225_plus_decompressed_size_mod_4700_plus_min_byte_value_times_2100 ---

class TestZstCompressedSizeMod337Times1225PlusDecomp4700PlusMin2100:
    def test_text_returns_400790(self):
        assert zst_compressed_size_mod_337_times_1225_plus_decompressed_size_mod_4700_plus_min_byte_value_times_2100(TEXT) == 400790

    def test_minimal_returns_12251(self):
        assert zst_compressed_size_mod_337_times_1225_plus_decompressed_size_mod_4700_plus_min_byte_value_times_2100(MINIMAL) == 12251

    def test_random_returns_339124(self):
        assert zst_compressed_size_mod_337_times_1225_plus_decompressed_size_mod_4700_plus_min_byte_value_times_2100(RANDOM) == 339124

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_337_times_1225_plus_decompressed_size_mod_4700_plus_min_byte_value_times_2100(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_compressed_size_mod_337_times_1225_plus_decompressed_size_mod_4700_plus_min_byte_value_times_2100(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_compressed_size_mod_337_times_1225_plus_decompressed_size_mod_4700_plus_min_byte_value_times_2100(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_337_times_1225_plus_decompressed_size_mod_4700_plus_min_byte_value_times_2100(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_compressed_size_mod_337_times_1225_plus_decompressed_size_mod_4700_plus_min_byte_value_times_2100(MINIMAL) >= 0

    def test_text_greater_than_minimal(self):
        assert (zst_compressed_size_mod_337_times_1225_plus_decompressed_size_mod_4700_plus_min_byte_value_times_2100(TEXT) >
                zst_compressed_size_mod_337_times_1225_plus_decompressed_size_mod_4700_plus_min_byte_value_times_2100(MINIMAL))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_337_times_1225_plus_decompressed_size_mod_4700_plus_min_byte_value_times_2100(str(TEXT)) == 400790
