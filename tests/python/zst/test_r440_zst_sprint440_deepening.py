"""Sprint 440 ZST analytics deepening tests."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINI = _ZST / "minimal-synthetic.zst"
RAND = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_773_times_2800_plus_decompressed_size_mod_8600_plus_max_byte_value_times_650,
    zst_compressed_size_mod_787_times_2750_plus_decompressed_size_mod_8500_plus_min_byte_value_times_3900,
)


class TestZstFileSizeMod773Times2800PlusDecompressedMod8600PlusMaxByte650:
    def test_text_returns_840640(self):
        assert zst_file_size_mod_773_times_2800_plus_decompressed_size_mod_8600_plus_max_byte_value_times_650(TEXT) == 840640

    def test_mini_returns_28001(self):
        assert zst_file_size_mod_773_times_2800_plus_decompressed_size_mod_8600_plus_max_byte_value_times_650(MINI) == 28001

    def test_rand_returns_939574(self):
        assert zst_file_size_mod_773_times_2800_plus_decompressed_size_mod_8600_plus_max_byte_value_times_650(RAND) == 939574

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_773_times_2800_plus_decompressed_size_mod_8600_plus_max_byte_value_times_650(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_file_size_mod_773_times_2800_plus_decompressed_size_mod_8600_plus_max_byte_value_times_650(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_file_size_mod_773_times_2800_plus_decompressed_size_mod_8600_plus_max_byte_value_times_650(RAND), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_773_times_2800_plus_decompressed_size_mod_8600_plus_max_byte_value_times_650(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_file_size_mod_773_times_2800_plus_decompressed_size_mod_8600_plus_max_byte_value_times_650(MINI) >= 0

    def test_rand_greater_than_mini(self):
        assert (zst_file_size_mod_773_times_2800_plus_decompressed_size_mod_8600_plus_max_byte_value_times_650(RAND) >
                zst_file_size_mod_773_times_2800_plus_decompressed_size_mod_8600_plus_max_byte_value_times_650(MINI))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_773_times_2800_plus_decompressed_size_mod_8600_plus_max_byte_value_times_650(str(TEXT)) == 840640


class TestZstCompressedSizeMod787Times2750PlusDecompressedMod8500PlusMinByte3900:
    def test_text_returns_873190(self):
        assert zst_compressed_size_mod_787_times_2750_plus_decompressed_size_mod_8500_plus_min_byte_value_times_3900(TEXT) == 873190

    def test_mini_returns_27501(self):
        assert zst_compressed_size_mod_787_times_2750_plus_decompressed_size_mod_8500_plus_min_byte_value_times_3900(MINI) == 27501

    def test_rand_returns_760024(self):
        assert zst_compressed_size_mod_787_times_2750_plus_decompressed_size_mod_8500_plus_min_byte_value_times_3900(RAND) == 760024

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_787_times_2750_plus_decompressed_size_mod_8500_plus_min_byte_value_times_3900(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_compressed_size_mod_787_times_2750_plus_decompressed_size_mod_8500_plus_min_byte_value_times_3900(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_compressed_size_mod_787_times_2750_plus_decompressed_size_mod_8500_plus_min_byte_value_times_3900(RAND), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_787_times_2750_plus_decompressed_size_mod_8500_plus_min_byte_value_times_3900(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_compressed_size_mod_787_times_2750_plus_decompressed_size_mod_8500_plus_min_byte_value_times_3900(MINI) >= 0

    def test_text_greater_than_mini(self):
        assert (zst_compressed_size_mod_787_times_2750_plus_decompressed_size_mod_8500_plus_min_byte_value_times_3900(TEXT) >
                zst_compressed_size_mod_787_times_2750_plus_decompressed_size_mod_8500_plus_min_byte_value_times_3900(MINI))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_787_times_2750_plus_decompressed_size_mod_8500_plus_min_byte_value_times_3900(str(TEXT)) == 873190
