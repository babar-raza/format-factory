"""Tests for ZST product deepening sprint 179.

New functions:
  zst_max_byte_value_times_decompressed_size  — max_byte * ds
  zst_byte_sum_div_1000  — byte_sum // 1000
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.zst import (
    zst_max_byte_value_times_decompressed_size,
    zst_byte_sum_div_1000,
)

_TEXT = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "text-compressed.zst")
_MINI = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "minimal-synthetic.zst")
_RAND = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "random-data.zst")


class TestZstMaxByteValueTimesDecompressedSize:
    def test_return_type(self):
        assert isinstance(zst_max_byte_value_times_decompressed_size(_TEXT), int)

    def test_exact_47190_for_text(self):
        # text-compressed: max=121, ds=390 → 121*390 = 47190
        assert zst_max_byte_value_times_decompressed_size(_TEXT) == 47190

    def test_exact_0_for_minimal(self):
        # minimal-synthetic: max=0, ds=1 → 0*1 = 0
        assert zst_max_byte_value_times_decompressed_size(_MINI) == 0

    def test_exact_261120_for_random(self):
        # random-data: max=255, ds=1024 → 255*1024 = 261120
        assert zst_max_byte_value_times_decompressed_size(_RAND) == 261120

    def test_nonnegative(self):
        assert zst_max_byte_value_times_decompressed_size(_TEXT) >= 0

    def test_consistent(self):
        assert zst_max_byte_value_times_decompressed_size(_RAND) == zst_max_byte_value_times_decompressed_size(_RAND)


class TestZstByteSumDiv1000:
    def test_return_type(self):
        assert isinstance(zst_byte_sum_div_1000(_TEXT), int)

    def test_exact_35_for_text(self):
        # text-compressed: bs=35803 → 35803//1000 = 35
        assert zst_byte_sum_div_1000(_TEXT) == 35

    def test_exact_0_for_minimal(self):
        # minimal-synthetic: bs=0 → 0//1000 = 0
        assert zst_byte_sum_div_1000(_MINI) == 0

    def test_exact_130_for_random(self):
        # random-data: bs=130560 → 130560//1000 = 130
        assert zst_byte_sum_div_1000(_RAND) == 130

    def test_nonnegative(self):
        assert zst_byte_sum_div_1000(_TEXT) >= 0

    def test_consistent(self):
        assert zst_byte_sum_div_1000(_RAND) == zst_byte_sum_div_1000(_RAND)
