"""Sprint 449 ZST analytics deepening tests."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINI = _ZST / "minimal-synthetic.zst"
RAND = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_823_times_3050_plus_decompressed_size_mod_9100_plus_max_byte_value_times_800,
    zst_compressed_size_mod_827_times_3100_plus_decompressed_size_mod_9200_plus_min_byte_value_times_4200,
)


class TestZstFileSizeMod823Times3050PlusDecompressedMod9100PlusMaxByte800:
    def test_text_returns_926790(self):
        assert zst_file_size_mod_823_times_3050_plus_decompressed_size_mod_9100_plus_max_byte_value_times_800(TEXT) == 926790

    def test_mini_returns_30501(self):
        assert zst_file_size_mod_823_times_3050_plus_decompressed_size_mod_9100_plus_max_byte_value_times_800(MINI) == 30501

    def test_rand_returns_1046824(self):
        assert zst_file_size_mod_823_times_3050_plus_decompressed_size_mod_9100_plus_max_byte_value_times_800(RAND) == 1046824

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_823_times_3050_plus_decompressed_size_mod_9100_plus_max_byte_value_times_800(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_file_size_mod_823_times_3050_plus_decompressed_size_mod_9100_plus_max_byte_value_times_800(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_file_size_mod_823_times_3050_plus_decompressed_size_mod_9100_plus_max_byte_value_times_800(RAND), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_823_times_3050_plus_decompressed_size_mod_9100_plus_max_byte_value_times_800(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_file_size_mod_823_times_3050_plus_decompressed_size_mod_9100_plus_max_byte_value_times_800(MINI) >= 0

    def test_rand_greater_than_mini(self):
        assert (zst_file_size_mod_823_times_3050_plus_decompressed_size_mod_9100_plus_max_byte_value_times_800(RAND) >
                zst_file_size_mod_823_times_3050_plus_decompressed_size_mod_9100_plus_max_byte_value_times_800(MINI))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_823_times_3050_plus_decompressed_size_mod_9100_plus_max_byte_value_times_800(str(TEXT)) == 926790


class TestZstCompressedSizeMod827Times3100PlusDecompressedMod9200PlusMinByte4200:
    def test_text_returns_977990(self):
        assert zst_compressed_size_mod_827_times_3100_plus_decompressed_size_mod_9200_plus_min_byte_value_times_4200(TEXT) == 977990

    def test_mini_returns_31001(self):
        assert zst_compressed_size_mod_827_times_3100_plus_decompressed_size_mod_9200_plus_min_byte_value_times_4200(MINI) == 31001

    def test_rand_returns_856624(self):
        assert zst_compressed_size_mod_827_times_3100_plus_decompressed_size_mod_9200_plus_min_byte_value_times_4200(RAND) == 856624

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_827_times_3100_plus_decompressed_size_mod_9200_plus_min_byte_value_times_4200(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_compressed_size_mod_827_times_3100_plus_decompressed_size_mod_9200_plus_min_byte_value_times_4200(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_compressed_size_mod_827_times_3100_plus_decompressed_size_mod_9200_plus_min_byte_value_times_4200(RAND), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_827_times_3100_plus_decompressed_size_mod_9200_plus_min_byte_value_times_4200(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_compressed_size_mod_827_times_3100_plus_decompressed_size_mod_9200_plus_min_byte_value_times_4200(MINI) >= 0

    def test_text_greater_than_mini(self):
        assert (zst_compressed_size_mod_827_times_3100_plus_decompressed_size_mod_9200_plus_min_byte_value_times_4200(TEXT) >
                zst_compressed_size_mod_827_times_3100_plus_decompressed_size_mod_9200_plus_min_byte_value_times_4200(MINI))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_827_times_3100_plus_decompressed_size_mod_9200_plus_min_byte_value_times_4200(str(TEXT)) == 977990
