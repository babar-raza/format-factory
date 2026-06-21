"""Tests for ZST Sprint 52 gap closure.

Closes:
  GAP-ZST-FOSS-ZST_FRAME_HE-001  (Zst Frame Header Descriptor)
  GAP-ZST-FOSS-ZST_IS_MINIM-001  (Zst Is Minimal Frame)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.zst import zst_frame_header_descriptor, zst_is_minimal_frame

_DIR = _REPO / "samples" / "by-format" / "zst" / "valid"
_MINIMAL = str(_DIR / "minimal-synthetic.zst")
_EMPTY = str(_DIR / "empty-block.zst")
_TEXT = str(_DIR / "text-compressed.zst")


class TestZstFrameHeaderDescriptor:
    def test_return_type(self):
        assert isinstance(zst_frame_header_descriptor(_MINIMAL), int)

    def test_exact_32_for_minimal(self):
        assert zst_frame_header_descriptor(_MINIMAL) == 32

    def test_zero_for_empty(self):
        assert zst_frame_header_descriptor(_EMPTY) == 0

    def test_exact_96_for_text(self):
        assert zst_frame_header_descriptor(_TEXT) == 96

    def test_nonnegative(self):
        assert zst_frame_header_descriptor(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert zst_frame_header_descriptor(_MINIMAL) == zst_frame_header_descriptor(_MINIMAL)


class TestZstIsMinimalFrame:
    def test_return_type(self):
        assert isinstance(zst_is_minimal_frame(_MINIMAL), bool)

    def test_true_for_minimal(self):
        assert zst_is_minimal_frame(_MINIMAL) is True

    def test_false_for_empty(self):
        assert zst_is_minimal_frame(_EMPTY) is False

    def test_false_for_text(self):
        assert zst_is_minimal_frame(_TEXT) is False

    def test_consistent_across_calls(self):
        assert zst_is_minimal_frame(_MINIMAL) == zst_is_minimal_frame(_MINIMAL)
