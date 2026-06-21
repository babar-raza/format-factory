"""Tests for ZST product deepening sprint 169.

New functions:
  zst_byte_sum_div_100                             — decompressed byte sum // 100
  zst_decompressed_size_plus_compressed_size_times_2 — ds + cs*2
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.zst import (
    zst_byte_sum_div_100,
    zst_decompressed_size_plus_compressed_size_times_2,
)

_TEXT = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "text-compressed.zst")
_MIN = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "minimal-synthetic.zst")
_RAND = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "random-data.zst")


class TestZstByteSumDiv100:
    def test_return_type(self):
        assert isinstance(zst_byte_sum_div_100(_TEXT), int)

    def test_exact_358_for_text(self):
        # text-compressed: byte_sum=35803 → 35803//100 = 358
        assert zst_byte_sum_div_100(_TEXT) == 358

    def test_zero_for_minimal(self):
        # minimal-synthetic: byte_sum=0 → 0
        assert zst_byte_sum_div_100(_MIN) == 0

    def test_exact_1305_for_random(self):
        # random-data: byte_sum=130560 → 130560//100 = 1305
        assert zst_byte_sum_div_100(_RAND) == 1305

    def test_nonnegative(self):
        assert zst_byte_sum_div_100(_MIN) >= 0

    def test_consistent(self):
        assert zst_byte_sum_div_100(_TEXT) == zst_byte_sum_div_100(_TEXT)


class TestZstDecompressedSizePlusCompressedSizeTimes2:
    def test_return_type(self):
        assert isinstance(zst_decompressed_size_plus_compressed_size_times_2(_TEXT), int)

    def test_exact_934_for_text(self):
        # text-compressed: 390 + 272*2 = 934
        assert zst_decompressed_size_plus_compressed_size_times_2(_TEXT) == 934

    def test_exact_21_for_minimal(self):
        # minimal-synthetic: 1 + 10*2 = 21
        assert zst_decompressed_size_plus_compressed_size_times_2(_MIN) == 21

    def test_exact_1576_for_random(self):
        # random-data: 1024 + 276*2 = 1576
        assert zst_decompressed_size_plus_compressed_size_times_2(_RAND) == 1576

    def test_positive(self):
        assert zst_decompressed_size_plus_compressed_size_times_2(_MIN) > 0

    def test_consistent(self):
        assert zst_decompressed_size_plus_compressed_size_times_2(_TEXT) == zst_decompressed_size_plus_compressed_size_times_2(_TEXT)
