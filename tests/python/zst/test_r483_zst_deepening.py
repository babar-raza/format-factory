"""Sprint 254 ZST deepening — 2 new analytics functions, 12 tests."""
from pathlib import Path

import pytest

from src.python.zst.zst_codec import (
    zst_max_byte_times_decompressed_size_mod_300_plus_compressed_size_times_5_plus_byte_sum_mod_700,
    zst_compressed_size_mod_53_times_4_plus_max_byte_times_10_plus_decompressed_size_mod_100,
)

_SAMPLES = Path("samples/by-format/zst/valid")
_TEXT = _SAMPLES / "text-compressed.zst"     # cs=272, ds=390, bs=35803, mx=121, mn=32
_MINIMAL = _SAMPLES / "minimal-synthetic.zst" # cs=10, ds=1, bs=0, mx=0, mn=0
_RANDOM = _SAMPLES / "random-data.zst"        # cs=276, ds=1024, bs=130560, mx=255, mn=0

# fn1 = mx * ds % 300 + cs * 5 + bs % 700
#   text:    121 * 390 % 300 + 272 * 5 + 35803 % 700 = 90 + 1360 + 103 = 1553
#   minimal: 0 * 1 % 300 + 10 * 5 + 0 % 700          = 0 + 50 + 0     = 50
#   random:  255 * 1024 % 300 + 276 * 5 + 130560 % 700 = 120 + 1380 + 360 = 1860

# fn2 = cs % 53 * 4 + mx * 10 + ds % 100
#   text:    272 % 53 * 4 + 121 * 10 + 390 % 100 = 28 + 1210 + 90 = 1328
#   minimal: 10 % 53 * 4 + 0 * 10 + 1 % 100      = 40 + 0 + 1    = 41
#   random:  276 % 53 * 4 + 255 * 10 + 1024 % 100 = 44 + 2550 + 24 = 2618


class TestZstMaxByteTimesDecompressedSizeMod300PlusCompressedSizeTimes5PlusByteSumMod700:
    def test_text_returns_1553(self):
        assert zst_max_byte_times_decompressed_size_mod_300_plus_compressed_size_times_5_plus_byte_sum_mod_700(_TEXT) == 1553

    def test_minimal_returns_50(self):
        assert zst_max_byte_times_decompressed_size_mod_300_plus_compressed_size_times_5_plus_byte_sum_mod_700(_MINIMAL) == 50

    def test_random_returns_1860(self):
        assert zst_max_byte_times_decompressed_size_mod_300_plus_compressed_size_times_5_plus_byte_sum_mod_700(_RANDOM) == 1860

    def test_minimal_is_positive(self):
        result = zst_max_byte_times_decompressed_size_mod_300_plus_compressed_size_times_5_plus_byte_sum_mod_700(_MINIMAL)
        assert result > 0

    def test_random_greater_than_minimal(self):
        r_r = zst_max_byte_times_decompressed_size_mod_300_plus_compressed_size_times_5_plus_byte_sum_mod_700(_RANDOM)
        r_m = zst_max_byte_times_decompressed_size_mod_300_plus_compressed_size_times_5_plus_byte_sum_mod_700(_MINIMAL)
        assert r_r > r_m

    def test_returns_int(self):
        result = zst_max_byte_times_decompressed_size_mod_300_plus_compressed_size_times_5_plus_byte_sum_mod_700(_TEXT)
        assert isinstance(result, int)


class TestZstCompressedSizeMod53Times4PlusMaxByteTimes10PlusDecompressedSizeMod100:
    def test_text_returns_1328(self):
        assert zst_compressed_size_mod_53_times_4_plus_max_byte_times_10_plus_decompressed_size_mod_100(_TEXT) == 1328

    def test_minimal_returns_41(self):
        assert zst_compressed_size_mod_53_times_4_plus_max_byte_times_10_plus_decompressed_size_mod_100(_MINIMAL) == 41

    def test_random_returns_2618(self):
        assert zst_compressed_size_mod_53_times_4_plus_max_byte_times_10_plus_decompressed_size_mod_100(_RANDOM) == 2618

    def test_minimal_is_positive(self):
        result = zst_compressed_size_mod_53_times_4_plus_max_byte_times_10_plus_decompressed_size_mod_100(_MINIMAL)
        assert result > 0

    def test_random_greater_than_text(self):
        r_r = zst_compressed_size_mod_53_times_4_plus_max_byte_times_10_plus_decompressed_size_mod_100(_RANDOM)
        r_t = zst_compressed_size_mod_53_times_4_plus_max_byte_times_10_plus_decompressed_size_mod_100(_TEXT)
        assert r_r > r_t

    def test_returns_int(self):
        result = zst_compressed_size_mod_53_times_4_plus_max_byte_times_10_plus_decompressed_size_mod_100(_TEXT)
        assert isinstance(result, int)
