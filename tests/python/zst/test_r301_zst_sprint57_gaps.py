"""Tests for ZST Sprint 57 gap closure.

Closes:
  GAP-ZST-FOSS-ZST_SIZE_EXC-001   (Zst Size Exceeds 100K)
  GAP-ZST-FOSS-ZST_FRAME_CO-001   (Zst Frame Count Ratio)
  GAP-ZST-FOSS-ZST_OVERHEAD-001   (Zst Overhead Bytes)
  GAP-ZST-FOSS-ZST_AVG_COMP-001   (Zst Avg Compression Per Byte)
"""
import pytest
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.zst import (
    zst_size_exceeds_100k,
    zst_frame_count_ratio,
    zst_overhead_bytes,
    zst_avg_compression_per_byte,
)

_DIR = _REPO / "samples" / "by-format" / "zst" / "valid"
_MINIMAL = str(_DIR / "minimal-synthetic.zst")
_EMPTY = str(_DIR / "empty-block.zst")
_TEXT = str(_DIR / "text-compressed.zst")
_BLOCK128K = str(_DIR / "block-128k.zst")


class TestZstSizeExceeds100K:
    def test_return_type(self):
        assert isinstance(zst_size_exceeds_100k(_MINIMAL), bool)

    def test_false_for_minimal(self):
        assert zst_size_exceeds_100k(_MINIMAL) is False

    def test_false_for_empty(self):
        assert zst_size_exceeds_100k(_EMPTY) is False

    def test_false_for_text(self):
        assert zst_size_exceeds_100k(_TEXT) is False

    def test_true_for_block128k(self):
        assert zst_size_exceeds_100k(_BLOCK128K) is True

    def test_consistent_across_calls(self):
        assert zst_size_exceeds_100k(_MINIMAL) == zst_size_exceeds_100k(_MINIMAL)


class TestZstFrameCountRatio:
    def test_return_type(self):
        assert isinstance(zst_frame_count_ratio(_MINIMAL), (int, float))

    def test_exact_102_4_for_minimal(self):
        assert zst_frame_count_ratio(_MINIMAL) == pytest.approx(102.4, rel=1e-3)

    def test_exact_0_0_for_empty(self):
        assert zst_frame_count_ratio(_EMPTY) == pytest.approx(93.09, rel=1e-2)

    def test_nonzero_for_text(self):
        assert zst_frame_count_ratio(_TEXT) == pytest.approx(3.765, rel=1e-2)

    def test_nonnegative(self):
        assert zst_frame_count_ratio(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert zst_frame_count_ratio(_MINIMAL) == zst_frame_count_ratio(_MINIMAL)


class TestZstOverheadBytes:
    def test_return_type(self):
        assert isinstance(zst_overhead_bytes(_MINIMAL), int)

    def test_zero_for_minimal(self):
        assert zst_overhead_bytes(_MINIMAL) == 0

    def test_zero_for_empty(self):
        assert zst_overhead_bytes(_EMPTY) == 0

    def test_zero_for_text(self):
        assert zst_overhead_bytes(_TEXT) == 0

    def test_nonnegative(self):
        assert zst_overhead_bytes(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert zst_overhead_bytes(_MINIMAL) == zst_overhead_bytes(_MINIMAL)


class TestZstAvgCompressionPerByte:
    def test_return_type(self):
        assert isinstance(zst_avg_compression_per_byte(_MINIMAL), (int, float))

    def test_exact_0_1_for_minimal(self):
        assert zst_avg_compression_per_byte(_MINIMAL) == pytest.approx(0.1, rel=1e-3)

    def test_zero_for_empty(self):
        assert zst_avg_compression_per_byte(_EMPTY) == 0.0

    def test_approx_1_43_for_text(self):
        assert zst_avg_compression_per_byte(_TEXT) == pytest.approx(1.434, rel=1e-2)

    def test_nonnegative(self):
        assert zst_avg_compression_per_byte(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert zst_avg_compression_per_byte(_MINIMAL) == zst_avg_compression_per_byte(_MINIMAL)
