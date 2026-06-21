"""Tests for ZST product deepening sprint 182.

New functions:
  zst_decompressed_size_minus_max_byte  — ds - max_byte, min 0
  zst_compressed_size_squared  — cs * cs
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.zst import (
    zst_decompressed_size_minus_max_byte,
    zst_compressed_size_squared,
)

_TEXT = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "text-compressed.zst")
_MINI = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "minimal-synthetic.zst")
_RAND = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "random-data.zst")


class TestZstDecompressedSizeMinusMaxByte:
    def test_return_type(self):
        assert isinstance(zst_decompressed_size_minus_max_byte(_TEXT), int)

    def test_exact_269_for_text(self):
        # text-compressed: ds=390, max=121 → 390 - 121 = 269
        assert zst_decompressed_size_minus_max_byte(_TEXT) == 269

    def test_exact_1_for_minimal(self):
        # minimal-synthetic: ds=1, max=0 → 1 - 0 = 1
        assert zst_decompressed_size_minus_max_byte(_MINI) == 1

    def test_exact_769_for_random(self):
        # random-data: ds=1024, max=255 → 1024 - 255 = 769
        assert zst_decompressed_size_minus_max_byte(_RAND) == 769

    def test_nonnegative(self):
        assert zst_decompressed_size_minus_max_byte(_TEXT) >= 0

    def test_consistent(self):
        assert zst_decompressed_size_minus_max_byte(_RAND) == zst_decompressed_size_minus_max_byte(_RAND)


class TestZstCompressedSizeSquared:
    def test_return_type(self):
        assert isinstance(zst_compressed_size_squared(_TEXT), int)

    def test_exact_73984_for_text(self):
        # text-compressed: cs=272 → 272*272 = 73984
        assert zst_compressed_size_squared(_TEXT) == 73984

    def test_exact_100_for_minimal(self):
        # minimal-synthetic: cs=10 → 10*10 = 100
        assert zst_compressed_size_squared(_MINI) == 100

    def test_exact_76176_for_random(self):
        # random-data: cs=276 → 276*276 = 76176
        assert zst_compressed_size_squared(_RAND) == 76176

    def test_nonnegative(self):
        assert zst_compressed_size_squared(_TEXT) >= 0

    def test_consistent(self):
        assert zst_compressed_size_squared(_RAND) == zst_compressed_size_squared(_RAND)
