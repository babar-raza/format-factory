"""Sprint 275 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINIMAL = _ZST / "minimal-synthetic.zst"
RANDOM = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_73_times_400_plus_decompressed_size_mod_700_plus_max_byte_value_times_60,
    zst_compressed_size_mod_79_times_250_plus_decompressed_size_mod_800_plus_min_byte_value_times_500,
)


# --- F1: zst_file_size_mod_73_times_400_plus_decompressed_size_mod_700_plus_max_byte_value_times_60 ---

class TestZstFileSizeMod73Times400PlusDecompressedMod700PlusMaxByte60:
    def test_text_returns_28850(self):
        assert zst_file_size_mod_73_times_400_plus_decompressed_size_mod_700_plus_max_byte_value_times_60(TEXT) == 28850

    def test_minimal_returns_4001(self):
        assert zst_file_size_mod_73_times_400_plus_decompressed_size_mod_700_plus_max_byte_value_times_60(MINIMAL) == 4001

    def test_random_returns_38424(self):
        assert zst_file_size_mod_73_times_400_plus_decompressed_size_mod_700_plus_max_byte_value_times_60(RANDOM) == 38424

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_73_times_400_plus_decompressed_size_mod_700_plus_max_byte_value_times_60(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_file_size_mod_73_times_400_plus_decompressed_size_mod_700_plus_max_byte_value_times_60(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_file_size_mod_73_times_400_plus_decompressed_size_mod_700_plus_max_byte_value_times_60(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_73_times_400_plus_decompressed_size_mod_700_plus_max_byte_value_times_60(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_file_size_mod_73_times_400_plus_decompressed_size_mod_700_plus_max_byte_value_times_60(MINIMAL) >= 0

    def test_random_greater_than_text(self):
        assert (zst_file_size_mod_73_times_400_plus_decompressed_size_mod_700_plus_max_byte_value_times_60(RANDOM) >
                zst_file_size_mod_73_times_400_plus_decompressed_size_mod_700_plus_max_byte_value_times_60(TEXT))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_73_times_400_plus_decompressed_size_mod_700_plus_max_byte_value_times_60(str(TEXT)) == 28850


# --- F2: zst_compressed_size_mod_79_times_250_plus_decompressed_size_mod_800_plus_min_byte_value_times_500 ---

class TestZstCompressedSizeMod79Times250PlusDecompressedMod800PlusMinByte500:
    def test_text_returns_25140(self):
        assert zst_compressed_size_mod_79_times_250_plus_decompressed_size_mod_800_plus_min_byte_value_times_500(TEXT) == 25140

    def test_minimal_returns_2501(self):
        assert zst_compressed_size_mod_79_times_250_plus_decompressed_size_mod_800_plus_min_byte_value_times_500(MINIMAL) == 2501

    def test_random_returns_9974(self):
        assert zst_compressed_size_mod_79_times_250_plus_decompressed_size_mod_800_plus_min_byte_value_times_500(RANDOM) == 9974

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_79_times_250_plus_decompressed_size_mod_800_plus_min_byte_value_times_500(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_compressed_size_mod_79_times_250_plus_decompressed_size_mod_800_plus_min_byte_value_times_500(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_compressed_size_mod_79_times_250_plus_decompressed_size_mod_800_plus_min_byte_value_times_500(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_79_times_250_plus_decompressed_size_mod_800_plus_min_byte_value_times_500(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_compressed_size_mod_79_times_250_plus_decompressed_size_mod_800_plus_min_byte_value_times_500(MINIMAL) >= 0

    def test_text_greater_than_random(self):
        assert (zst_compressed_size_mod_79_times_250_plus_decompressed_size_mod_800_plus_min_byte_value_times_500(TEXT) >
                zst_compressed_size_mod_79_times_250_plus_decompressed_size_mod_800_plus_min_byte_value_times_500(RANDOM))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_79_times_250_plus_decompressed_size_mod_800_plus_min_byte_value_times_500(str(TEXT)) == 25140
