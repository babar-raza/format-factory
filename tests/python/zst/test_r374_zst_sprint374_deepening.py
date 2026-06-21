"""Sprint 374 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINI = _ZST / "minimal-synthetic.zst"
RAND = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_487_times_1950_plus_decompressed_size_mod_7200_plus_max_byte_value_times_390,
    zst_compressed_size_mod_491_times_1875_plus_decompressed_size_mod_7300_plus_min_byte_value_times_2750,
)


# --- F1: zst_file_size_mod_487_times_1950_plus_decompressed_size_mod_7200_plus_max_byte_value_times_390 ---

class TestZstFileSizeMod487Times1950PlusDecompressed7200PlusMaxByte390:
    def test_text_returns_577980(self):
        assert zst_file_size_mod_487_times_1950_plus_decompressed_size_mod_7200_plus_max_byte_value_times_390(TEXT) == 577980

    def test_mini_returns_19501(self):
        assert zst_file_size_mod_487_times_1950_plus_decompressed_size_mod_7200_plus_max_byte_value_times_390(MINI) == 19501

    def test_rand_returns_638674(self):
        assert zst_file_size_mod_487_times_1950_plus_decompressed_size_mod_7200_plus_max_byte_value_times_390(RAND) == 638674

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_487_times_1950_plus_decompressed_size_mod_7200_plus_max_byte_value_times_390(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_file_size_mod_487_times_1950_plus_decompressed_size_mod_7200_plus_max_byte_value_times_390(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_file_size_mod_487_times_1950_plus_decompressed_size_mod_7200_plus_max_byte_value_times_390(RAND), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_487_times_1950_plus_decompressed_size_mod_7200_plus_max_byte_value_times_390(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_file_size_mod_487_times_1950_plus_decompressed_size_mod_7200_plus_max_byte_value_times_390(MINI) >= 0

    def test_rand_greater_than_mini(self):
        assert (zst_file_size_mod_487_times_1950_plus_decompressed_size_mod_7200_plus_max_byte_value_times_390(RAND) >
                zst_file_size_mod_487_times_1950_plus_decompressed_size_mod_7200_plus_max_byte_value_times_390(MINI))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_487_times_1950_plus_decompressed_size_mod_7200_plus_max_byte_value_times_390(str(TEXT)) == 577980


# --- F2: zst_compressed_size_mod_491_times_1875_plus_decompressed_size_mod_7300_plus_min_byte_value_times_2750 ---

class TestZstCompressedSizeMod491Times1875PlusDecompressed7300PlusMinByte2750:
    def test_text_returns_598390(self):
        assert zst_compressed_size_mod_491_times_1875_plus_decompressed_size_mod_7300_plus_min_byte_value_times_2750(TEXT) == 598390

    def test_mini_returns_18751(self):
        assert zst_compressed_size_mod_491_times_1875_plus_decompressed_size_mod_7300_plus_min_byte_value_times_2750(MINI) == 18751

    def test_rand_returns_518524(self):
        assert zst_compressed_size_mod_491_times_1875_plus_decompressed_size_mod_7300_plus_min_byte_value_times_2750(RAND) == 518524

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_491_times_1875_plus_decompressed_size_mod_7300_plus_min_byte_value_times_2750(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_compressed_size_mod_491_times_1875_plus_decompressed_size_mod_7300_plus_min_byte_value_times_2750(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_compressed_size_mod_491_times_1875_plus_decompressed_size_mod_7300_plus_min_byte_value_times_2750(RAND), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_491_times_1875_plus_decompressed_size_mod_7300_plus_min_byte_value_times_2750(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_compressed_size_mod_491_times_1875_plus_decompressed_size_mod_7300_plus_min_byte_value_times_2750(MINI) >= 0

    def test_text_greater_than_mini(self):
        assert (zst_compressed_size_mod_491_times_1875_plus_decompressed_size_mod_7300_plus_min_byte_value_times_2750(TEXT) >
                zst_compressed_size_mod_491_times_1875_plus_decompressed_size_mod_7300_plus_min_byte_value_times_2750(MINI))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_491_times_1875_plus_decompressed_size_mod_7300_plus_min_byte_value_times_2750(str(TEXT)) == 598390
