"""Tests for ZST product deepening sprint 153.

New functions:
  zst_byte_sum_per_frame                — decompressed byte sum / frame count
  zst_compressed_plus_decompressed_size — compressed size + decompressed size
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.zst import zst_byte_sum_per_frame, zst_compressed_plus_decompressed_size

_TEXT = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "text-compressed.zst")
_MINIMAL = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "minimal-synthetic.zst")
_RANDOM = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "random-data.zst")


class TestZstByteSumPerFrame:
    def test_return_type(self):
        assert isinstance(zst_byte_sum_per_frame(_TEXT), int)

    def test_exact_35803_for_text(self):
        # text-compressed.zst: byte_sum=35803, frames=1 → 35803
        assert zst_byte_sum_per_frame(_TEXT) == 35803

    def test_zero_for_minimal(self):
        # minimal-synthetic.zst: byte_sum=0 (single null byte) → 0
        assert zst_byte_sum_per_frame(_MINIMAL) == 0

    def test_exact_130560_for_random(self):
        # random-data.zst: byte_sum=130560, frames=1 → 130560
        assert zst_byte_sum_per_frame(_RANDOM) == 130560

    def test_nonnegative(self):
        assert zst_byte_sum_per_frame(_TEXT) >= 0

    def test_consistent(self):
        assert zst_byte_sum_per_frame(_TEXT) == zst_byte_sum_per_frame(_TEXT)


class TestZstCompressedPlusDecompressedSize:
    def test_return_type(self):
        assert isinstance(zst_compressed_plus_decompressed_size(_TEXT), int)

    def test_exact_662_for_text(self):
        # text-compressed.zst: 272 + 390 = 662
        assert zst_compressed_plus_decompressed_size(_TEXT) == 662

    def test_exact_11_for_minimal(self):
        # minimal-synthetic.zst: 10 + 1 = 11
        assert zst_compressed_plus_decompressed_size(_MINIMAL) == 11

    def test_exact_1300_for_random(self):
        # random-data.zst: 276 + 1024 = 1300
        assert zst_compressed_plus_decompressed_size(_RANDOM) == 1300

    def test_positive(self):
        assert zst_compressed_plus_decompressed_size(_TEXT) > 0

    def test_consistent(self):
        assert zst_compressed_plus_decompressed_size(_TEXT) == zst_compressed_plus_decompressed_size(_TEXT)
