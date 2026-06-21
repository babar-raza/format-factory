"""Tests for ZST product deepening sprint 159.

New functions:
  zst_max_byte_value_plus_min_byte_value    — max + min decompressed byte value
  zst_compressed_size_minus_min_byte_value  — compressed size - min byte value
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.zst import (
    zst_max_byte_value_plus_min_byte_value,
    zst_compressed_size_minus_min_byte_value,
)

_TEXT = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "text-compressed.zst")
_MIN = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "minimal-synthetic.zst")
_RAND = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "random-data.zst")


class TestZstMaxByteValuePlusMinByteValue:
    def test_return_type(self):
        assert isinstance(zst_max_byte_value_plus_min_byte_value(_TEXT), int)

    def test_exact_153_for_text(self):
        # text-compressed: max=121, min=32 → 153
        assert zst_max_byte_value_plus_min_byte_value(_TEXT) == 153

    def test_zero_for_minimal(self):
        # minimal-synthetic: max=0, min=0 → 0
        assert zst_max_byte_value_plus_min_byte_value(_MIN) == 0

    def test_exact_255_for_random(self):
        # random-data: max=255, min=0 → 255
        assert zst_max_byte_value_plus_min_byte_value(_RAND) == 255

    def test_nonnegative(self):
        assert zst_max_byte_value_plus_min_byte_value(_MIN) >= 0

    def test_consistent(self):
        assert zst_max_byte_value_plus_min_byte_value(_TEXT) == zst_max_byte_value_plus_min_byte_value(_TEXT)


class TestZstCompressedSizeMinusMinByteValue:
    def test_return_type(self):
        assert isinstance(zst_compressed_size_minus_min_byte_value(_TEXT), int)

    def test_exact_240_for_text(self):
        # text-compressed: cs=272, min=32 → 240
        assert zst_compressed_size_minus_min_byte_value(_TEXT) == 240

    def test_exact_10_for_minimal(self):
        # minimal-synthetic: cs=10, min=0 → 10
        assert zst_compressed_size_minus_min_byte_value(_MIN) == 10

    def test_exact_276_for_random(self):
        # random-data: cs=276, min=0 → 276
        assert zst_compressed_size_minus_min_byte_value(_RAND) == 276

    def test_nonnegative(self):
        assert zst_compressed_size_minus_min_byte_value(_MIN) >= 0

    def test_consistent(self):
        assert zst_compressed_size_minus_min_byte_value(_TEXT) == zst_compressed_size_minus_min_byte_value(_TEXT)
