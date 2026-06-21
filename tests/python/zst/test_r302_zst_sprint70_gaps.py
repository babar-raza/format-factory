"""Tests for ZST Sprint 70 gap closure.

Closes:
  GAP-ZST-FOSS-ZST_AVG_BYTE-001   (Zst Avg Byte Value)
  GAP-ZST-FOSS-ZST_SIZE_PER-001   (Zst Size Per Frame)
  GAP-ZST-FOSS-ZST_BYTE_RAT-001   (Zst Byte Ratio)
"""
import pytest
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.zst import zst_avg_byte_value, zst_size_per_frame, zst_byte_ratio

_DIR = _REPO / "samples" / "by-format" / "zst" / "valid"
_BLOCK = str(_DIR / "block-128k.zst")
_DICT = str(_DIR / "dict-compressed.zst")
_EMPTY = str(_DIR / "empty-block.zst")
_MINIMAL = str(_DIR / "minimal-synthetic.zst")


class TestZstAvgByteValue:
    def test_return_type(self):
        assert isinstance(zst_avg_byte_value(_BLOCK), (int, float))

    def test_zero_for_block128k(self):
        assert zst_avg_byte_value(_BLOCK) == 0.0

    def test_approx_94_86_for_dict(self):
        assert zst_avg_byte_value(_DICT) == pytest.approx(94.862, rel=1e-2)

    def test_zero_for_empty(self):
        assert zst_avg_byte_value(_EMPTY) == 0.0

    def test_zero_for_minimal(self):
        assert zst_avg_byte_value(_MINIMAL) == 0.0

    def test_consistent_across_calls(self):
        assert zst_avg_byte_value(_BLOCK) == zst_avg_byte_value(_BLOCK)


class TestZstSizePerFrame:
    def test_return_type(self):
        assert isinstance(zst_size_per_frame(_BLOCK), (int, float))

    def test_exact_131081_for_block128k(self):
        assert zst_size_per_frame(_BLOCK) == 131081.0

    def test_exact_74_for_dict(self):
        assert zst_size_per_frame(_DICT) == 74.0

    def test_exact_11_for_empty(self):
        assert zst_size_per_frame(_EMPTY) == 11.0

    def test_exact_10_for_minimal(self):
        assert zst_size_per_frame(_MINIMAL) == 10.0

    def test_positive(self):
        assert zst_size_per_frame(_BLOCK) > 0

    def test_consistent_across_calls(self):
        assert zst_size_per_frame(_BLOCK) == zst_size_per_frame(_BLOCK)


class TestZstByteRatio:
    def test_return_type(self):
        assert isinstance(zst_byte_ratio(_BLOCK), (int, float))

    def test_approx_1_0_for_block128k(self):
        assert zst_byte_ratio(_BLOCK) == pytest.approx(1.0, rel=1e-3)

    def test_approx_56_22_for_dict(self):
        assert zst_byte_ratio(_DICT) == pytest.approx(56.216, rel=1e-2)

    def test_zero_for_empty(self):
        assert zst_byte_ratio(_EMPTY) == 0.0

    def test_exact_0_1_for_minimal(self):
        assert zst_byte_ratio(_MINIMAL) == pytest.approx(0.1)

    def test_nonnegative(self):
        assert zst_byte_ratio(_BLOCK) >= 0.0

    def test_consistent_across_calls(self):
        assert zst_byte_ratio(_BLOCK) == zst_byte_ratio(_BLOCK)
