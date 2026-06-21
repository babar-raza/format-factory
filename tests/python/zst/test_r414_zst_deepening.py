"""Tests for ZST product deepening sprint 185.

New functions:
  zst_decompressed_size_times_100  — ds * 100
  zst_byte_sum_plus_compressed_size_times_2  — byte_sum + cs*2
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.zst import (
    zst_decompressed_size_times_100,
    zst_byte_sum_plus_compressed_size_times_2,
)

_TEXT = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "text-compressed.zst")
_MINI = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "minimal-synthetic.zst")
_RAND = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "random-data.zst")


class TestZstDecompressedSizeTimes100:
    def test_return_type(self):
        assert isinstance(zst_decompressed_size_times_100(_TEXT), int)

    def test_exact_39000_for_text(self):
        # text-compressed: ds=390 → 390*100 = 39000
        assert zst_decompressed_size_times_100(_TEXT) == 39000

    def test_exact_100_for_minimal(self):
        # minimal-synthetic: ds=1 → 1*100 = 100
        assert zst_decompressed_size_times_100(_MINI) == 100

    def test_exact_102400_for_random(self):
        # random-data: ds=1024 → 1024*100 = 102400
        assert zst_decompressed_size_times_100(_RAND) == 102400

    def test_nonnegative(self):
        assert zst_decompressed_size_times_100(_TEXT) >= 0

    def test_consistent(self):
        assert zst_decompressed_size_times_100(_RAND) == zst_decompressed_size_times_100(_RAND)


class TestZstByteSumPlusCompressedSizeTimes2:
    def test_return_type(self):
        assert isinstance(zst_byte_sum_plus_compressed_size_times_2(_TEXT), int)

    def test_exact_36347_for_text(self):
        # text-compressed: byte_sum=35803, cs=272 → 35803 + 272*2 = 35803 + 544 = 36347
        assert zst_byte_sum_plus_compressed_size_times_2(_TEXT) == 36347

    def test_exact_20_for_minimal(self):
        # minimal-synthetic: byte_sum=0, cs=10 → 0 + 10*2 = 20
        assert zst_byte_sum_plus_compressed_size_times_2(_MINI) == 20

    def test_exact_131112_for_random(self):
        # random-data: byte_sum=130560, cs=276 → 130560 + 276*2 = 130560 + 552 = 131112
        assert zst_byte_sum_plus_compressed_size_times_2(_RAND) == 131112

    def test_nonnegative(self):
        assert zst_byte_sum_plus_compressed_size_times_2(_TEXT) >= 0

    def test_consistent(self):
        assert zst_byte_sum_plus_compressed_size_times_2(_RAND) == zst_byte_sum_plus_compressed_size_times_2(_RAND)
