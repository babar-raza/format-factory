"""Tests for ZST product deepening sprint 191.

New functions:
  zst_max_byte_times_compressed_size_div_100  — mx*cs//100
  zst_decompressed_plus_compressed_size_times_2  — (ds+cs)*2
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.zst import (
    zst_max_byte_times_compressed_size_div_100,
    zst_decompressed_plus_compressed_size_times_2,
)

_TEXT = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "text-compressed.zst")
_MINI = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "minimal-synthetic.zst")
_RAND = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "random-data.zst")


class TestZstMaxByteTimesCompressedSizeDiv100:
    def test_return_type(self):
        assert isinstance(zst_max_byte_times_compressed_size_div_100(_TEXT), int)

    def test_exact_329_for_text(self):
        # text-compressed: mx=121, cs=272 → 121*272//100 = 329
        assert zst_max_byte_times_compressed_size_div_100(_TEXT) == 329

    def test_exact_0_for_minimal(self):
        # minimal-synthetic: mx=0, cs=10 → 0*10//100 = 0
        assert zst_max_byte_times_compressed_size_div_100(_MINI) == 0

    def test_exact_703_for_random(self):
        # random-data: mx=255, cs=276 → 255*276//100 = 703
        assert zst_max_byte_times_compressed_size_div_100(_RAND) == 703

    def test_nonnegative(self):
        assert zst_max_byte_times_compressed_size_div_100(_TEXT) >= 0

    def test_consistent(self):
        assert zst_max_byte_times_compressed_size_div_100(_RAND) == zst_max_byte_times_compressed_size_div_100(_RAND)


class TestZstDecompressedPlusCompressedSizeTimes2:
    def test_return_type(self):
        assert isinstance(zst_decompressed_plus_compressed_size_times_2(_TEXT), int)

    def test_exact_1324_for_text(self):
        # text-compressed: ds=390, cs=272 → (390+272)*2 = 1324
        assert zst_decompressed_plus_compressed_size_times_2(_TEXT) == 1324

    def test_exact_22_for_minimal(self):
        # minimal-synthetic: ds=1, cs=10 → (1+10)*2 = 22
        assert zst_decompressed_plus_compressed_size_times_2(_MINI) == 22

    def test_exact_2600_for_random(self):
        # random-data: ds=1024, cs=276 → (1024+276)*2 = 2600
        assert zst_decompressed_plus_compressed_size_times_2(_RAND) == 2600

    def test_nonnegative(self):
        assert zst_decompressed_plus_compressed_size_times_2(_TEXT) >= 0

    def test_consistent(self):
        assert zst_decompressed_plus_compressed_size_times_2(_RAND) == zst_decompressed_plus_compressed_size_times_2(_RAND)
