"""Tests for zst_is_compressible and zst_compression_saving (Sprint 63)."""
import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src" / "python"))

from zst.zst_codec import zst_is_compressible, zst_compression_saving

ZST = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "zst" / "valid"


class TestZstIsCompressible:
    def test_minimal_not_compressible(self):
        assert zst_is_compressible(ZST / "minimal-synthetic.zst") is False

    def test_text_is_compressible(self):
        assert zst_is_compressible(ZST / "text-compressed.zst") is True

    def test_random_is_compressible(self):
        assert zst_is_compressible(ZST / "random-data.zst") is True

    def test_returns_bool(self):
        assert isinstance(zst_is_compressible(ZST / "minimal-synthetic.zst"), bool)

    def test_false_when_compressed_larger(self):
        assert zst_is_compressible(ZST / "minimal-synthetic.zst") is False


class TestZstCompressionSaving:
    def test_minimal_zero_saving(self):
        assert zst_compression_saving(ZST / "minimal-synthetic.zst") == 0

    def test_text_saving(self):
        assert zst_compression_saving(ZST / "text-compressed.zst") == 118

    def test_random_saving(self):
        assert zst_compression_saving(ZST / "random-data.zst") == 748

    def test_returns_int(self):
        assert isinstance(zst_compression_saving(ZST / "minimal-synthetic.zst"), int)

    def test_nonnegative(self):
        for f in ["minimal-synthetic.zst", "text-compressed.zst", "random-data.zst"]:
            assert zst_compression_saving(ZST / f) >= 0
