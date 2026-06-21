"""Sprint 251 ZST deepening — 2 new analytics functions, 12 tests."""
from pathlib import Path

import pytest

from src.python.zst.zst_codec import (
    zst_decompressed_byte_sum_mod_500_plus_compressed_size_times_3_plus_max_byte_times_100,
    zst_decompressed_size_mod_41_times_5_plus_byte_sum_mod_200_plus_compressed_size_times_7,
)

_SAMPLES = Path("samples/by-format/zst/valid")
_TEXT = _SAMPLES / "text-compressed.zst"     # cs=272, ds=390, bs=35803, mx=121, mn=32
_MINIMAL = _SAMPLES / "minimal-synthetic.zst" # cs=10, ds=1, bs=0, mx=0, mn=0
_RANDOM = _SAMPLES / "random-data.zst"        # cs=276, ds=1024, bs=130560, mx=255, mn=0

# fn1 = bs % 500 + cs * 3 + mx * 100
#   text:    35803 % 500 + 272 * 3 + 121 * 100 = 303 + 816 + 12100 = 13219
#   minimal: 0 % 500 + 10 * 3 + 0 * 100        = 0 + 30 + 0         = 30
#   random:  130560 % 500 + 276 * 3 + 255 * 100 = 60 + 828 + 25500  = 26388

# fn2 = ds % 41 * 5 + bs % 200 + cs * 7
#   text:    390 % 41 * 5 + 35803 % 200 + 272 * 7 = 105 + 3 + 1904 = 2012
#   minimal: 1 % 41 * 5 + 0 % 200 + 10 * 7        = 5 + 0 + 70     = 75
#   random:  1024 % 41 * 5 + 130560 % 200 + 276 * 7 = 200 + 160 + 1932 = 2292


class TestZstDecompressedByteSumMod500PlusCompressedSizeTimes3PlusMaxBytesTimes100:
    def test_text_returns_13219(self):
        assert zst_decompressed_byte_sum_mod_500_plus_compressed_size_times_3_plus_max_byte_times_100(_TEXT) == 13219

    def test_minimal_returns_30(self):
        assert zst_decompressed_byte_sum_mod_500_plus_compressed_size_times_3_plus_max_byte_times_100(_MINIMAL) == 30

    def test_random_returns_26388(self):
        assert zst_decompressed_byte_sum_mod_500_plus_compressed_size_times_3_plus_max_byte_times_100(_RANDOM) == 26388

    def test_minimal_is_positive(self):
        result = zst_decompressed_byte_sum_mod_500_plus_compressed_size_times_3_plus_max_byte_times_100(_MINIMAL)
        assert result > 0

    def test_random_greater_than_text(self):
        r_r = zst_decompressed_byte_sum_mod_500_plus_compressed_size_times_3_plus_max_byte_times_100(_RANDOM)
        r_t = zst_decompressed_byte_sum_mod_500_plus_compressed_size_times_3_plus_max_byte_times_100(_TEXT)
        assert r_r > r_t

    def test_returns_int(self):
        result = zst_decompressed_byte_sum_mod_500_plus_compressed_size_times_3_plus_max_byte_times_100(_TEXT)
        assert isinstance(result, int)


class TestZstDecompressedSizeMod41Times5PlusByteSumMod200PlusCompressedSizeTimes7:
    def test_text_returns_2012(self):
        assert zst_decompressed_size_mod_41_times_5_plus_byte_sum_mod_200_plus_compressed_size_times_7(_TEXT) == 2012

    def test_minimal_returns_75(self):
        assert zst_decompressed_size_mod_41_times_5_plus_byte_sum_mod_200_plus_compressed_size_times_7(_MINIMAL) == 75

    def test_random_returns_2292(self):
        assert zst_decompressed_size_mod_41_times_5_plus_byte_sum_mod_200_plus_compressed_size_times_7(_RANDOM) == 2292

    def test_minimal_is_positive(self):
        result = zst_decompressed_size_mod_41_times_5_plus_byte_sum_mod_200_plus_compressed_size_times_7(_MINIMAL)
        assert result > 0

    def test_random_greater_than_text(self):
        r_r = zst_decompressed_size_mod_41_times_5_plus_byte_sum_mod_200_plus_compressed_size_times_7(_RANDOM)
        r_t = zst_decompressed_size_mod_41_times_5_plus_byte_sum_mod_200_plus_compressed_size_times_7(_TEXT)
        assert r_r > r_t

    def test_returns_int(self):
        result = zst_decompressed_size_mod_41_times_5_plus_byte_sum_mod_200_plus_compressed_size_times_7(_TEXT)
        assert isinstance(result, int)
