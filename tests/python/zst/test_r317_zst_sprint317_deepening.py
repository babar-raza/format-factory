"""Sprint 317 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINIMAL = _ZST / "minimal-synthetic.zst"
RANDOM = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_251_times_1000_plus_decompressed_size_mod_3500_plus_max_byte_value_times_200,
    zst_compressed_size_mod_257_times_925_plus_decompressed_size_mod_3600_plus_min_byte_value_times_1800,
)


# --- F1: zst_file_size_mod_251_times_1000_plus_decompressed_size_mod_3500_plus_max_byte_value_times_200 ---

class TestZstFileSizeMod251Times1000PlusDecompressed3500PlusMaxByte200:
    def test_text_returns_45590(self):
        assert zst_file_size_mod_251_times_1000_plus_decompressed_size_mod_3500_plus_max_byte_value_times_200(TEXT) == 45590

    def test_minimal_returns_10001(self):
        assert zst_file_size_mod_251_times_1000_plus_decompressed_size_mod_3500_plus_max_byte_value_times_200(MINIMAL) == 10001

    def test_random_returns_77024(self):
        assert zst_file_size_mod_251_times_1000_plus_decompressed_size_mod_3500_plus_max_byte_value_times_200(RANDOM) == 77024

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_251_times_1000_plus_decompressed_size_mod_3500_plus_max_byte_value_times_200(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_file_size_mod_251_times_1000_plus_decompressed_size_mod_3500_plus_max_byte_value_times_200(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_file_size_mod_251_times_1000_plus_decompressed_size_mod_3500_plus_max_byte_value_times_200(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_251_times_1000_plus_decompressed_size_mod_3500_plus_max_byte_value_times_200(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_file_size_mod_251_times_1000_plus_decompressed_size_mod_3500_plus_max_byte_value_times_200(MINIMAL) >= 0

    def test_random_greater_than_text(self):
        assert (zst_file_size_mod_251_times_1000_plus_decompressed_size_mod_3500_plus_max_byte_value_times_200(RANDOM) >
                zst_file_size_mod_251_times_1000_plus_decompressed_size_mod_3500_plus_max_byte_value_times_200(TEXT))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_251_times_1000_plus_decompressed_size_mod_3500_plus_max_byte_value_times_200(str(TEXT)) == 45590


# --- F2: zst_compressed_size_mod_257_times_925_plus_decompressed_size_mod_3600_plus_min_byte_value_times_1800 ---

class TestZstCompressedSizeMod257Times925PlusDecompressed3600PlusMinByte1800:
    def test_text_returns_71865(self):
        assert zst_compressed_size_mod_257_times_925_plus_decompressed_size_mod_3600_plus_min_byte_value_times_1800(TEXT) == 71865

    def test_minimal_returns_9251(self):
        assert zst_compressed_size_mod_257_times_925_plus_decompressed_size_mod_3600_plus_min_byte_value_times_1800(MINIMAL) == 9251

    def test_random_returns_18599(self):
        assert zst_compressed_size_mod_257_times_925_plus_decompressed_size_mod_3600_plus_min_byte_value_times_1800(RANDOM) == 18599

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_257_times_925_plus_decompressed_size_mod_3600_plus_min_byte_value_times_1800(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_compressed_size_mod_257_times_925_plus_decompressed_size_mod_3600_plus_min_byte_value_times_1800(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_compressed_size_mod_257_times_925_plus_decompressed_size_mod_3600_plus_min_byte_value_times_1800(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_257_times_925_plus_decompressed_size_mod_3600_plus_min_byte_value_times_1800(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_compressed_size_mod_257_times_925_plus_decompressed_size_mod_3600_plus_min_byte_value_times_1800(MINIMAL) >= 0

    def test_text_greater_than_random(self):
        assert (zst_compressed_size_mod_257_times_925_plus_decompressed_size_mod_3600_plus_min_byte_value_times_1800(TEXT) >
                zst_compressed_size_mod_257_times_925_plus_decompressed_size_mod_3600_plus_min_byte_value_times_1800(RANDOM))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_257_times_925_plus_decompressed_size_mod_3600_plus_min_byte_value_times_1800(str(TEXT)) == 71865
