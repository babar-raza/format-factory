"""Sprint 308 ZST product deepening — 2 new analytics functions, 20 tests.

Skill: add-python-api
Spec fact refs: FACT-ZST-EX-0001, FACT-ZST-EX-0002
"""
from __future__ import annotations

from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
_ZST_DIR = _REPO / "samples" / "by-format" / "zst" / "valid"

ZST_MINIMAL = _ZST_DIR / "minimal-synthetic.zst"
ZST_TEXT = _ZST_DIR / "text-compressed.zst"
ZST_RLE = _ZST_DIR / "rle-first-block.zst"

import sys
sys.path.insert(0, str(_REPO))

from src.python.zst import (
    zst_compressed_size_mod_29_times_400_plus_decompressed_size_times_4_plus_max_byte_value_times_60 as f1,
    zst_file_size_times_13_plus_decompressed_size_mod_300_times_8_plus_max_byte_value_times_90 as f2,
)


# ---------------------------------------------------------------------------
# zst_compressed_size_mod_29_times_400_plus_decompressed_size_times_4_plus_max_byte_value_times_60
# ---------------------------------------------------------------------------

class TestZstCompressedSizeMod29Times400PlusDecompressedSize4PlusMaxByte60:
    def test_minimal_returns_int(self):
        result = f1(ZST_MINIMAL)
        assert isinstance(result, int)

    def test_minimal_expected_value(self):
        assert f1(ZST_MINIMAL) == 4004

    def test_text_returns_int(self):
        result = f1(ZST_TEXT)
        assert isinstance(result, int)

    def test_text_expected_value(self):
        assert f1(ZST_TEXT) == 13220

    def test_rle_returns_int(self):
        result = f1(ZST_RLE)
        assert isinstance(result, int)

    def test_rle_expected_value(self):
        assert f1(ZST_RLE) == 4200704

    def test_rle_greater_than_text(self):
        assert f1(ZST_RLE) > f1(ZST_TEXT)

    def test_text_greater_than_minimal(self):
        assert f1(ZST_TEXT) > f1(ZST_MINIMAL)

    def test_path_string_accepted(self):
        result = f1(str(ZST_MINIMAL))
        assert isinstance(result, int)

    def test_invalid_path_raises(self):
        with pytest.raises(Exception):
            f1("/nonexistent/path/missing.zst")


# ---------------------------------------------------------------------------
# zst_file_size_times_13_plus_decompressed_size_mod_300_times_8_plus_max_byte_value_times_90
# ---------------------------------------------------------------------------

class TestZstFileSizeTimes13PlusDecompressedSizeMod300Times8PlusMaxByte90:
    def test_minimal_returns_int(self):
        result = f2(ZST_MINIMAL)
        assert isinstance(result, int)

    def test_minimal_expected_value(self):
        assert f2(ZST_MINIMAL) == 138

    def test_text_returns_int(self):
        result = f2(ZST_TEXT)
        assert isinstance(result, int)

    def test_text_expected_value(self):
        assert f2(ZST_TEXT) == 15146

    def test_rle_returns_int(self):
        result = f2(ZST_RLE)
        assert isinstance(result, int)

    def test_rle_expected_value(self):
        assert f2(ZST_RLE) == 1193

    def test_text_greater_than_minimal(self):
        assert f2(ZST_TEXT) > f2(ZST_MINIMAL)

    def test_text_greater_than_rle(self):
        assert f2(ZST_TEXT) > f2(ZST_RLE)

    def test_path_string_accepted(self):
        result = f2(str(ZST_TEXT))
        assert isinstance(result, int)

    def test_invalid_path_raises(self):
        with pytest.raises(Exception):
            f2("/nonexistent/path/missing.zst")
