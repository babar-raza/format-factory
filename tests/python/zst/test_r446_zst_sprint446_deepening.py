"""Sprint 446 ZST analytics deepening tests."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINI = _ZST / "minimal-synthetic.zst"
RAND = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_811_times_2950_plus_decompressed_size_mod_8900_plus_max_byte_value_times_750,
    zst_compressed_size_mod_821_times_3000_plus_decompressed_size_mod_9000_plus_min_byte_value_times_4100,
)


class TestZstFileSizeMod811Times2950PlusDecompressedMod8900PlusMaxByte750:
    def test_text_returns_893540(self):
        assert zst_file_size_mod_811_times_2950_plus_decompressed_size_mod_8900_plus_max_byte_value_times_750(TEXT) == 893540

    def test_mini_returns_29501(self):
        assert zst_file_size_mod_811_times_2950_plus_decompressed_size_mod_8900_plus_max_byte_value_times_750(MINI) == 29501

    def test_rand_returns_1006474(self):
        assert zst_file_size_mod_811_times_2950_plus_decompressed_size_mod_8900_plus_max_byte_value_times_750(RAND) == 1006474

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_811_times_2950_plus_decompressed_size_mod_8900_plus_max_byte_value_times_750(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_file_size_mod_811_times_2950_plus_decompressed_size_mod_8900_plus_max_byte_value_times_750(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_file_size_mod_811_times_2950_plus_decompressed_size_mod_8900_plus_max_byte_value_times_750(RAND), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_811_times_2950_plus_decompressed_size_mod_8900_plus_max_byte_value_times_750(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_file_size_mod_811_times_2950_plus_decompressed_size_mod_8900_plus_max_byte_value_times_750(MINI) >= 0

    def test_rand_greater_than_mini(self):
        assert (zst_file_size_mod_811_times_2950_plus_decompressed_size_mod_8900_plus_max_byte_value_times_750(RAND) >
                zst_file_size_mod_811_times_2950_plus_decompressed_size_mod_8900_plus_max_byte_value_times_750(MINI))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_811_times_2950_plus_decompressed_size_mod_8900_plus_max_byte_value_times_750(str(TEXT)) == 893540


class TestZstCompressedSizeMod821Times3000PlusDecompressedMod9000PlusMinByte4100:
    def test_text_returns_947590(self):
        assert zst_compressed_size_mod_821_times_3000_plus_decompressed_size_mod_9000_plus_min_byte_value_times_4100(TEXT) == 947590

    def test_mini_returns_30001(self):
        assert zst_compressed_size_mod_821_times_3000_plus_decompressed_size_mod_9000_plus_min_byte_value_times_4100(MINI) == 30001

    def test_rand_returns_829024(self):
        assert zst_compressed_size_mod_821_times_3000_plus_decompressed_size_mod_9000_plus_min_byte_value_times_4100(RAND) == 829024

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_821_times_3000_plus_decompressed_size_mod_9000_plus_min_byte_value_times_4100(TEXT), int)

    def test_mini_returns_int(self):
        assert isinstance(zst_compressed_size_mod_821_times_3000_plus_decompressed_size_mod_9000_plus_min_byte_value_times_4100(MINI), int)

    def test_rand_returns_int(self):
        assert isinstance(zst_compressed_size_mod_821_times_3000_plus_decompressed_size_mod_9000_plus_min_byte_value_times_4100(RAND), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_821_times_3000_plus_decompressed_size_mod_9000_plus_min_byte_value_times_4100(TEXT) >= 0

    def test_mini_nonnegative(self):
        assert zst_compressed_size_mod_821_times_3000_plus_decompressed_size_mod_9000_plus_min_byte_value_times_4100(MINI) >= 0

    def test_text_greater_than_mini(self):
        assert (zst_compressed_size_mod_821_times_3000_plus_decompressed_size_mod_9000_plus_min_byte_value_times_4100(TEXT) >
                zst_compressed_size_mod_821_times_3000_plus_decompressed_size_mod_9000_plus_min_byte_value_times_4100(MINI))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_821_times_3000_plus_decompressed_size_mod_9000_plus_min_byte_value_times_4100(str(TEXT)) == 947590
