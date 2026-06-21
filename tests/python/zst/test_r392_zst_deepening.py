"""Tests for ZST product deepening sprint 163.

New functions:
  zst_max_byte_value_minus_avg_byte_value  — max - avg byte value (int)
  zst_decompressed_size_plus_max_byte      — decompressed size + max byte value
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.zst import (
    zst_max_byte_value_minus_avg_byte_value,
    zst_decompressed_size_plus_max_byte,
)

_TEXT = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "text-compressed.zst")
_MIN = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "minimal-synthetic.zst")
_RAND = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "random-data.zst")


class TestZstMaxByteValueMinusAvgByteValue:
    def test_return_type(self):
        assert isinstance(zst_max_byte_value_minus_avg_byte_value(_TEXT), int)

    def test_exact_30_for_text(self):
        # text-compressed: max=121, avg=91 → 30
        assert zst_max_byte_value_minus_avg_byte_value(_TEXT) == 30

    def test_zero_for_minimal(self):
        # minimal-synthetic: max=0, avg=0 → 0
        assert zst_max_byte_value_minus_avg_byte_value(_MIN) == 0

    def test_exact_128_for_random(self):
        # random-data: max=255, avg=127 → 128
        assert zst_max_byte_value_minus_avg_byte_value(_RAND) == 128

    def test_nonnegative(self):
        assert zst_max_byte_value_minus_avg_byte_value(_MIN) >= 0

    def test_consistent(self):
        assert zst_max_byte_value_minus_avg_byte_value(_TEXT) == zst_max_byte_value_minus_avg_byte_value(_TEXT)


class TestZstDecompressedSizePlusMaxByte:
    def test_return_type(self):
        assert isinstance(zst_decompressed_size_plus_max_byte(_TEXT), int)

    def test_exact_511_for_text(self):
        # text-compressed: ds=390, max=121 → 511
        assert zst_decompressed_size_plus_max_byte(_TEXT) == 511

    def test_exact_1_for_minimal(self):
        # minimal-synthetic: ds=1, max=0 → 1
        assert zst_decompressed_size_plus_max_byte(_MIN) == 1

    def test_exact_1279_for_random(self):
        # random-data: ds=1024, max=255 → 1279
        assert zst_decompressed_size_plus_max_byte(_RAND) == 1279

    def test_positive(self):
        assert zst_decompressed_size_plus_max_byte(_MIN) > 0

    def test_consistent(self):
        assert zst_decompressed_size_plus_max_byte(_TEXT) == zst_decompressed_size_plus_max_byte(_TEXT)
