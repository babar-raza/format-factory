"""Sprint 377 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINI = _ZST / "minimal-synthetic.zst"
RAND = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_499_times_1975_plus_decompressed_size_mod_7400_plus_max_byte_value_times_400,
    zst_compressed_size_mod_503_times_1925_plus_decompressed_size_mod_7500_plus_min_byte_value_times_2800,
)


# --- F1: zst_file_size_mod_499_times_1975_plus_decompressed_size_mod_7400_plus_max_byte_value_times_400 ---

class TestZstFileSizeMod499Times1975PlusDecompressed7400PlusMaxByte400:
    def test_text_returns_585990(self):
        assert zst_file_size_mod_499_times_1975_plus_decompressed_size_mod_7400_plus_max_byte_value_times_400(TEXT) == 585990

    def test_mini_returns_19751(self):
        assert zst_file_size_mod_499_times_1975_plus_decompressed_size_mod_7400_plus_max_byte_value_times_400(MINI) == 19751

    def test_rand_returns_648124(self):
        assert zst_file_size_mod_499_times_1975_plus_decompressed_size_mod_7400_plus_max_byte_value_times_400(RAND) == 648124

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_499_times_1975_plus_decompressed_size_mod_7400_plus_max_byte_value_times_400(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_file_size_mod_499_times_1975_plus_decompressed_size_mod_7400_plus_max_byte_value_times_400(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_file_size_mod_499_times_1975_plus_decompressed_size_mod_7400_plus_max_byte_value_times_400(RAND), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_499_times_1975_plus_decompressed_size_mod_7400_plus_max_byte_value_times_400(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_file_size_mod_499_times_1975_plus_decompressed_size_mod_7400_plus_max_byte_value_times_400(MINI) >= 0

    def test_rand_greater_than_mini(self):
        assert (zst_file_size_mod_499_times_1975_plus_decompressed_size_mod_7400_plus_max_byte_value_times_400(RAND) >
                zst_file_size_mod_499_times_1975_plus_decompressed_size_mod_7400_plus_max_byte_value_times_400(MINI))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_499_times_1975_plus_decompressed_size_mod_7400_plus_max_byte_value_times_400(str(TEXT)) == 585990


# --- F2: zst_compressed_size_mod_503_times_1925_plus_decompressed_size_mod_7500_plus_min_byte_value_times_2800 ---

class TestZstCompressedSizeMod503Times1925PlusDecompressed7500PlusMinByte2800:
    def test_text_returns_613590(self):
        assert zst_compressed_size_mod_503_times_1925_plus_decompressed_size_mod_7500_plus_min_byte_value_times_2800(TEXT) == 613590

    def test_mini_returns_19251(self):
        assert zst_compressed_size_mod_503_times_1925_plus_decompressed_size_mod_7500_plus_min_byte_value_times_2800(MINI) == 19251

    def test_rand_returns_532324(self):
        assert zst_compressed_size_mod_503_times_1925_plus_decompressed_size_mod_7500_plus_min_byte_value_times_2800(RAND) == 532324

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_503_times_1925_plus_decompressed_size_mod_7500_plus_min_byte_value_times_2800(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_compressed_size_mod_503_times_1925_plus_decompressed_size_mod_7500_plus_min_byte_value_times_2800(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_compressed_size_mod_503_times_1925_plus_decompressed_size_mod_7500_plus_min_byte_value_times_2800(RAND), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_503_times_1925_plus_decompressed_size_mod_7500_plus_min_byte_value_times_2800(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_compressed_size_mod_503_times_1925_plus_decompressed_size_mod_7500_plus_min_byte_value_times_2800(MINI) >= 0

    def test_text_greater_than_mini(self):
        assert (zst_compressed_size_mod_503_times_1925_plus_decompressed_size_mod_7500_plus_min_byte_value_times_2800(TEXT) >
                zst_compressed_size_mod_503_times_1925_plus_decompressed_size_mod_7500_plus_min_byte_value_times_2800(MINI))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_503_times_1925_plus_decompressed_size_mod_7500_plus_min_byte_value_times_2800(str(TEXT)) == 613590
