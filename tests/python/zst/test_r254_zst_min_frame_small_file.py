"""Tests for zst_min_frame_size and zst_is_small_file (Sprint 44)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.zst import zst_min_frame_size, zst_is_small_file

_DIR = _REPO / "samples" / "by-format" / "zst" / "valid"
_MINIMAL = str(_DIR / "minimal-synthetic.zst")  # 10 bytes: min_frame=10, is_small=True
_EMPTY = str(_DIR / "empty-block.zst")           # 11 bytes: min_frame=11, is_small=True
_BIG = str(_DIR / "block-128k.zst")              # 131081 bytes: min_frame=131081, is_small=False
_TEXT = str(_DIR / "text-compressed.zst")         # 272 bytes: min_frame=272, is_small=False


class TestZstMinFrameSize:
    def test_return_type(self):
        assert isinstance(zst_min_frame_size(_MINIMAL), int)

    def test_exact_10_for_minimal(self):
        # minimal-synthetic.zst: single 10-byte frame
        assert zst_min_frame_size(_MINIMAL) == 10

    def test_exact_11_for_empty(self):
        # empty-block.zst: single 11-byte frame
        assert zst_min_frame_size(_EMPTY) == 11

    def test_exact_for_big(self):
        # block-128k.zst: single large frame
        assert zst_min_frame_size(_BIG) == 131081

    def test_nonnegative(self):
        assert zst_min_frame_size(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert zst_min_frame_size(_MINIMAL) == zst_min_frame_size(_MINIMAL)

    def test_min_le_max(self):
        from src.python.zst import zst_max_frame_size
        assert zst_min_frame_size(_BIG) <= zst_max_frame_size(_BIG)


class TestZstIsSmallFile:
    def test_return_type(self):
        assert isinstance(zst_is_small_file(_MINIMAL), bool)

    def test_true_for_minimal(self):
        # minimal-synthetic.zst: 10 bytes < 128 bytes threshold
        assert zst_is_small_file(_MINIMAL) is True

    def test_true_for_empty_block(self):
        # empty-block.zst: 11 bytes < 128 bytes threshold
        assert zst_is_small_file(_EMPTY) is True

    def test_false_for_big(self):
        # block-128k.zst: 131081 bytes >= 128 bytes threshold
        assert zst_is_small_file(_BIG) is False

    def test_false_for_text(self):
        # text-compressed.zst: 272 bytes >= 128 bytes threshold
        assert zst_is_small_file(_TEXT) is False

    def test_consistent_across_calls(self):
        assert zst_is_small_file(_MINIMAL) == zst_is_small_file(_MINIMAL)
