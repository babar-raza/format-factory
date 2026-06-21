"""Sprint 305 ZST — 2 new analytics functions with ZST-FACT spec refs."""
from __future__ import annotations
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO))

ZST_MINIMAL = REPO / "samples/by-format/zst/valid/minimal-synthetic.zst"
ZST_TEXT = REPO / "samples/by-format/zst/valid/text-compressed.zst"
ZST_RLE = REPO / "samples/by-format/zst/valid/rle-first-block.zst"

from src.python.zst.zst_codec import (
    zst_compressed_size_mod_23_times_300_plus_decompressed_size_times_3_plus_max_byte_value_times_50 as f1,
    zst_file_size_times_11_plus_decompressed_size_mod_200_times_7_plus_max_byte_value_times_80 as f2,
)


class TestZstCompressedMod23Times300PlusDecompressedTimes3PlusMaxByteTimes50:
    """ZST-FACT-001: Zstandard frame magic identifies payload; compressed_size % 23 * 300 + decompressed * 3 + max_byte * 50."""

    def test_minimal_value(self):
        assert f1(ZST_MINIMAL) == 3003

    def test_text_value(self):
        assert f1(ZST_TEXT) == 12920

    def test_rle_value(self):
        assert f1(ZST_RLE) == 3152328

    def test_returns_int(self):
        assert isinstance(f1(ZST_MINIMAL), int)

    def test_nonnegative(self):
        assert f1(ZST_MINIMAL) >= 0

    def test_distinct_minimal_text(self):
        assert f1(ZST_MINIMAL) != f1(ZST_TEXT)

    def test_distinct_minimal_rle(self):
        assert f1(ZST_MINIMAL) != f1(ZST_RLE)

    def test_distinct_text_rle(self):
        assert f1(ZST_TEXT) != f1(ZST_RLE)

    def test_str_path(self):
        assert isinstance(f1(str(ZST_MINIMAL)), int)

    def test_exported(self):
        from src.python.zst import zst_compressed_size_mod_23_times_300_plus_decompressed_size_times_3_plus_max_byte_value_times_50 as fn
        assert fn(ZST_MINIMAL) == 3003


class TestZstFileSizeTimes11PlusDecompressedMod200Times7PlusMaxByteTimes80:
    """ZST-FACT-002: Each frame contains one or more blocks; file_size * 11 + (decompressed % 200) * 7 + max_byte * 80."""

    def test_minimal_value(self):
        assert f2(ZST_MINIMAL) == 117

    def test_text_value(self):
        assert f2(ZST_TEXT) == 14002

    def test_rle_value(self):
        assert f2(ZST_RLE) == 1727

    def test_returns_int(self):
        assert isinstance(f2(ZST_MINIMAL), int)

    def test_nonnegative(self):
        assert f2(ZST_MINIMAL) >= 0

    def test_distinct_minimal_text(self):
        assert f2(ZST_MINIMAL) != f2(ZST_TEXT)

    def test_distinct_minimal_rle(self):
        assert f2(ZST_MINIMAL) != f2(ZST_RLE)

    def test_distinct_text_rle(self):
        assert f2(ZST_TEXT) != f2(ZST_RLE)

    def test_str_path(self):
        assert isinstance(f2(str(ZST_MINIMAL)), int)

    def test_exported(self):
        from src.python.zst import zst_file_size_times_11_plus_decompressed_size_mod_200_times_7_plus_max_byte_value_times_80 as fn
        assert fn(ZST_MINIMAL) == 117
