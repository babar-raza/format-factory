"""Tests for zst_frame_header_descriptor and zst_is_minimal_frame (Sprint r300)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.zst.zst_codec import zst_frame_header_descriptor, zst_is_minimal_frame

_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"


class TestZstFrameHeaderDescriptor:
    """Tests for zst_frame_header_descriptor."""

    def test_minimal_synthetic_descriptor_is_32(self):
        """minimal-synthetic.zst: frame header descriptor byte = 32."""
        result = zst_frame_header_descriptor(_ZST / "minimal-synthetic.zst")
        assert result == 32

    def test_text_compressed_descriptor_is_96(self):
        """text-compressed.zst: frame header descriptor byte = 96."""
        result = zst_frame_header_descriptor(_ZST / "text-compressed.zst")
        assert result == 96

    def test_block_128k_descriptor_is_0(self):
        """block-128k.zst: frame header descriptor byte = 0."""
        result = zst_frame_header_descriptor(_ZST / "block-128k.zst")
        assert result == 0

    def test_returns_int(self):
        result = zst_frame_header_descriptor(_ZST / "minimal-synthetic.zst")
        assert isinstance(result, int)

    def test_nonnegative(self):
        for f in ["minimal-synthetic.zst", "text-compressed.zst", "block-128k.zst"]:
            assert zst_frame_header_descriptor(_ZST / f) >= 0

    def test_minimal_and_text_differ(self):
        r1 = zst_frame_header_descriptor(_ZST / "minimal-synthetic.zst")
        r2 = zst_frame_header_descriptor(_ZST / "text-compressed.zst")
        assert r1 != r2


class TestZstIsMinimalFrame:
    """Tests for zst_is_minimal_frame."""

    def test_minimal_synthetic_is_minimal(self):
        """minimal-synthetic.zst is 10 bytes — at threshold."""
        result = zst_is_minimal_frame(_ZST / "minimal-synthetic.zst")
        assert result is True

    def test_text_compressed_is_not_minimal(self):
        """text-compressed.zst is 272 bytes — above threshold."""
        result = zst_is_minimal_frame(_ZST / "text-compressed.zst")
        assert result is False

    def test_block_128k_is_not_minimal(self):
        """block-128k.zst is 131081 bytes — far above threshold."""
        result = zst_is_minimal_frame(_ZST / "block-128k.zst")
        assert result is False

    def test_returns_bool(self):
        result = zst_is_minimal_frame(_ZST / "minimal-synthetic.zst")
        assert isinstance(result, bool)

    def test_larger_files_not_minimal(self):
        for f in ["text-compressed.zst", "block-128k.zst"]:
            assert zst_is_minimal_frame(_ZST / f) is False

    def test_minimal_true_text_false(self):
        r1 = zst_is_minimal_frame(_ZST / "minimal-synthetic.zst")
        r2 = zst_is_minimal_frame(_ZST / "text-compressed.zst")
        assert r1 is True and r2 is False
