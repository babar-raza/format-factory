"""Sprint 350 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINI = _ZST / "minimal-synthetic.zst"
RAND = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_389_times_1550_plus_decompressed_size_mod_5600_plus_max_byte_value_times_310,
    zst_compressed_size_mod_397_times_1475_plus_decompressed_size_mod_5700_plus_min_byte_value_times_2350,
)


# --- F1: zst_file_size_mod_389_times_1550_plus_decompressed_size_mod_5600_plus_max_byte_value_times_310 ---

class TestZstFileSizeMod389Times1550PlusDecompressed5600PlusMaxByte310:
    def test_text_returns_459500(self):
        assert zst_file_size_mod_389_times_1550_plus_decompressed_size_mod_5600_plus_max_byte_value_times_310(TEXT) == 459500

    def test_mini_returns_15501(self):
        assert zst_file_size_mod_389_times_1550_plus_decompressed_size_mod_5600_plus_max_byte_value_times_310(MINI) == 15501

    def test_rand_returns_507874(self):
        assert zst_file_size_mod_389_times_1550_plus_decompressed_size_mod_5600_plus_max_byte_value_times_310(RAND) == 507874

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_389_times_1550_plus_decompressed_size_mod_5600_plus_max_byte_value_times_310(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_file_size_mod_389_times_1550_plus_decompressed_size_mod_5600_plus_max_byte_value_times_310(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_file_size_mod_389_times_1550_plus_decompressed_size_mod_5600_plus_max_byte_value_times_310(RAND), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_389_times_1550_plus_decompressed_size_mod_5600_plus_max_byte_value_times_310(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_file_size_mod_389_times_1550_plus_decompressed_size_mod_5600_plus_max_byte_value_times_310(MINI) >= 0

    def test_rand_greater_than_mini(self):
        assert (zst_file_size_mod_389_times_1550_plus_decompressed_size_mod_5600_plus_max_byte_value_times_310(RAND) >
                zst_file_size_mod_389_times_1550_plus_decompressed_size_mod_5600_plus_max_byte_value_times_310(MINI))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_389_times_1550_plus_decompressed_size_mod_5600_plus_max_byte_value_times_310(str(TEXT)) == 459500


# --- F2: zst_compressed_size_mod_397_times_1475_plus_decompressed_size_mod_5700_plus_min_byte_value_times_2350 ---

class TestZstCompressedSizeMod397Times1475PlusDecompressed5700PlusMinByte2350:
    def test_text_returns_476790(self):
        assert zst_compressed_size_mod_397_times_1475_plus_decompressed_size_mod_5700_plus_min_byte_value_times_2350(TEXT) == 476790

    def test_mini_returns_14751(self):
        assert zst_compressed_size_mod_397_times_1475_plus_decompressed_size_mod_5700_plus_min_byte_value_times_2350(MINI) == 14751

    def test_rand_returns_408124(self):
        assert zst_compressed_size_mod_397_times_1475_plus_decompressed_size_mod_5700_plus_min_byte_value_times_2350(RAND) == 408124

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_397_times_1475_plus_decompressed_size_mod_5700_plus_min_byte_value_times_2350(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_compressed_size_mod_397_times_1475_plus_decompressed_size_mod_5700_plus_min_byte_value_times_2350(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_compressed_size_mod_397_times_1475_plus_decompressed_size_mod_5700_plus_min_byte_value_times_2350(RAND), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_397_times_1475_plus_decompressed_size_mod_5700_plus_min_byte_value_times_2350(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_compressed_size_mod_397_times_1475_plus_decompressed_size_mod_5700_plus_min_byte_value_times_2350(MINI) >= 0

    def test_rand_greater_than_mini(self):
        assert (zst_compressed_size_mod_397_times_1475_plus_decompressed_size_mod_5700_plus_min_byte_value_times_2350(RAND) >
                zst_compressed_size_mod_397_times_1475_plus_decompressed_size_mod_5700_plus_min_byte_value_times_2350(MINI))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_397_times_1475_plus_decompressed_size_mod_5700_plus_min_byte_value_times_2350(str(TEXT)) == 476790
