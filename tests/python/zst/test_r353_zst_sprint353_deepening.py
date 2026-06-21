"""Sprint 353 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINI = _ZST / "minimal-synthetic.zst"
RAND = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_401_times_1600_plus_decompressed_size_mod_5800_plus_max_byte_value_times_320,
    zst_compressed_size_mod_409_times_1525_plus_decompressed_size_mod_5900_plus_min_byte_value_times_2400,
)


# --- F1: zst_file_size_mod_401_times_1600_plus_decompressed_size_mod_5800_plus_max_byte_value_times_320 ---

class TestZstFileSizeMod401Times1600PlusDecompressed5800PlusMaxByte320:
    def test_text_returns_474310(self):
        assert zst_file_size_mod_401_times_1600_plus_decompressed_size_mod_5800_plus_max_byte_value_times_320(TEXT) == 474310

    def test_mini_returns_16001(self):
        assert zst_file_size_mod_401_times_1600_plus_decompressed_size_mod_5800_plus_max_byte_value_times_320(MINI) == 16001

    def test_rand_returns_524224(self):
        assert zst_file_size_mod_401_times_1600_plus_decompressed_size_mod_5800_plus_max_byte_value_times_320(RAND) == 524224

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_401_times_1600_plus_decompressed_size_mod_5800_plus_max_byte_value_times_320(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_file_size_mod_401_times_1600_plus_decompressed_size_mod_5800_plus_max_byte_value_times_320(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_file_size_mod_401_times_1600_plus_decompressed_size_mod_5800_plus_max_byte_value_times_320(RAND), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_401_times_1600_plus_decompressed_size_mod_5800_plus_max_byte_value_times_320(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_file_size_mod_401_times_1600_plus_decompressed_size_mod_5800_plus_max_byte_value_times_320(MINI) >= 0

    def test_rand_greater_than_mini(self):
        assert (zst_file_size_mod_401_times_1600_plus_decompressed_size_mod_5800_plus_max_byte_value_times_320(RAND) >
                zst_file_size_mod_401_times_1600_plus_decompressed_size_mod_5800_plus_max_byte_value_times_320(MINI))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_401_times_1600_plus_decompressed_size_mod_5800_plus_max_byte_value_times_320(str(TEXT)) == 474310


# --- F2: zst_compressed_size_mod_409_times_1525_plus_decompressed_size_mod_5900_plus_min_byte_value_times_2400 ---

class TestZstCompressedSizeMod409Times1525PlusDecompressed5900PlusMinByte2400:
    def test_text_returns_491990(self):
        assert zst_compressed_size_mod_409_times_1525_plus_decompressed_size_mod_5900_plus_min_byte_value_times_2400(TEXT) == 491990

    def test_mini_returns_15251(self):
        assert zst_compressed_size_mod_409_times_1525_plus_decompressed_size_mod_5900_plus_min_byte_value_times_2400(MINI) == 15251

    def test_rand_returns_421924(self):
        assert zst_compressed_size_mod_409_times_1525_plus_decompressed_size_mod_5900_plus_min_byte_value_times_2400(RAND) == 421924

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_409_times_1525_plus_decompressed_size_mod_5900_plus_min_byte_value_times_2400(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_compressed_size_mod_409_times_1525_plus_decompressed_size_mod_5900_plus_min_byte_value_times_2400(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_compressed_size_mod_409_times_1525_plus_decompressed_size_mod_5900_plus_min_byte_value_times_2400(RAND), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_409_times_1525_plus_decompressed_size_mod_5900_plus_min_byte_value_times_2400(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_compressed_size_mod_409_times_1525_plus_decompressed_size_mod_5900_plus_min_byte_value_times_2400(MINI) >= 0

    def test_rand_greater_than_mini(self):
        assert (zst_compressed_size_mod_409_times_1525_plus_decompressed_size_mod_5900_plus_min_byte_value_times_2400(RAND) >
                zst_compressed_size_mod_409_times_1525_plus_decompressed_size_mod_5900_plus_min_byte_value_times_2400(MINI))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_409_times_1525_plus_decompressed_size_mod_5900_plus_min_byte_value_times_2400(str(TEXT)) == 491990
