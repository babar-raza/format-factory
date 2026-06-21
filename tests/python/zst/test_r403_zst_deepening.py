"""Tests for ZST product deepening sprint 174.

New functions:
  zst_max_byte_value_plus_compressed_size  — max_byte + cs
  zst_decompressed_size_times_frame_count  — ds * frame_count
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.zst import (
    zst_max_byte_value_plus_compressed_size,
    zst_decompressed_size_times_frame_count,
)

_TEXT = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "text-compressed.zst")
_MINI = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "minimal-synthetic.zst")
_RAND = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "random-data.zst")


class TestZstMaxByteValuePlusCompressedSize:
    def test_return_type(self):
        assert isinstance(zst_max_byte_value_plus_compressed_size(_TEXT), int)

    def test_exact_393_for_text(self):
        # text-compressed: max=121, cs=272 → 393
        assert zst_max_byte_value_plus_compressed_size(_TEXT) == 393

    def test_exact_10_for_minimal(self):
        # minimal-synthetic: max=0, cs=10 → 10
        assert zst_max_byte_value_plus_compressed_size(_MINI) == 10

    def test_exact_531_for_random(self):
        # random-data: max=255, cs=276 → 531
        assert zst_max_byte_value_plus_compressed_size(_RAND) == 531

    def test_nonnegative(self):
        assert zst_max_byte_value_plus_compressed_size(_TEXT) >= 0

    def test_consistent(self):
        assert zst_max_byte_value_plus_compressed_size(_RAND) == zst_max_byte_value_plus_compressed_size(_RAND)


class TestZstDecompressedSizeTimesFrameCount:
    def test_return_type(self):
        assert isinstance(zst_decompressed_size_times_frame_count(_TEXT), int)

    def test_exact_390_for_text(self):
        # text-compressed: ds=390, fc=1 → 390
        assert zst_decompressed_size_times_frame_count(_TEXT) == 390

    def test_exact_1_for_minimal(self):
        # minimal-synthetic: ds=1, fc=1 → 1
        assert zst_decompressed_size_times_frame_count(_MINI) == 1

    def test_exact_1024_for_random(self):
        # random-data: ds=1024, fc=1 → 1024
        assert zst_decompressed_size_times_frame_count(_RAND) == 1024

    def test_nonnegative(self):
        assert zst_decompressed_size_times_frame_count(_TEXT) >= 0

    def test_consistent(self):
        assert zst_decompressed_size_times_frame_count(_RAND) == zst_decompressed_size_times_frame_count(_RAND)
