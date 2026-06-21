"""Sprint 413 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINI = _ZST / "minimal-synthetic.zst"
RAND = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_653_times_2350_plus_decompressed_size_mod_9800_plus_max_byte_value_times_520,
    zst_compressed_size_mod_659_times_2300_plus_decompressed_size_mod_9900_plus_min_byte_value_times_3400,
)


# --- F1: zst_file_size_mod_653_times_2350_plus_decompressed_size_mod_9800_plus_max_byte_value_times_520 ---

class TestZstFileSizeMod653Times2350PlusDecompressed9800PlusMaxByte520:
    def test_text_returns_702510(self):
        assert zst_file_size_mod_653_times_2350_plus_decompressed_size_mod_9800_plus_max_byte_value_times_520(TEXT) == 702510

    def test_mini_returns_23501(self):
        assert zst_file_size_mod_653_times_2350_plus_decompressed_size_mod_9800_plus_max_byte_value_times_520(MINI) == 23501

    def test_rand_returns_782224(self):
        assert zst_file_size_mod_653_times_2350_plus_decompressed_size_mod_9800_plus_max_byte_value_times_520(RAND) == 782224

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_653_times_2350_plus_decompressed_size_mod_9800_plus_max_byte_value_times_520(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_file_size_mod_653_times_2350_plus_decompressed_size_mod_9800_plus_max_byte_value_times_520(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_file_size_mod_653_times_2350_plus_decompressed_size_mod_9800_plus_max_byte_value_times_520(RAND), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_653_times_2350_plus_decompressed_size_mod_9800_plus_max_byte_value_times_520(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_file_size_mod_653_times_2350_plus_decompressed_size_mod_9800_plus_max_byte_value_times_520(MINI) >= 0

    def test_rand_greater_than_mini(self):
        assert (zst_file_size_mod_653_times_2350_plus_decompressed_size_mod_9800_plus_max_byte_value_times_520(RAND) >
                zst_file_size_mod_653_times_2350_plus_decompressed_size_mod_9800_plus_max_byte_value_times_520(MINI))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_653_times_2350_plus_decompressed_size_mod_9800_plus_max_byte_value_times_520(str(TEXT)) == 702510


# --- F2: zst_compressed_size_mod_659_times_2300_plus_decompressed_size_mod_9900_plus_min_byte_value_times_3400 ---

class TestZstCompressedSizeMod659Times2300PlusDecompressed9900PlusMinByte3400:
    def test_text_returns_734790(self):
        assert zst_compressed_size_mod_659_times_2300_plus_decompressed_size_mod_9900_plus_min_byte_value_times_3400(TEXT) == 734790

    def test_mini_returns_23001(self):
        assert zst_compressed_size_mod_659_times_2300_plus_decompressed_size_mod_9900_plus_min_byte_value_times_3400(MINI) == 23001

    def test_rand_returns_635824(self):
        assert zst_compressed_size_mod_659_times_2300_plus_decompressed_size_mod_9900_plus_min_byte_value_times_3400(RAND) == 635824

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_659_times_2300_plus_decompressed_size_mod_9900_plus_min_byte_value_times_3400(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_compressed_size_mod_659_times_2300_plus_decompressed_size_mod_9900_plus_min_byte_value_times_3400(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_compressed_size_mod_659_times_2300_plus_decompressed_size_mod_9900_plus_min_byte_value_times_3400(RAND), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_659_times_2300_plus_decompressed_size_mod_9900_plus_min_byte_value_times_3400(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_compressed_size_mod_659_times_2300_plus_decompressed_size_mod_9900_plus_min_byte_value_times_3400(MINI) >= 0

    def test_text_greater_than_mini(self):
        assert (zst_compressed_size_mod_659_times_2300_plus_decompressed_size_mod_9900_plus_min_byte_value_times_3400(TEXT) >
                zst_compressed_size_mod_659_times_2300_plus_decompressed_size_mod_9900_plus_min_byte_value_times_3400(MINI))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_659_times_2300_plus_decompressed_size_mod_9900_plus_min_byte_value_times_3400(str(TEXT)) == 734790
