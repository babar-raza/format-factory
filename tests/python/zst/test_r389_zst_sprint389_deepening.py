"""Sprint 389 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINI = _ZST / "minimal-synthetic.zst"
RAND = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_563_times_2075_plus_decompressed_size_mod_8200_plus_max_byte_value_times_440,
    zst_compressed_size_mod_569_times_2025_plus_decompressed_size_mod_8300_plus_min_byte_value_times_3000,
)


# --- F1: zst_file_size_mod_563_times_2075_plus_decompressed_size_mod_8200_plus_max_byte_value_times_440 ---

class TestZstFileSizeMod563Times2075PlusDecompressed8200PlusMaxByte440:
    def test_text_returns_618030(self):
        assert zst_file_size_mod_563_times_2075_plus_decompressed_size_mod_8200_plus_max_byte_value_times_440(TEXT) == 618030

    def test_mini_returns_20751(self):
        assert zst_file_size_mod_563_times_2075_plus_decompressed_size_mod_8200_plus_max_byte_value_times_440(MINI) == 20751

    def test_rand_returns_685924(self):
        assert zst_file_size_mod_563_times_2075_plus_decompressed_size_mod_8200_plus_max_byte_value_times_440(RAND) == 685924

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_563_times_2075_plus_decompressed_size_mod_8200_plus_max_byte_value_times_440(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_file_size_mod_563_times_2075_plus_decompressed_size_mod_8200_plus_max_byte_value_times_440(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_file_size_mod_563_times_2075_plus_decompressed_size_mod_8200_plus_max_byte_value_times_440(RAND), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_563_times_2075_plus_decompressed_size_mod_8200_plus_max_byte_value_times_440(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_file_size_mod_563_times_2075_plus_decompressed_size_mod_8200_plus_max_byte_value_times_440(MINI) >= 0

    def test_rand_greater_than_mini(self):
        assert (zst_file_size_mod_563_times_2075_plus_decompressed_size_mod_8200_plus_max_byte_value_times_440(RAND) >
                zst_file_size_mod_563_times_2075_plus_decompressed_size_mod_8200_plus_max_byte_value_times_440(MINI))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_563_times_2075_plus_decompressed_size_mod_8200_plus_max_byte_value_times_440(str(TEXT)) == 618030


# --- F2: zst_compressed_size_mod_569_times_2025_plus_decompressed_size_mod_8300_plus_min_byte_value_times_3000 ---

class TestZstCompressedSizeMod569Times2025PlusDecompressed8300PlusMinByte3000:
    def test_text_returns_647190(self):
        assert zst_compressed_size_mod_569_times_2025_plus_decompressed_size_mod_8300_plus_min_byte_value_times_3000(TEXT) == 647190

    def test_mini_returns_20251(self):
        assert zst_compressed_size_mod_569_times_2025_plus_decompressed_size_mod_8300_plus_min_byte_value_times_3000(MINI) == 20251

    def test_rand_returns_559924(self):
        assert zst_compressed_size_mod_569_times_2025_plus_decompressed_size_mod_8300_plus_min_byte_value_times_3000(RAND) == 559924

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_569_times_2025_plus_decompressed_size_mod_8300_plus_min_byte_value_times_3000(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_compressed_size_mod_569_times_2025_plus_decompressed_size_mod_8300_plus_min_byte_value_times_3000(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_compressed_size_mod_569_times_2025_plus_decompressed_size_mod_8300_plus_min_byte_value_times_3000(RAND), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_569_times_2025_plus_decompressed_size_mod_8300_plus_min_byte_value_times_3000(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_compressed_size_mod_569_times_2025_plus_decompressed_size_mod_8300_plus_min_byte_value_times_3000(MINI) >= 0

    def test_text_greater_than_mini(self):
        assert (zst_compressed_size_mod_569_times_2025_plus_decompressed_size_mod_8300_plus_min_byte_value_times_3000(TEXT) >
                zst_compressed_size_mod_569_times_2025_plus_decompressed_size_mod_8300_plus_min_byte_value_times_3000(MINI))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_569_times_2025_plus_decompressed_size_mod_8300_plus_min_byte_value_times_3000(str(TEXT)) == 647190
