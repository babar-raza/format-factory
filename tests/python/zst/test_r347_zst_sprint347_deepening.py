"""Sprint 347 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINI = _ZST / "minimal-synthetic.zst"
RAND = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_379_times_1500_plus_decompressed_size_mod_5400_plus_max_byte_value_times_300,
    zst_compressed_size_mod_383_times_1425_plus_decompressed_size_mod_5500_plus_min_byte_value_times_2300,
)


# --- F1: zst_file_size_mod_379_times_1500_plus_decompressed_size_mod_5400_plus_max_byte_value_times_300 ---

class TestZstFileSizeMod379Times1500PlusDecompressed5400PlusMaxByte300:
    def test_text_returns_444690(self):
        assert zst_file_size_mod_379_times_1500_plus_decompressed_size_mod_5400_plus_max_byte_value_times_300(TEXT) == 444690

    def test_mini_returns_15001(self):
        assert zst_file_size_mod_379_times_1500_plus_decompressed_size_mod_5400_plus_max_byte_value_times_300(MINI) == 15001

    def test_rand_returns_491524(self):
        assert zst_file_size_mod_379_times_1500_plus_decompressed_size_mod_5400_plus_max_byte_value_times_300(RAND) == 491524

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_379_times_1500_plus_decompressed_size_mod_5400_plus_max_byte_value_times_300(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_file_size_mod_379_times_1500_plus_decompressed_size_mod_5400_plus_max_byte_value_times_300(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_file_size_mod_379_times_1500_plus_decompressed_size_mod_5400_plus_max_byte_value_times_300(RAND), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_379_times_1500_plus_decompressed_size_mod_5400_plus_max_byte_value_times_300(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_file_size_mod_379_times_1500_plus_decompressed_size_mod_5400_plus_max_byte_value_times_300(MINI) >= 0

    def test_rand_greater_than_mini(self):
        assert (zst_file_size_mod_379_times_1500_plus_decompressed_size_mod_5400_plus_max_byte_value_times_300(RAND) >
                zst_file_size_mod_379_times_1500_plus_decompressed_size_mod_5400_plus_max_byte_value_times_300(MINI))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_379_times_1500_plus_decompressed_size_mod_5400_plus_max_byte_value_times_300(str(TEXT)) == 444690


# --- F2: zst_compressed_size_mod_383_times_1425_plus_decompressed_size_mod_5500_plus_min_byte_value_times_2300 ---

class TestZstCompressedSizeMod383Times1425PlusDecompressed5500PlusMinByte2300:
    def test_text_returns_461590(self):
        assert zst_compressed_size_mod_383_times_1425_plus_decompressed_size_mod_5500_plus_min_byte_value_times_2300(TEXT) == 461590

    def test_mini_returns_14251(self):
        assert zst_compressed_size_mod_383_times_1425_plus_decompressed_size_mod_5500_plus_min_byte_value_times_2300(MINI) == 14251

    def test_rand_returns_394324(self):
        assert zst_compressed_size_mod_383_times_1425_plus_decompressed_size_mod_5500_plus_min_byte_value_times_2300(RAND) == 394324

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_383_times_1425_plus_decompressed_size_mod_5500_plus_min_byte_value_times_2300(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_compressed_size_mod_383_times_1425_plus_decompressed_size_mod_5500_plus_min_byte_value_times_2300(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_compressed_size_mod_383_times_1425_plus_decompressed_size_mod_5500_plus_min_byte_value_times_2300(RAND), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_383_times_1425_plus_decompressed_size_mod_5500_plus_min_byte_value_times_2300(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_compressed_size_mod_383_times_1425_plus_decompressed_size_mod_5500_plus_min_byte_value_times_2300(MINI) >= 0

    def test_rand_greater_than_mini(self):
        assert (zst_compressed_size_mod_383_times_1425_plus_decompressed_size_mod_5500_plus_min_byte_value_times_2300(RAND) >
                zst_compressed_size_mod_383_times_1425_plus_decompressed_size_mod_5500_plus_min_byte_value_times_2300(MINI))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_383_times_1425_plus_decompressed_size_mod_5500_plus_min_byte_value_times_2300(str(TEXT)) == 461590
