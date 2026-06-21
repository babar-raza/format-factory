"""Sprint 365 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINI = _ZST / "minimal-synthetic.zst"
RAND = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_449_times_1800_plus_decompressed_size_mod_6600_plus_max_byte_value_times_360,
    zst_compressed_size_mod_457_times_1725_plus_decompressed_size_mod_6700_plus_min_byte_value_times_2600,
)


# --- F1: zst_file_size_mod_449_times_1800_plus_decompressed_size_mod_6600_plus_max_byte_value_times_360 ---

class TestZstFileSizeMod449Times1800PlusDecompressed6600PlusMaxByte360:
    def test_text_returns_533550(self):
        assert zst_file_size_mod_449_times_1800_plus_decompressed_size_mod_6600_plus_max_byte_value_times_360(TEXT) == 533550

    def test_mini_returns_18001(self):
        assert zst_file_size_mod_449_times_1800_plus_decompressed_size_mod_6600_plus_max_byte_value_times_360(MINI) == 18001

    def test_rand_returns_589624(self):
        assert zst_file_size_mod_449_times_1800_plus_decompressed_size_mod_6600_plus_max_byte_value_times_360(RAND) == 589624

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_449_times_1800_plus_decompressed_size_mod_6600_plus_max_byte_value_times_360(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_file_size_mod_449_times_1800_plus_decompressed_size_mod_6600_plus_max_byte_value_times_360(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_file_size_mod_449_times_1800_plus_decompressed_size_mod_6600_plus_max_byte_value_times_360(RAND), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_449_times_1800_plus_decompressed_size_mod_6600_plus_max_byte_value_times_360(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_file_size_mod_449_times_1800_plus_decompressed_size_mod_6600_plus_max_byte_value_times_360(MINI) >= 0

    def test_rand_greater_than_mini(self):
        assert (zst_file_size_mod_449_times_1800_plus_decompressed_size_mod_6600_plus_max_byte_value_times_360(RAND) >
                zst_file_size_mod_449_times_1800_plus_decompressed_size_mod_6600_plus_max_byte_value_times_360(MINI))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_449_times_1800_plus_decompressed_size_mod_6600_plus_max_byte_value_times_360(str(TEXT)) == 533550


# --- F2: zst_compressed_size_mod_457_times_1725_plus_decompressed_size_mod_6700_plus_min_byte_value_times_2600 ---

class TestZstCompressedSizeMod457Times1725PlusDecompressed6700PlusMinByte2600:
    def test_text_returns_552790(self):
        assert zst_compressed_size_mod_457_times_1725_plus_decompressed_size_mod_6700_plus_min_byte_value_times_2600(TEXT) == 552790

    def test_mini_returns_17251(self):
        assert zst_compressed_size_mod_457_times_1725_plus_decompressed_size_mod_6700_plus_min_byte_value_times_2600(MINI) == 17251

    def test_rand_returns_477124(self):
        assert zst_compressed_size_mod_457_times_1725_plus_decompressed_size_mod_6700_plus_min_byte_value_times_2600(RAND) == 477124

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_457_times_1725_plus_decompressed_size_mod_6700_plus_min_byte_value_times_2600(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_compressed_size_mod_457_times_1725_plus_decompressed_size_mod_6700_plus_min_byte_value_times_2600(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_compressed_size_mod_457_times_1725_plus_decompressed_size_mod_6700_plus_min_byte_value_times_2600(RAND), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_457_times_1725_plus_decompressed_size_mod_6700_plus_min_byte_value_times_2600(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_compressed_size_mod_457_times_1725_plus_decompressed_size_mod_6700_plus_min_byte_value_times_2600(MINI) >= 0

    def test_text_greater_than_mini(self):
        assert (zst_compressed_size_mod_457_times_1725_plus_decompressed_size_mod_6700_plus_min_byte_value_times_2600(TEXT) >
                zst_compressed_size_mod_457_times_1725_plus_decompressed_size_mod_6700_plus_min_byte_value_times_2600(MINI))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_457_times_1725_plus_decompressed_size_mod_6700_plus_min_byte_value_times_2600(str(TEXT)) == 552790
