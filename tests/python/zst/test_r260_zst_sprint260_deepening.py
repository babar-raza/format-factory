"""Sprint 260 ZST analytics deepening tests.

F1: zst_file_size_mod_37_times_100_plus_decompressed_size_mod_400_plus_max_byte_value_times_25
    TEXT=4715, MINIMAL=1001, RANDOM=8299
F2: zst_compressed_size_mod_41_times_200_plus_decompressed_size_mod_600_plus_min_byte_value_times_100
    TEXT=8790, MINIMAL=2001, RANDOM=6424
"""
from pathlib import Path

from src.python.zst import (
    zst_file_size_mod_37_times_100_plus_decompressed_size_mod_400_plus_max_byte_value_times_25,
    zst_compressed_size_mod_41_times_200_plus_decompressed_size_mod_600_plus_min_byte_value_times_100,
)

_REPO = Path(__file__).parent.parent.parent.parent
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"

TEXT = str(_ZST / "text-compressed.zst")
MINIMAL = str(_ZST / "minimal-synthetic.zst")
RANDOM = str(_ZST / "random-data.zst")


class TestF1Text:
    def test_returns_int(self):
        assert isinstance(zst_file_size_mod_37_times_100_plus_decompressed_size_mod_400_plus_max_byte_value_times_25(TEXT), int)

    def test_value(self):
        assert zst_file_size_mod_37_times_100_plus_decompressed_size_mod_400_plus_max_byte_value_times_25(TEXT) == 4715

    def test_nonnegative(self):
        assert zst_file_size_mod_37_times_100_plus_decompressed_size_mod_400_plus_max_byte_value_times_25(TEXT) >= 0


class TestF1Minimal:
    def test_returns_int(self):
        assert isinstance(zst_file_size_mod_37_times_100_plus_decompressed_size_mod_400_plus_max_byte_value_times_25(MINIMAL), int)

    def test_value(self):
        assert zst_file_size_mod_37_times_100_plus_decompressed_size_mod_400_plus_max_byte_value_times_25(MINIMAL) == 1001

    def test_nonnegative(self):
        assert zst_file_size_mod_37_times_100_plus_decompressed_size_mod_400_plus_max_byte_value_times_25(MINIMAL) >= 0


class TestF1Random:
    def test_returns_int(self):
        assert isinstance(zst_file_size_mod_37_times_100_plus_decompressed_size_mod_400_plus_max_byte_value_times_25(RANDOM), int)

    def test_value(self):
        assert zst_file_size_mod_37_times_100_plus_decompressed_size_mod_400_plus_max_byte_value_times_25(RANDOM) == 8299

    def test_nonnegative(self):
        assert zst_file_size_mod_37_times_100_plus_decompressed_size_mod_400_plus_max_byte_value_times_25(RANDOM) >= 0

    def test_random_greater_than_text(self):
        assert (zst_file_size_mod_37_times_100_plus_decompressed_size_mod_400_plus_max_byte_value_times_25(RANDOM) >
                zst_file_size_mod_37_times_100_plus_decompressed_size_mod_400_plus_max_byte_value_times_25(TEXT))


class TestF2Text:
    def test_returns_int(self):
        assert isinstance(zst_compressed_size_mod_41_times_200_plus_decompressed_size_mod_600_plus_min_byte_value_times_100(TEXT), int)

    def test_value(self):
        assert zst_compressed_size_mod_41_times_200_plus_decompressed_size_mod_600_plus_min_byte_value_times_100(TEXT) == 8790

    def test_nonnegative(self):
        assert zst_compressed_size_mod_41_times_200_plus_decompressed_size_mod_600_plus_min_byte_value_times_100(TEXT) >= 0

    def test_text_greater_than_random(self):
        assert (zst_compressed_size_mod_41_times_200_plus_decompressed_size_mod_600_plus_min_byte_value_times_100(TEXT) >
                zst_compressed_size_mod_41_times_200_plus_decompressed_size_mod_600_plus_min_byte_value_times_100(RANDOM))


class TestF2Minimal:
    def test_returns_int(self):
        assert isinstance(zst_compressed_size_mod_41_times_200_plus_decompressed_size_mod_600_plus_min_byte_value_times_100(MINIMAL), int)

    def test_value(self):
        assert zst_compressed_size_mod_41_times_200_plus_decompressed_size_mod_600_plus_min_byte_value_times_100(MINIMAL) == 2001

    def test_nonnegative(self):
        assert zst_compressed_size_mod_41_times_200_plus_decompressed_size_mod_600_plus_min_byte_value_times_100(MINIMAL) >= 0


class TestF2Random:
    def test_returns_int(self):
        assert isinstance(zst_compressed_size_mod_41_times_200_plus_decompressed_size_mod_600_plus_min_byte_value_times_100(RANDOM), int)

    def test_value(self):
        assert zst_compressed_size_mod_41_times_200_plus_decompressed_size_mod_600_plus_min_byte_value_times_100(RANDOM) == 6424

    def test_nonnegative(self):
        assert zst_compressed_size_mod_41_times_200_plus_decompressed_size_mod_600_plus_min_byte_value_times_100(RANDOM) >= 0
