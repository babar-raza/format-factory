"""Tests for zst_is_smaller_than_1kb and zst_size_exceeds_100k (Sprint r305)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.zst.zst_codec import zst_is_smaller_than_1kb, zst_size_exceeds_100k

_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"


class TestZstIsSmallerThan1kb:
    """Tests for zst_is_smaller_than_1kb."""

    def test_minimal_synthetic_is_small(self):
        """minimal-synthetic.zst is 10 bytes → True."""
        assert zst_is_smaller_than_1kb(_ZST / "minimal-synthetic.zst") is True

    def test_text_compressed_is_small(self):
        """text-compressed.zst is 272 bytes → True."""
        assert zst_is_smaller_than_1kb(_ZST / "text-compressed.zst") is True

    def test_block_128k_is_not_small(self):
        """block-128k.zst is ~131K bytes → False."""
        assert zst_is_smaller_than_1kb(_ZST / "block-128k.zst") is False

    def test_returns_bool(self):
        assert isinstance(zst_is_smaller_than_1kb(_ZST / "minimal-synthetic.zst"), bool)

    def test_two_small_files(self):
        for f in ["minimal-synthetic.zst", "text-compressed.zst"]:
            assert zst_is_smaller_than_1kb(_ZST / f) is True

    def test_small_true_large_false(self):
        r1 = zst_is_smaller_than_1kb(_ZST / "minimal-synthetic.zst")
        r2 = zst_is_smaller_than_1kb(_ZST / "block-128k.zst")
        assert r1 is True and r2 is False


class TestZstSizeExceeds100k:
    """Tests for zst_size_exceeds_100k."""

    def test_minimal_does_not_exceed(self):
        """minimal-synthetic.zst is 10 bytes → False."""
        assert zst_size_exceeds_100k(_ZST / "minimal-synthetic.zst") is False

    def test_text_does_not_exceed(self):
        """text-compressed.zst is 272 bytes → False."""
        assert zst_size_exceeds_100k(_ZST / "text-compressed.zst") is False

    def test_block_128k_exceeds(self):
        """block-128k.zst is ~131K bytes → True."""
        assert zst_size_exceeds_100k(_ZST / "block-128k.zst") is True

    def test_returns_bool(self):
        assert isinstance(zst_size_exceeds_100k(_ZST / "block-128k.zst"), bool)

    def test_two_small_files_do_not_exceed(self):
        for f in ["minimal-synthetic.zst", "text-compressed.zst"]:
            assert zst_size_exceeds_100k(_ZST / f) is False

    def test_large_true_small_false(self):
        r1 = zst_size_exceeds_100k(_ZST / "block-128k.zst")
        r2 = zst_size_exceeds_100k(_ZST / "minimal-synthetic.zst")
        assert r1 is True and r2 is False
