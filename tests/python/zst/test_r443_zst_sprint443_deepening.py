"""Sprint 443 ZST analytics deepening tests."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINI = _ZST / "minimal-synthetic.zst"
RAND = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_797_times_2850_plus_decompressed_size_mod_8700_plus_max_byte_value_times_700,
    zst_compressed_size_mod_809_times_2900_plus_decompressed_size_mod_8800_plus_min_byte_value_times_4000,
)


class TestZstFileSizeMod797Times2850PlusDecompressedMod8700PlusMaxByte700:
    def test_text_returns_860290(self):
        assert zst_file_size_mod_797_times_2850_plus_decompressed_size_mod_8700_plus_max_byte_value_times_700(TEXT) == 860290

    def test_mini_returns_28501(self):
        assert zst_file_size_mod_797_times_2850_plus_decompressed_size_mod_8700_plus_max_byte_value_times_700(MINI) == 28501

    def test_rand_returns_966124(self):
        assert zst_file_size_mod_797_times_2850_plus_decompressed_size_mod_8700_plus_max_byte_value_times_700(RAND) == 966124

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_797_times_2850_plus_decompressed_size_mod_8700_plus_max_byte_value_times_700(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_file_size_mod_797_times_2850_plus_decompressed_size_mod_8700_plus_max_byte_value_times_700(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_file_size_mod_797_times_2850_plus_decompressed_size_mod_8700_plus_max_byte_value_times_700(RAND), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_797_times_2850_plus_decompressed_size_mod_8700_plus_max_byte_value_times_700(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_file_size_mod_797_times_2850_plus_decompressed_size_mod_8700_plus_max_byte_value_times_700(MINI) >= 0

    def test_rand_greater_than_mini(self):
        assert (zst_file_size_mod_797_times_2850_plus_decompressed_size_mod_8700_plus_max_byte_value_times_700(RAND) >
                zst_file_size_mod_797_times_2850_plus_decompressed_size_mod_8700_plus_max_byte_value_times_700(MINI))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_797_times_2850_plus_decompressed_size_mod_8700_plus_max_byte_value_times_700(str(TEXT)) == 860290


class TestZstCompressedSizeMod809Times2900PlusDecompressedMod8800PlusMinByte4000:
    def test_text_returns_917190(self):
        assert zst_compressed_size_mod_809_times_2900_plus_decompressed_size_mod_8800_plus_min_byte_value_times_4000(TEXT) == 917190

    def test_mini_returns_29001(self):
        assert zst_compressed_size_mod_809_times_2900_plus_decompressed_size_mod_8800_plus_min_byte_value_times_4000(MINI) == 29001

    def test_rand_returns_801424(self):
        assert zst_compressed_size_mod_809_times_2900_plus_decompressed_size_mod_8800_plus_min_byte_value_times_4000(RAND) == 801424

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_809_times_2900_plus_decompressed_size_mod_8800_plus_min_byte_value_times_4000(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_compressed_size_mod_809_times_2900_plus_decompressed_size_mod_8800_plus_min_byte_value_times_4000(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_compressed_size_mod_809_times_2900_plus_decompressed_size_mod_8800_plus_min_byte_value_times_4000(RAND), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_809_times_2900_plus_decompressed_size_mod_8800_plus_min_byte_value_times_4000(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_compressed_size_mod_809_times_2900_plus_decompressed_size_mod_8800_plus_min_byte_value_times_4000(MINI) >= 0

    def test_text_greater_than_mini(self):
        assert (zst_compressed_size_mod_809_times_2900_plus_decompressed_size_mod_8800_plus_min_byte_value_times_4000(TEXT) >
                zst_compressed_size_mod_809_times_2900_plus_decompressed_size_mod_8800_plus_min_byte_value_times_4000(MINI))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_809_times_2900_plus_decompressed_size_mod_8800_plus_min_byte_value_times_4000(str(TEXT)) == 917190
