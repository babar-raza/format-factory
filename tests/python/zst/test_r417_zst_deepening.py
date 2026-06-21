"""Tests for ZST product deepening sprint 188.

New functions:
  zst_decompressed_size_times_10_plus_compressed_size  — ds*10 + cs
  zst_byte_sum_div_compressed_size  — bs//cs (0 if cs==0)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.zst import (
    zst_decompressed_size_times_10_plus_compressed_size,
    zst_byte_sum_div_compressed_size,
)

_TEXT = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "text-compressed.zst")
_MINI = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "minimal-synthetic.zst")
_RAND = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "random-data.zst")


class TestZstDecompressedSizeTimes10PlusCompressedSize:
    def test_return_type(self):
        assert isinstance(zst_decompressed_size_times_10_plus_compressed_size(_TEXT), int)

    def test_exact_4172_for_text(self):
        # text-compressed: ds=390, cs=272 → 390*10 + 272 = 4172
        assert zst_decompressed_size_times_10_plus_compressed_size(_TEXT) == 4172

    def test_exact_20_for_minimal(self):
        # minimal-synthetic: ds=1, cs=10 → 1*10 + 10 = 20
        assert zst_decompressed_size_times_10_plus_compressed_size(_MINI) == 20

    def test_exact_10516_for_random(self):
        # random-data: ds=1024, cs=276 → 1024*10 + 276 = 10516
        assert zst_decompressed_size_times_10_plus_compressed_size(_RAND) == 10516

    def test_nonnegative(self):
        assert zst_decompressed_size_times_10_plus_compressed_size(_TEXT) >= 0

    def test_consistent(self):
        assert zst_decompressed_size_times_10_plus_compressed_size(_RAND) == zst_decompressed_size_times_10_plus_compressed_size(_RAND)


class TestZstByteSumDivCompressedSize:
    def test_return_type(self):
        assert isinstance(zst_byte_sum_div_compressed_size(_TEXT), int)

    def test_exact_131_for_text(self):
        # text-compressed: bs=35803, cs=272 → 35803//272 = 131
        assert zst_byte_sum_div_compressed_size(_TEXT) == 131

    def test_exact_0_for_minimal(self):
        # minimal-synthetic: bs=0, cs=10 → 0//10 = 0
        assert zst_byte_sum_div_compressed_size(_MINI) == 0

    def test_exact_473_for_random(self):
        # random-data: bs=130560, cs=276 → 130560//276 = 473
        assert zst_byte_sum_div_compressed_size(_RAND) == 473

    def test_nonnegative(self):
        assert zst_byte_sum_div_compressed_size(_TEXT) >= 0

    def test_consistent(self):
        assert zst_byte_sum_div_compressed_size(_RAND) == zst_byte_sum_div_compressed_size(_RAND)
