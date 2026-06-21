"""Sprint 410 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINI = _ZST / "minimal-synthetic.zst"
RAND = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_643_times_2300_plus_decompressed_size_mod_9600_plus_max_byte_value_times_510,
    zst_compressed_size_mod_647_times_2250_plus_decompressed_size_mod_9700_plus_min_byte_value_times_3350,
)


# --- F1: zst_file_size_mod_643_times_2300_plus_decompressed_size_mod_9600_plus_max_byte_value_times_510 ---

class TestZstFileSizeMod643Times2300PlusDecompressed9600PlusMaxByte510:
    def test_text_returns_687700(self):
        assert zst_file_size_mod_643_times_2300_plus_decompressed_size_mod_9600_plus_max_byte_value_times_510(TEXT) == 687700

    def test_mini_returns_23001(self):
        assert zst_file_size_mod_643_times_2300_plus_decompressed_size_mod_9600_plus_max_byte_value_times_510(MINI) == 23001

    def test_rand_returns_765874(self):
        assert zst_file_size_mod_643_times_2300_plus_decompressed_size_mod_9600_plus_max_byte_value_times_510(RAND) == 765874

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_643_times_2300_plus_decompressed_size_mod_9600_plus_max_byte_value_times_510(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_file_size_mod_643_times_2300_plus_decompressed_size_mod_9600_plus_max_byte_value_times_510(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_file_size_mod_643_times_2300_plus_decompressed_size_mod_9600_plus_max_byte_value_times_510(RAND), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_643_times_2300_plus_decompressed_size_mod_9600_plus_max_byte_value_times_510(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_file_size_mod_643_times_2300_plus_decompressed_size_mod_9600_plus_max_byte_value_times_510(MINI) >= 0

    def test_rand_greater_than_mini(self):
        assert (zst_file_size_mod_643_times_2300_plus_decompressed_size_mod_9600_plus_max_byte_value_times_510(RAND) >
                zst_file_size_mod_643_times_2300_plus_decompressed_size_mod_9600_plus_max_byte_value_times_510(MINI))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_643_times_2300_plus_decompressed_size_mod_9600_plus_max_byte_value_times_510(str(TEXT)) == 687700


# --- F2: zst_compressed_size_mod_647_times_2250_plus_decompressed_size_mod_9700_plus_min_byte_value_times_3350 ---

class TestZstCompressedSizeMod647Times2250PlusDecompressed9700PlusMinByte3350:
    def test_text_returns_719590(self):
        assert zst_compressed_size_mod_647_times_2250_plus_decompressed_size_mod_9700_plus_min_byte_value_times_3350(TEXT) == 719590

    def test_mini_returns_22501(self):
        assert zst_compressed_size_mod_647_times_2250_plus_decompressed_size_mod_9700_plus_min_byte_value_times_3350(MINI) == 22501

    def test_rand_returns_622024(self):
        assert zst_compressed_size_mod_647_times_2250_plus_decompressed_size_mod_9700_plus_min_byte_value_times_3350(RAND) == 622024

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_647_times_2250_plus_decompressed_size_mod_9700_plus_min_byte_value_times_3350(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_compressed_size_mod_647_times_2250_plus_decompressed_size_mod_9700_plus_min_byte_value_times_3350(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_compressed_size_mod_647_times_2250_plus_decompressed_size_mod_9700_plus_min_byte_value_times_3350(RAND), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_647_times_2250_plus_decompressed_size_mod_9700_plus_min_byte_value_times_3350(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_compressed_size_mod_647_times_2250_plus_decompressed_size_mod_9700_plus_min_byte_value_times_3350(MINI) >= 0

    def test_text_greater_than_mini(self):
        assert (zst_compressed_size_mod_647_times_2250_plus_decompressed_size_mod_9700_plus_min_byte_value_times_3350(TEXT) >
                zst_compressed_size_mod_647_times_2250_plus_decompressed_size_mod_9700_plus_min_byte_value_times_3350(MINI))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_647_times_2250_plus_decompressed_size_mod_9700_plus_min_byte_value_times_3350(str(TEXT)) == 719590
