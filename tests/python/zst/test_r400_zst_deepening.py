"""Tests for ZST product deepening sprint 171.

New functions:
  zst_max_byte_value_times_frame_count  — max_byte * frame_count
  zst_decompressed_size_minus_byte_sum_div_10  — ds - (byte_sum // 10), min 0
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.zst import (
    zst_max_byte_value_times_frame_count,
    zst_decompressed_size_minus_byte_sum_div_10,
)

_TEXT = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "text-compressed.zst")
_MINI = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "minimal-synthetic.zst")
_RAND = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "random-data.zst")


class TestZstMaxByteValueTimesFrameCount:
    def test_return_type(self):
        assert isinstance(zst_max_byte_value_times_frame_count(_TEXT), int)

    def test_exact_121_for_text(self):
        # text-compressed: max_byte=121, frame_count=1 → 121
        assert zst_max_byte_value_times_frame_count(_TEXT) == 121

    def test_exact_0_for_minimal(self):
        # minimal-synthetic: max_byte=0, frame_count=1 → 0
        assert zst_max_byte_value_times_frame_count(_MINI) == 0

    def test_exact_255_for_random(self):
        # random-data: max_byte=255, frame_count=1 → 255
        assert zst_max_byte_value_times_frame_count(_RAND) == 255

    def test_nonnegative(self):
        assert zst_max_byte_value_times_frame_count(_TEXT) >= 0

    def test_consistent(self):
        assert zst_max_byte_value_times_frame_count(_RAND) == zst_max_byte_value_times_frame_count(_RAND)


class TestZstDecompressedSizeMinusByteSumDiv10:
    def test_return_type(self):
        assert isinstance(zst_decompressed_size_minus_byte_sum_div_10(_TEXT), int)

    def test_exact_0_for_text(self):
        # text-compressed: ds=390, byte_sum=35803 → 390 - 3580 = -3190 → max(0, ...) = 0
        assert zst_decompressed_size_minus_byte_sum_div_10(_TEXT) == 0

    def test_exact_1_for_minimal(self):
        # minimal-synthetic: ds=1, byte_sum=0 → 1 - 0 = 1
        assert zst_decompressed_size_minus_byte_sum_div_10(_MINI) == 1

    def test_exact_0_for_random(self):
        # random-data: ds=1024, byte_sum=130560 → 1024 - 13056 = -12032 → 0
        assert zst_decompressed_size_minus_byte_sum_div_10(_RAND) == 0

    def test_nonnegative(self):
        assert zst_decompressed_size_minus_byte_sum_div_10(_TEXT) >= 0

    def test_consistent(self):
        assert zst_decompressed_size_minus_byte_sum_div_10(_MINI) == zst_decompressed_size_minus_byte_sum_div_10(_MINI)
