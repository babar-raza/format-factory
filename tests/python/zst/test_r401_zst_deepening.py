"""Tests for ZST product deepening sprint 172.

New functions:
  zst_compressed_size_minus_frame_count_times_5  — cs - fc*5, min 0
  zst_byte_sum_div_decompressed_size  — byte_sum // ds, 0 if empty
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.zst import (
    zst_compressed_size_minus_frame_count_times_5,
    zst_byte_sum_div_decompressed_size,
)

_TEXT = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "text-compressed.zst")
_MINI = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "minimal-synthetic.zst")
_RAND = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "random-data.zst")


class TestZstCompressedSizeMinusFrameCountTimes5:
    def test_return_type(self):
        assert isinstance(zst_compressed_size_minus_frame_count_times_5(_TEXT), int)

    def test_exact_267_for_text(self):
        # text-compressed: cs=272, fc=1 → 272 - 5 = 267
        assert zst_compressed_size_minus_frame_count_times_5(_TEXT) == 267

    def test_exact_5_for_minimal(self):
        # minimal-synthetic: cs=10, fc=1 → 10 - 5 = 5
        assert zst_compressed_size_minus_frame_count_times_5(_MINI) == 5

    def test_exact_271_for_random(self):
        # random-data: cs=276, fc=1 → 276 - 5 = 271
        assert zst_compressed_size_minus_frame_count_times_5(_RAND) == 271

    def test_nonnegative(self):
        assert zst_compressed_size_minus_frame_count_times_5(_TEXT) >= 0

    def test_consistent(self):
        assert zst_compressed_size_minus_frame_count_times_5(_RAND) == zst_compressed_size_minus_frame_count_times_5(_RAND)


class TestZstByteSumDivDecompressedSize:
    def test_return_type(self):
        assert isinstance(zst_byte_sum_div_decompressed_size(_TEXT), int)

    def test_exact_91_for_text(self):
        # text-compressed: bs=35803, ds=390 → 35803 // 390 = 91
        assert zst_byte_sum_div_decompressed_size(_TEXT) == 91

    def test_exact_0_for_minimal(self):
        # minimal-synthetic: bs=0, ds=1 → 0 // 1 = 0
        assert zst_byte_sum_div_decompressed_size(_MINI) == 0

    def test_exact_127_for_random(self):
        # random-data: bs=130560, ds=1024 → 130560 // 1024 = 127
        assert zst_byte_sum_div_decompressed_size(_RAND) == 127

    def test_nonnegative(self):
        assert zst_byte_sum_div_decompressed_size(_TEXT) >= 0

    def test_consistent(self):
        assert zst_byte_sum_div_decompressed_size(_RAND) == zst_byte_sum_div_decompressed_size(_RAND)
