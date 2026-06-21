"""Tests for ZST product deepening sprint 167.

New functions:
  zst_byte_sum_plus_compressed_size  — decompressed byte sum + compressed size
  zst_compressed_size_times_10       — compressed size * 10
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.zst import (
    zst_byte_sum_plus_compressed_size,
    zst_compressed_size_times_10,
)

_TEXT = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "text-compressed.zst")
_MIN = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "minimal-synthetic.zst")
_RAND = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "random-data.zst")


class TestZstByteSumPlusCompressedSize:
    def test_return_type(self):
        assert isinstance(zst_byte_sum_plus_compressed_size(_TEXT), int)

    def test_exact_36075_for_text(self):
        # text-compressed: byte_sum=35803, cs=272 → 36075
        assert zst_byte_sum_plus_compressed_size(_TEXT) == 36075

    def test_exact_10_for_minimal(self):
        # minimal-synthetic: byte_sum=0, cs=10 → 10
        assert zst_byte_sum_plus_compressed_size(_MIN) == 10

    def test_exact_130836_for_random(self):
        # random-data: byte_sum=130560, cs=276 → 130836
        assert zst_byte_sum_plus_compressed_size(_RAND) == 130836

    def test_positive(self):
        assert zst_byte_sum_plus_compressed_size(_MIN) > 0

    def test_consistent(self):
        assert zst_byte_sum_plus_compressed_size(_TEXT) == zst_byte_sum_plus_compressed_size(_TEXT)


class TestZstCompressedSizeTimes10:
    def test_return_type(self):
        assert isinstance(zst_compressed_size_times_10(_TEXT), int)

    def test_exact_2720_for_text(self):
        # text-compressed: cs=272 → 2720
        assert zst_compressed_size_times_10(_TEXT) == 2720

    def test_exact_100_for_minimal(self):
        # minimal-synthetic: cs=10 → 100
        assert zst_compressed_size_times_10(_MIN) == 100

    def test_exact_2760_for_random(self):
        # random-data: cs=276 → 2760
        assert zst_compressed_size_times_10(_RAND) == 2760

    def test_positive(self):
        assert zst_compressed_size_times_10(_MIN) > 0

    def test_consistent(self):
        assert zst_compressed_size_times_10(_TEXT) == zst_compressed_size_times_10(_TEXT)
