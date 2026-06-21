"""Sprint 311 ZST product deepening — 2 new analytics functions, 20 tests.

Skill: add-python-api
Spec fact refs: FACT-ZST-EX-0003, FACT-ZST-EX-0004
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
    zst_decompressed_size_mod_31_times_500_plus_compressed_size_times_5_plus_max_byte_value_times_70 as f1,
    zst_file_size_times_29_plus_decompressed_size_mod_400_times_9_plus_max_byte_value_times_100 as f2,
)


class TestZstDecompressedSizeMod31Times500PlusCompressedSize5PlusMaxByte70:
    def test_minimal_returns_int(self):
        assert isinstance(f1(ZST_MINIMAL), int)

    def test_minimal_expected_value(self):
        assert f1(ZST_MINIMAL) == 550

    def test_text_returns_int(self):
        assert isinstance(f1(ZST_TEXT), int)

    def test_text_expected_value(self):
        assert f1(ZST_TEXT) == 18830

    def test_rle_returns_int(self):
        assert isinstance(f1(ZST_RLE), int)

    def test_rle_expected_value(self):
        assert f1(ZST_RLE) == 725

    def test_text_greater_than_rle(self):
        assert f1(ZST_TEXT) > f1(ZST_RLE)

    def test_rle_greater_than_minimal(self):
        assert f1(ZST_RLE) > f1(ZST_MINIMAL)

    def test_path_string_accepted(self):
        assert isinstance(f1(str(ZST_MINIMAL)), int)

    def test_invalid_path_raises(self):
        with pytest.raises(Exception):
            f1("/nonexistent/path/missing.zst")


class TestZstFileSizeTimes29PlusDecompressedSizeMod400Times9PlusMaxByte100:
    def test_minimal_returns_int(self):
        assert isinstance(f2(ZST_MINIMAL), int)

    def test_minimal_expected_value(self):
        assert f2(ZST_MINIMAL) == 299

    def test_text_returns_int(self):
        assert isinstance(f2(ZST_TEXT), int)

    def test_text_expected_value(self):
        assert f2(ZST_TEXT) == 23498

    def test_rle_returns_int(self):
        assert isinstance(f2(ZST_RLE), int)

    def test_rle_expected_value(self):
        assert f2(ZST_RLE) == 2889

    def test_text_greater_than_rle(self):
        assert f2(ZST_TEXT) > f2(ZST_RLE)

    def test_rle_greater_than_minimal(self):
        assert f2(ZST_RLE) > f2(ZST_MINIMAL)

    def test_path_string_accepted(self):
        assert isinstance(f2(str(ZST_TEXT)), int)

    def test_invalid_path_raises(self):
        with pytest.raises(Exception):
            f2("/nonexistent/path/missing.zst")
