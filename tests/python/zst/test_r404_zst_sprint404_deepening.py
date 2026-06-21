"""Sprint 404 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINI = _ZST / "minimal-synthetic.zst"
RAND = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_617_times_2200_plus_decompressed_size_mod_9200_plus_max_byte_value_times_490,
    zst_compressed_size_mod_619_times_2150_plus_decompressed_size_mod_9300_plus_min_byte_value_times_3250,
)


# --- F1: zst_file_size_mod_617_times_2200_plus_decompressed_size_mod_9200_plus_max_byte_value_times_490 ---

class TestZstFileSizeMod617Times2200PlusDecompressed9200PlusMaxByte490:
    def test_text_returns_658080(self):
        assert zst_file_size_mod_617_times_2200_plus_decompressed_size_mod_9200_plus_max_byte_value_times_490(TEXT) == 658080

    def test_mini_returns_22001(self):
        assert zst_file_size_mod_617_times_2200_plus_decompressed_size_mod_9200_plus_max_byte_value_times_490(MINI) == 22001

    def test_rand_returns_733174(self):
        assert zst_file_size_mod_617_times_2200_plus_decompressed_size_mod_9200_plus_max_byte_value_times_490(RAND) == 733174

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_617_times_2200_plus_decompressed_size_mod_9200_plus_max_byte_value_times_490(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_file_size_mod_617_times_2200_plus_decompressed_size_mod_9200_plus_max_byte_value_times_490(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_file_size_mod_617_times_2200_plus_decompressed_size_mod_9200_plus_max_byte_value_times_490(RAND), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_617_times_2200_plus_decompressed_size_mod_9200_plus_max_byte_value_times_490(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_file_size_mod_617_times_2200_plus_decompressed_size_mod_9200_plus_max_byte_value_times_490(MINI) >= 0

    def test_rand_greater_than_mini(self):
        assert (zst_file_size_mod_617_times_2200_plus_decompressed_size_mod_9200_plus_max_byte_value_times_490(RAND) >
                zst_file_size_mod_617_times_2200_plus_decompressed_size_mod_9200_plus_max_byte_value_times_490(MINI))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_617_times_2200_plus_decompressed_size_mod_9200_plus_max_byte_value_times_490(str(TEXT)) == 658080


# --- F2: zst_compressed_size_mod_619_times_2150_plus_decompressed_size_mod_9300_plus_min_byte_value_times_3250 ---

class TestZstCompressedSizeMod619Times2150PlusDecompressed9300PlusMinByte3250:
    def test_text_returns_689190(self):
        assert zst_compressed_size_mod_619_times_2150_plus_decompressed_size_mod_9300_plus_min_byte_value_times_3250(TEXT) == 689190

    def test_mini_returns_21501(self):
        assert zst_compressed_size_mod_619_times_2150_plus_decompressed_size_mod_9300_plus_min_byte_value_times_3250(MINI) == 21501

    def test_rand_returns_594424(self):
        assert zst_compressed_size_mod_619_times_2150_plus_decompressed_size_mod_9300_plus_min_byte_value_times_3250(RAND) == 594424

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_619_times_2150_plus_decompressed_size_mod_9300_plus_min_byte_value_times_3250(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_compressed_size_mod_619_times_2150_plus_decompressed_size_mod_9300_plus_min_byte_value_times_3250(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_compressed_size_mod_619_times_2150_plus_decompressed_size_mod_9300_plus_min_byte_value_times_3250(RAND), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_619_times_2150_plus_decompressed_size_mod_9300_plus_min_byte_value_times_3250(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_compressed_size_mod_619_times_2150_plus_decompressed_size_mod_9300_plus_min_byte_value_times_3250(MINI) >= 0

    def test_text_greater_than_mini(self):
        assert (zst_compressed_size_mod_619_times_2150_plus_decompressed_size_mod_9300_plus_min_byte_value_times_3250(TEXT) >
                zst_compressed_size_mod_619_times_2150_plus_decompressed_size_mod_9300_plus_min_byte_value_times_3250(MINI))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_619_times_2150_plus_decompressed_size_mod_9300_plus_min_byte_value_times_3250(str(TEXT)) == 689190
