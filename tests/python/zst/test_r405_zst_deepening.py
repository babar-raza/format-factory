"""Tests for ZST product deepening sprint 176.

New functions:
  zst_compressed_plus_decompressed_size_div_2  — (cs + ds) // 2
  zst_byte_sum_minus_compressed_size  — byte_sum - cs, min 0
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.zst import (
    zst_compressed_plus_decompressed_size_div_2,
    zst_byte_sum_minus_compressed_size,
)

_TEXT = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "text-compressed.zst")
_MINI = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "minimal-synthetic.zst")
_RAND = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "random-data.zst")


class TestZstCompressedPlusDecompressedSizeDiv2:
    def test_return_type(self):
        assert isinstance(zst_compressed_plus_decompressed_size_div_2(_TEXT), int)

    def test_exact_331_for_text(self):
        # text-compressed: cs=272, ds=390 → (272+390)//2 = 331
        assert zst_compressed_plus_decompressed_size_div_2(_TEXT) == 331

    def test_exact_5_for_minimal(self):
        # minimal-synthetic: cs=10, ds=1 → (10+1)//2 = 5
        assert zst_compressed_plus_decompressed_size_div_2(_MINI) == 5

    def test_exact_650_for_random(self):
        # random-data: cs=276, ds=1024 → (276+1024)//2 = 650
        assert zst_compressed_plus_decompressed_size_div_2(_RAND) == 650

    def test_nonnegative(self):
        assert zst_compressed_plus_decompressed_size_div_2(_TEXT) >= 0

    def test_consistent(self):
        assert zst_compressed_plus_decompressed_size_div_2(_RAND) == zst_compressed_plus_decompressed_size_div_2(_RAND)


class TestZstByteSumMinusCompressedSize:
    def test_return_type(self):
        assert isinstance(zst_byte_sum_minus_compressed_size(_TEXT), int)

    def test_exact_35531_for_text(self):
        # text-compressed: bs=35803, cs=272 → 35803 - 272 = 35531
        assert zst_byte_sum_minus_compressed_size(_TEXT) == 35531

    def test_exact_0_for_minimal(self):
        # minimal-synthetic: bs=0, cs=10 → max(0, -10) = 0
        assert zst_byte_sum_minus_compressed_size(_MINI) == 0

    def test_exact_130284_for_random(self):
        # random-data: bs=130560, cs=276 → 130560 - 276 = 130284
        assert zst_byte_sum_minus_compressed_size(_RAND) == 130284

    def test_nonnegative(self):
        assert zst_byte_sum_minus_compressed_size(_TEXT) >= 0

    def test_consistent(self):
        assert zst_byte_sum_minus_compressed_size(_RAND) == zst_byte_sum_minus_compressed_size(_RAND)
