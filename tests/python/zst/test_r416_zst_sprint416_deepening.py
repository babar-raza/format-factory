"""Sprint 416 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINI = _ZST / "minimal-synthetic.zst"
RAND = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_661_times_2400_plus_decompressed_size_mod_9900_plus_max_byte_value_times_530,
    zst_compressed_size_mod_673_times_2350_plus_decompressed_size_mod_9800_plus_min_byte_value_times_3450,
)


# --- F1: zst_file_size_mod_661_times_2400_plus_decompressed_size_mod_9900_plus_max_byte_value_times_530 ---

class TestZstFileSizeMod661Times2400PlusDecompressed9900PlusMaxByte530:
    def test_text_returns_717320(self):
        assert zst_file_size_mod_661_times_2400_plus_decompressed_size_mod_9900_plus_max_byte_value_times_530(TEXT) == 717320

    def test_mini_returns_24001(self):
        assert zst_file_size_mod_661_times_2400_plus_decompressed_size_mod_9900_plus_max_byte_value_times_530(MINI) == 24001

    def test_rand_returns_798574(self):
        assert zst_file_size_mod_661_times_2400_plus_decompressed_size_mod_9900_plus_max_byte_value_times_530(RAND) == 798574

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_661_times_2400_plus_decompressed_size_mod_9900_plus_max_byte_value_times_530(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_file_size_mod_661_times_2400_plus_decompressed_size_mod_9900_plus_max_byte_value_times_530(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_file_size_mod_661_times_2400_plus_decompressed_size_mod_9900_plus_max_byte_value_times_530(RAND), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_661_times_2400_plus_decompressed_size_mod_9900_plus_max_byte_value_times_530(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_file_size_mod_661_times_2400_plus_decompressed_size_mod_9900_plus_max_byte_value_times_530(MINI) >= 0

    def test_rand_greater_than_mini(self):
        assert (zst_file_size_mod_661_times_2400_plus_decompressed_size_mod_9900_plus_max_byte_value_times_530(RAND) >
                zst_file_size_mod_661_times_2400_plus_decompressed_size_mod_9900_plus_max_byte_value_times_530(MINI))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_661_times_2400_plus_decompressed_size_mod_9900_plus_max_byte_value_times_530(str(TEXT)) == 717320


# --- F2: zst_compressed_size_mod_673_times_2350_plus_decompressed_size_mod_9800_plus_min_byte_value_times_3450 ---

class TestZstCompressedSizeMod673Times2350PlusDecompressed9800PlusMinByte3450:
    def test_text_returns_749990(self):
        assert zst_compressed_size_mod_673_times_2350_plus_decompressed_size_mod_9800_plus_min_byte_value_times_3450(TEXT) == 749990

    def test_mini_returns_23501(self):
        assert zst_compressed_size_mod_673_times_2350_plus_decompressed_size_mod_9800_plus_min_byte_value_times_3450(MINI) == 23501

    def test_rand_returns_649624(self):
        assert zst_compressed_size_mod_673_times_2350_plus_decompressed_size_mod_9800_plus_min_byte_value_times_3450(RAND) == 649624

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_673_times_2350_plus_decompressed_size_mod_9800_plus_min_byte_value_times_3450(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_compressed_size_mod_673_times_2350_plus_decompressed_size_mod_9800_plus_min_byte_value_times_3450(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_compressed_size_mod_673_times_2350_plus_decompressed_size_mod_9800_plus_min_byte_value_times_3450(RAND), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_673_times_2350_plus_decompressed_size_mod_9800_plus_min_byte_value_times_3450(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_compressed_size_mod_673_times_2350_plus_decompressed_size_mod_9800_plus_min_byte_value_times_3450(MINI) >= 0

    def test_text_greater_than_mini(self):
        assert (zst_compressed_size_mod_673_times_2350_plus_decompressed_size_mod_9800_plus_min_byte_value_times_3450(TEXT) >
                zst_compressed_size_mod_673_times_2350_plus_decompressed_size_mod_9800_plus_min_byte_value_times_3450(MINI))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_673_times_2350_plus_decompressed_size_mod_9800_plus_min_byte_value_times_3450(str(TEXT)) == 749990
