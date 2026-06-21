"""Sprint 380 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINI = _ZST / "minimal-synthetic.zst"
RAND = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_509_times_2000_plus_decompressed_size_mod_7600_plus_max_byte_value_times_410,
    zst_compressed_size_mod_521_times_1950_plus_decompressed_size_mod_7700_plus_min_byte_value_times_2850,
)


# --- F1: zst_file_size_mod_509_times_2000_plus_decompressed_size_mod_7600_plus_max_byte_value_times_410 ---

class TestZstFileSizeMod509Times2000PlusDecompressed7600PlusMaxByte410:
    def test_text_returns_594000(self):
        assert zst_file_size_mod_509_times_2000_plus_decompressed_size_mod_7600_plus_max_byte_value_times_410(TEXT) == 594000

    def test_mini_returns_20001(self):
        assert zst_file_size_mod_509_times_2000_plus_decompressed_size_mod_7600_plus_max_byte_value_times_410(MINI) == 20001

    def test_rand_returns_657574(self):
        assert zst_file_size_mod_509_times_2000_plus_decompressed_size_mod_7600_plus_max_byte_value_times_410(RAND) == 657574

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_509_times_2000_plus_decompressed_size_mod_7600_plus_max_byte_value_times_410(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_file_size_mod_509_times_2000_plus_decompressed_size_mod_7600_plus_max_byte_value_times_410(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_file_size_mod_509_times_2000_plus_decompressed_size_mod_7600_plus_max_byte_value_times_410(RAND), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_509_times_2000_plus_decompressed_size_mod_7600_plus_max_byte_value_times_410(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_file_size_mod_509_times_2000_plus_decompressed_size_mod_7600_plus_max_byte_value_times_410(MINI) >= 0

    def test_rand_greater_than_mini(self):
        assert (zst_file_size_mod_509_times_2000_plus_decompressed_size_mod_7600_plus_max_byte_value_times_410(RAND) >
                zst_file_size_mod_509_times_2000_plus_decompressed_size_mod_7600_plus_max_byte_value_times_410(MINI))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_509_times_2000_plus_decompressed_size_mod_7600_plus_max_byte_value_times_410(str(TEXT)) == 594000


# --- F2: zst_compressed_size_mod_521_times_1950_plus_decompressed_size_mod_7700_plus_min_byte_value_times_2850 ---

class TestZstCompressedSizeMod521Times1950PlusDecompressed7700PlusMinByte2850:
    def test_text_returns_621990(self):
        assert zst_compressed_size_mod_521_times_1950_plus_decompressed_size_mod_7700_plus_min_byte_value_times_2850(TEXT) == 621990

    def test_mini_returns_19501(self):
        assert zst_compressed_size_mod_521_times_1950_plus_decompressed_size_mod_7700_plus_min_byte_value_times_2850(MINI) == 19501

    def test_rand_returns_539224(self):
        assert zst_compressed_size_mod_521_times_1950_plus_decompressed_size_mod_7700_plus_min_byte_value_times_2850(RAND) == 539224

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_521_times_1950_plus_decompressed_size_mod_7700_plus_min_byte_value_times_2850(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_compressed_size_mod_521_times_1950_plus_decompressed_size_mod_7700_plus_min_byte_value_times_2850(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_compressed_size_mod_521_times_1950_plus_decompressed_size_mod_7700_plus_min_byte_value_times_2850(RAND), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_521_times_1950_plus_decompressed_size_mod_7700_plus_min_byte_value_times_2850(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_compressed_size_mod_521_times_1950_plus_decompressed_size_mod_7700_plus_min_byte_value_times_2850(MINI) >= 0

    def test_text_greater_than_mini(self):
        assert (zst_compressed_size_mod_521_times_1950_plus_decompressed_size_mod_7700_plus_min_byte_value_times_2850(TEXT) >
                zst_compressed_size_mod_521_times_1950_plus_decompressed_size_mod_7700_plus_min_byte_value_times_2850(MINI))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_521_times_1950_plus_decompressed_size_mod_7700_plus_min_byte_value_times_2850(str(TEXT)) == 621990
