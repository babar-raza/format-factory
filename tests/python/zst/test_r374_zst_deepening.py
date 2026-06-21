"""Tests for ZST product deepening sprint 147.

New functions:
  zst_decompressed_byte_range     — max byte value minus min byte value
  zst_avg_decompressed_byte_value — mean byte value (0.0-255.0)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.zst import zst_decompressed_byte_range, zst_avg_decompressed_byte_value

_TEXT = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "text-compressed.zst")
_MINIMAL = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "minimal-synthetic.zst")
_EMPTY = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "empty-block.zst")


class TestZstDecompressedByteRange:
    def test_return_type(self):
        assert isinstance(zst_decompressed_byte_range(_TEXT), int)

    def test_exact_89_for_text(self):
        # text-compressed.zst: max=121, min=32 → range=89
        assert zst_decompressed_byte_range(_TEXT) == 89

    def test_zero_for_minimal(self):
        # minimal-synthetic.zst: single zero byte → max=0, min=0 → range=0
        assert zst_decompressed_byte_range(_MINIMAL) == 0

    def test_zero_for_empty(self):
        assert zst_decompressed_byte_range(_EMPTY) == 0

    def test_nonnegative(self):
        assert zst_decompressed_byte_range(_TEXT) >= 0

    def test_consistent(self):
        assert zst_decompressed_byte_range(_TEXT) == zst_decompressed_byte_range(_TEXT)


class TestZstAvgDecompressedByteValue:
    def test_return_type(self):
        assert isinstance(zst_avg_decompressed_byte_value(_TEXT), float)

    def test_approx_91_8_for_text(self):
        # text-compressed.zst: sum=35803, count=390 → avg≈91.8026
        result = zst_avg_decompressed_byte_value(_TEXT)
        assert abs(result - 91.8026) < 0.001

    def test_zero_for_minimal(self):
        assert zst_avg_decompressed_byte_value(_MINIMAL) == 0.0

    def test_zero_for_empty(self):
        assert zst_avg_decompressed_byte_value(_EMPTY) == 0.0

    def test_bounded(self):
        r = zst_avg_decompressed_byte_value(_TEXT)
        assert 0.0 <= r <= 255.0

    def test_consistent(self):
        assert zst_avg_decompressed_byte_value(_TEXT) == zst_avg_decompressed_byte_value(_TEXT)
