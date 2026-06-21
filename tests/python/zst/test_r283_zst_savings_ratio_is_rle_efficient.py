"""Tests for zst_savings_ratio and zst_is_rle_efficient (Sprint 73)."""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src" / "python"))

from zst.zst_codec import zst_savings_ratio, zst_is_rle_efficient

ZST = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "zst" / "valid"


class TestZstSavingsRatio:
    def test_minimal_negative(self):
        assert abs(zst_savings_ratio(ZST / "minimal-synthetic.zst") - (-0.9)) < 0.01

    def test_text_positive(self):
        assert abs(zst_savings_ratio(ZST / "text-compressed.zst") - 0.434) < 0.01

    def test_rle_large(self):
        assert zst_savings_ratio(ZST / "rle-first-block.zst") > 1000

    def test_returns_float(self):
        assert isinstance(zst_savings_ratio(ZST / "minimal-synthetic.zst"), float)

    def test_text_greater_than_minimal(self):
        assert zst_savings_ratio(ZST / "text-compressed.zst") > zst_savings_ratio(ZST / "minimal-synthetic.zst")


class TestZstIsRleEfficient:
    def test_minimal_false(self):
        assert zst_is_rle_efficient(ZST / "minimal-synthetic.zst") is False

    def test_text_false(self):
        assert zst_is_rle_efficient(ZST / "text-compressed.zst") is False

    def test_rle_true(self):
        assert zst_is_rle_efficient(ZST / "rle-first-block.zst") is True

    def test_returns_bool(self):
        assert isinstance(zst_is_rle_efficient(ZST / "minimal-synthetic.zst"), bool)

    def test_all_files_return_bool(self):
        for f in ["minimal-synthetic.zst", "text-compressed.zst", "rle-first-block.zst"]:
            assert isinstance(zst_is_rle_efficient(ZST / f), bool)
