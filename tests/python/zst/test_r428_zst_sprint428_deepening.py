"""Sprint 428 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINI = _ZST / "minimal-synthetic.zst"
RAND = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_727_times_2600_plus_decompressed_size_mod_9100_plus_max_byte_value_times_570,
    zst_compressed_size_mod_733_times_2550_plus_decompressed_size_mod_9000_plus_min_byte_value_times_3650,
)


# --- F1: zst_file_size_mod_727_times_2600_plus_decompressed_size_mod_9100_plus_max_byte_value_times_570 ---

class TestZstFileSizeMod727Times2600PlusDecompressedMod9100PlusMaxByte570:
    def test_text_returns_776560(self):
        assert zst_file_size_mod_727_times_2600_plus_decompressed_size_mod_9100_plus_max_byte_value_times_570(TEXT) == 776560

    def test_mini_returns_26001(self):
        assert zst_file_size_mod_727_times_2600_plus_decompressed_size_mod_9100_plus_max_byte_value_times_570(MINI) == 26001

    def test_rand_returns_863974(self):
        assert zst_file_size_mod_727_times_2600_plus_decompressed_size_mod_9100_plus_max_byte_value_times_570(RAND) == 863974

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_727_times_2600_plus_decompressed_size_mod_9100_plus_max_byte_value_times_570(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_file_size_mod_727_times_2600_plus_decompressed_size_mod_9100_plus_max_byte_value_times_570(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_file_size_mod_727_times_2600_plus_decompressed_size_mod_9100_plus_max_byte_value_times_570(RAND), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_727_times_2600_plus_decompressed_size_mod_9100_plus_max_byte_value_times_570(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_file_size_mod_727_times_2600_plus_decompressed_size_mod_9100_plus_max_byte_value_times_570(MINI) >= 0

    def test_rand_greater_than_mini(self):
        assert (zst_file_size_mod_727_times_2600_plus_decompressed_size_mod_9100_plus_max_byte_value_times_570(RAND) >
                zst_file_size_mod_727_times_2600_plus_decompressed_size_mod_9100_plus_max_byte_value_times_570(MINI))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_727_times_2600_plus_decompressed_size_mod_9100_plus_max_byte_value_times_570(str(TEXT)) == 776560


# --- F2: zst_compressed_size_mod_733_times_2550_plus_decompressed_size_mod_9000_plus_min_byte_value_times_3650 ---

class TestZstCompressedSizeMod733Times2550PlusDecompressedMod9000PlusMinByte3650:
    def test_text_returns_810790(self):
        assert zst_compressed_size_mod_733_times_2550_plus_decompressed_size_mod_9000_plus_min_byte_value_times_3650(TEXT) == 810790

    def test_mini_returns_25501(self):
        assert zst_compressed_size_mod_733_times_2550_plus_decompressed_size_mod_9000_plus_min_byte_value_times_3650(MINI) == 25501

    def test_rand_returns_704824(self):
        assert zst_compressed_size_mod_733_times_2550_plus_decompressed_size_mod_9000_plus_min_byte_value_times_3650(RAND) == 704824

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_733_times_2550_plus_decompressed_size_mod_9000_plus_min_byte_value_times_3650(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_compressed_size_mod_733_times_2550_plus_decompressed_size_mod_9000_plus_min_byte_value_times_3650(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_compressed_size_mod_733_times_2550_plus_decompressed_size_mod_9000_plus_min_byte_value_times_3650(RAND), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_733_times_2550_plus_decompressed_size_mod_9000_plus_min_byte_value_times_3650(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_compressed_size_mod_733_times_2550_plus_decompressed_size_mod_9000_plus_min_byte_value_times_3650(MINI) >= 0

    def test_text_greater_than_mini(self):
        assert (zst_compressed_size_mod_733_times_2550_plus_decompressed_size_mod_9000_plus_min_byte_value_times_3650(TEXT) >
                zst_compressed_size_mod_733_times_2550_plus_decompressed_size_mod_9000_plus_min_byte_value_times_3650(MINI))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_733_times_2550_plus_decompressed_size_mod_9000_plus_min_byte_value_times_3650(str(TEXT)) == 810790
