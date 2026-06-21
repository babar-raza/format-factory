"""Sprint 332 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINIMAL = _ZST / "minimal-synthetic.zst"
RANDOM = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_313_times_1250_plus_decompressed_size_mod_4400_plus_max_byte_value_times_250,
    zst_compressed_size_mod_317_times_1175_plus_decompressed_size_mod_4500_plus_min_byte_value_times_2050,
)


# --- F1: zst_file_size_mod_313_times_1250_plus_decompressed_size_mod_4400_plus_max_byte_value_times_250 ---

class TestZstFileSizeMod313Times1250PlusDecomp4400PlusMax250:
    def test_text_returns_370640(self):
        assert zst_file_size_mod_313_times_1250_plus_decompressed_size_mod_4400_plus_max_byte_value_times_250(TEXT) == 370640

    def test_minimal_returns_12501(self):
        assert zst_file_size_mod_313_times_1250_plus_decompressed_size_mod_4400_plus_max_byte_value_times_250(MINIMAL) == 12501

    def test_random_returns_409774(self):
        assert zst_file_size_mod_313_times_1250_plus_decompressed_size_mod_4400_plus_max_byte_value_times_250(RANDOM) == 409774

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_313_times_1250_plus_decompressed_size_mod_4400_plus_max_byte_value_times_250(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_file_size_mod_313_times_1250_plus_decompressed_size_mod_4400_plus_max_byte_value_times_250(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_file_size_mod_313_times_1250_plus_decompressed_size_mod_4400_plus_max_byte_value_times_250(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_313_times_1250_plus_decompressed_size_mod_4400_plus_max_byte_value_times_250(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_file_size_mod_313_times_1250_plus_decompressed_size_mod_4400_plus_max_byte_value_times_250(MINIMAL) >= 0

    def test_random_greater_than_text(self):
        assert (zst_file_size_mod_313_times_1250_plus_decompressed_size_mod_4400_plus_max_byte_value_times_250(RANDOM) >
                zst_file_size_mod_313_times_1250_plus_decompressed_size_mod_4400_plus_max_byte_value_times_250(TEXT))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_313_times_1250_plus_decompressed_size_mod_4400_plus_max_byte_value_times_250(str(TEXT)) == 370640


# --- F2: zst_compressed_size_mod_317_times_1175_plus_decompressed_size_mod_4500_plus_min_byte_value_times_2050 ---

class TestZstCompressedSizeMod317Times1175PlusDecomp4500PlusMin2050:
    def test_text_returns_385590(self):
        assert zst_compressed_size_mod_317_times_1175_plus_decompressed_size_mod_4500_plus_min_byte_value_times_2050(TEXT) == 385590

    def test_minimal_returns_11751(self):
        assert zst_compressed_size_mod_317_times_1175_plus_decompressed_size_mod_4500_plus_min_byte_value_times_2050(MINIMAL) == 11751

    def test_random_returns_325324(self):
        assert zst_compressed_size_mod_317_times_1175_plus_decompressed_size_mod_4500_plus_min_byte_value_times_2050(RANDOM) == 325324

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_317_times_1175_plus_decompressed_size_mod_4500_plus_min_byte_value_times_2050(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_compressed_size_mod_317_times_1175_plus_decompressed_size_mod_4500_plus_min_byte_value_times_2050(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_compressed_size_mod_317_times_1175_plus_decompressed_size_mod_4500_plus_min_byte_value_times_2050(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_317_times_1175_plus_decompressed_size_mod_4500_plus_min_byte_value_times_2050(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_compressed_size_mod_317_times_1175_plus_decompressed_size_mod_4500_plus_min_byte_value_times_2050(MINIMAL) >= 0

    def test_text_greater_than_minimal(self):
        assert (zst_compressed_size_mod_317_times_1175_plus_decompressed_size_mod_4500_plus_min_byte_value_times_2050(TEXT) >
                zst_compressed_size_mod_317_times_1175_plus_decompressed_size_mod_4500_plus_min_byte_value_times_2050(MINIMAL))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_317_times_1175_plus_decompressed_size_mod_4500_plus_min_byte_value_times_2050(str(TEXT)) == 385590
