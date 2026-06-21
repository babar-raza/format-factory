"""Sprint 329 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINIMAL = _ZST / "minimal-synthetic.zst"
RANDOM = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_307_times_1200_plus_decompressed_size_mod_4200_plus_max_byte_value_times_240,
    zst_compressed_size_mod_311_times_1125_plus_decompressed_size_mod_4300_plus_min_byte_value_times_2000,
)


# --- F1: zst_file_size_mod_307_times_1200_plus_decompressed_size_mod_4200_plus_max_byte_value_times_240 ---

class TestZstFileSizeMod307Times1200PlusDecomp4200PlusMax240:
    def test_text_returns_355830(self):
        assert zst_file_size_mod_307_times_1200_plus_decompressed_size_mod_4200_plus_max_byte_value_times_240(TEXT) == 355830

    def test_minimal_returns_12001(self):
        assert zst_file_size_mod_307_times_1200_plus_decompressed_size_mod_4200_plus_max_byte_value_times_240(MINIMAL) == 12001

    def test_random_returns_393424(self):
        assert zst_file_size_mod_307_times_1200_plus_decompressed_size_mod_4200_plus_max_byte_value_times_240(RANDOM) == 393424

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_307_times_1200_plus_decompressed_size_mod_4200_plus_max_byte_value_times_240(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_file_size_mod_307_times_1200_plus_decompressed_size_mod_4200_plus_max_byte_value_times_240(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_file_size_mod_307_times_1200_plus_decompressed_size_mod_4200_plus_max_byte_value_times_240(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_307_times_1200_plus_decompressed_size_mod_4200_plus_max_byte_value_times_240(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_file_size_mod_307_times_1200_plus_decompressed_size_mod_4200_plus_max_byte_value_times_240(MINIMAL) >= 0

    def test_random_greater_than_text(self):
        assert (zst_file_size_mod_307_times_1200_plus_decompressed_size_mod_4200_plus_max_byte_value_times_240(RANDOM) >
                zst_file_size_mod_307_times_1200_plus_decompressed_size_mod_4200_plus_max_byte_value_times_240(TEXT))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_307_times_1200_plus_decompressed_size_mod_4200_plus_max_byte_value_times_240(str(TEXT)) == 355830


# --- F2: zst_compressed_size_mod_311_times_1125_plus_decompressed_size_mod_4300_plus_min_byte_value_times_2000 ---

class TestZstCompressedSizeMod311Times1125PlusDecomp4300PlusMin2000:
    def test_text_returns_370390(self):
        assert zst_compressed_size_mod_311_times_1125_plus_decompressed_size_mod_4300_plus_min_byte_value_times_2000(TEXT) == 370390

    def test_minimal_returns_11251(self):
        assert zst_compressed_size_mod_311_times_1125_plus_decompressed_size_mod_4300_plus_min_byte_value_times_2000(MINIMAL) == 11251

    def test_random_returns_311524(self):
        assert zst_compressed_size_mod_311_times_1125_plus_decompressed_size_mod_4300_plus_min_byte_value_times_2000(RANDOM) == 311524

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_311_times_1125_plus_decompressed_size_mod_4300_plus_min_byte_value_times_2000(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_compressed_size_mod_311_times_1125_plus_decompressed_size_mod_4300_plus_min_byte_value_times_2000(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_compressed_size_mod_311_times_1125_plus_decompressed_size_mod_4300_plus_min_byte_value_times_2000(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_311_times_1125_plus_decompressed_size_mod_4300_plus_min_byte_value_times_2000(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_compressed_size_mod_311_times_1125_plus_decompressed_size_mod_4300_plus_min_byte_value_times_2000(MINIMAL) >= 0

    def test_text_greater_than_minimal(self):
        assert (zst_compressed_size_mod_311_times_1125_plus_decompressed_size_mod_4300_plus_min_byte_value_times_2000(TEXT) >
                zst_compressed_size_mod_311_times_1125_plus_decompressed_size_mod_4300_plus_min_byte_value_times_2000(MINIMAL))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_311_times_1125_plus_decompressed_size_mod_4300_plus_min_byte_value_times_2000(str(TEXT)) == 370390
