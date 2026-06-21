"""Sprint 425 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINI = _ZST / "minimal-synthetic.zst"
RAND = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_709_times_2550_plus_decompressed_size_mod_9300_plus_max_byte_value_times_560,
    zst_compressed_size_mod_719_times_2500_plus_decompressed_size_mod_9200_plus_min_byte_value_times_3600,
)


# --- F1: zst_file_size_mod_709_times_2550_plus_decompressed_size_mod_9300_plus_max_byte_value_times_560 ---

class TestZstFileSizeMod709Times2550PlusDecompressedMod9300PlusMaxByte560:
    def test_text_returns_761750(self):
        assert zst_file_size_mod_709_times_2550_plus_decompressed_size_mod_9300_plus_max_byte_value_times_560(TEXT) == 761750

    def test_mini_returns_25501(self):
        assert zst_file_size_mod_709_times_2550_plus_decompressed_size_mod_9300_plus_max_byte_value_times_560(MINI) == 25501

    def test_rand_returns_847624(self):
        assert zst_file_size_mod_709_times_2550_plus_decompressed_size_mod_9300_plus_max_byte_value_times_560(RAND) == 847624

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_709_times_2550_plus_decompressed_size_mod_9300_plus_max_byte_value_times_560(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_file_size_mod_709_times_2550_plus_decompressed_size_mod_9300_plus_max_byte_value_times_560(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_file_size_mod_709_times_2550_plus_decompressed_size_mod_9300_plus_max_byte_value_times_560(RAND), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_709_times_2550_plus_decompressed_size_mod_9300_plus_max_byte_value_times_560(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_file_size_mod_709_times_2550_plus_decompressed_size_mod_9300_plus_max_byte_value_times_560(MINI) >= 0

    def test_rand_greater_than_mini(self):
        assert (zst_file_size_mod_709_times_2550_plus_decompressed_size_mod_9300_plus_max_byte_value_times_560(RAND) >
                zst_file_size_mod_709_times_2550_plus_decompressed_size_mod_9300_plus_max_byte_value_times_560(MINI))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_709_times_2550_plus_decompressed_size_mod_9300_plus_max_byte_value_times_560(str(TEXT)) == 761750


# --- F2: zst_compressed_size_mod_719_times_2500_plus_decompressed_size_mod_9200_plus_min_byte_value_times_3600 ---

class TestZstCompressedSizeMod719Times2500PlusDecompressedMod9200PlusMinByte3600:
    def test_text_returns_795590(self):
        assert zst_compressed_size_mod_719_times_2500_plus_decompressed_size_mod_9200_plus_min_byte_value_times_3600(TEXT) == 795590

    def test_mini_returns_25001(self):
        assert zst_compressed_size_mod_719_times_2500_plus_decompressed_size_mod_9200_plus_min_byte_value_times_3600(MINI) == 25001

    def test_rand_returns_691024(self):
        assert zst_compressed_size_mod_719_times_2500_plus_decompressed_size_mod_9200_plus_min_byte_value_times_3600(RAND) == 691024

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_719_times_2500_plus_decompressed_size_mod_9200_plus_min_byte_value_times_3600(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_compressed_size_mod_719_times_2500_plus_decompressed_size_mod_9200_plus_min_byte_value_times_3600(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_compressed_size_mod_719_times_2500_plus_decompressed_size_mod_9200_plus_min_byte_value_times_3600(RAND), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_719_times_2500_plus_decompressed_size_mod_9200_plus_min_byte_value_times_3600(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_compressed_size_mod_719_times_2500_plus_decompressed_size_mod_9200_plus_min_byte_value_times_3600(MINI) >= 0

    def test_text_greater_than_mini(self):
        assert (zst_compressed_size_mod_719_times_2500_plus_decompressed_size_mod_9200_plus_min_byte_value_times_3600(TEXT) >
                zst_compressed_size_mod_719_times_2500_plus_decompressed_size_mod_9200_plus_min_byte_value_times_3600(MINI))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_719_times_2500_plus_decompressed_size_mod_9200_plus_min_byte_value_times_3600(str(TEXT)) == 795590
