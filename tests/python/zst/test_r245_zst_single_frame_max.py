"""Tests for zst_is_single_frame and zst_max_frame_size (Sprint 35)."""
import sys
import tempfile
import os
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.zst import zst_is_single_frame, zst_max_frame_size, compress_bytes

_ZST_DIR = _REPO / "samples" / "by-format" / "zst" / "valid"
_MINIMAL = str(_ZST_DIR / "minimal-synthetic.zst")  # single frame, size=10


def _make_multi_frame(tmp_path, data_list):
    """Create a multi-frame ZST by concatenating compressed frames."""
    frames = b"".join(compress_bytes(d) for d in data_list)
    p = tmp_path / "multi.zst"
    p.write_bytes(frames)
    return str(p)


def _make_single_frame(tmp_path, data):
    p = tmp_path / "single.zst"
    p.write_bytes(compress_bytes(data))
    return str(p)


class TestZstIsSingleFrame:
    def test_return_type(self):
        result = zst_is_single_frame(_MINIMAL)
        assert isinstance(result, bool)

    def test_true_for_single_frame_file(self):
        assert zst_is_single_frame(_MINIMAL) is True

    def test_false_for_multi_frame(self, tmp_path):
        p = _make_multi_frame(tmp_path, [b"frame1" * 50, b"frame2" * 50])
        assert zst_is_single_frame(p) is False

    def test_true_for_synthetic_single(self, tmp_path):
        p = _make_single_frame(tmp_path, b"single frame data" * 100)
        assert zst_is_single_frame(p) is True

    def test_consistent_across_calls(self):
        assert zst_is_single_frame(_MINIMAL) == zst_is_single_frame(_MINIMAL)


class TestZstMaxFrameSize:
    def test_return_type(self):
        result = zst_max_frame_size(_MINIMAL)
        assert isinstance(result, int)

    def test_nonnegative(self):
        assert zst_max_frame_size(_MINIMAL) >= 0

    def test_exact_for_minimal(self):
        # minimal-synthetic.zst has one frame of size 10
        assert zst_max_frame_size(_MINIMAL) == 10

    def test_max_for_multi_frame(self, tmp_path):
        # frame1 compressed size > frame2 compressed size (more data)
        frame1 = compress_bytes(b"a" * 1000)
        frame2 = compress_bytes(b"b" * 10)
        p = tmp_path / "multi.zst"
        p.write_bytes(frame1 + frame2)
        result = zst_max_frame_size(str(p))
        assert result == max(len(frame1), len(frame2))

    def test_returns_int_type(self, tmp_path):
        p = _make_single_frame(tmp_path, b"data" * 100)
        assert isinstance(zst_max_frame_size(p), int)
