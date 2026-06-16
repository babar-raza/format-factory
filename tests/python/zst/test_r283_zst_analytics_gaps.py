"""
Tests for ZST analytics gap closure (1 FOSS gap).
Closes: GAP-ZST-FOSS-ZST_COMPRES-001
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from zst.zst_codec import zst_compression_saving

_ZST_TEXT = _REPO / "samples/by-format/zst/valid/text-compressed.zst"
_ZST_BLOCK = _REPO / "samples/by-format/zst/valid/block-128k.zst"
_ZST_MINIMAL = _REPO / "samples/by-format/zst/valid/minimal-synthetic.zst"


class TestZstCompressionSaving:
    def test_returns_int(self):
        assert isinstance(zst_compression_saving(_ZST_TEXT), int)

    def test_nonnegative(self):
        # saving is max(0, decompressed - compressed) so always >= 0
        assert zst_compression_saving(_ZST_TEXT) >= 0

    def test_block_nonnegative(self):
        assert zst_compression_saving(_ZST_BLOCK) >= 0

    def test_minimal_nonnegative(self):
        assert zst_compression_saving(_ZST_MINIMAL) >= 0
