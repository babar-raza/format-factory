"""
tests/python/zst/test_r293_zst_inspect_frame.py

Sprint: ff-sprint-s293-zst-frame-inspector-20260626
Authority: RFC 8878 — Zstandard Compression

Tests for zst_inspect_frame() in zst_frame_inspector.py.
"""
from __future__ import annotations

import pytest


def _make_compressed():
    from zst.zst_codec import compress_bytes
    return compress_bytes(b"hello world this is test data")


class TestZstInspectFrameImport:
    def test_importable_from_zst_frame_inspector(self):
        from zst.zst_frame_inspector import zst_inspect_frame
        assert callable(zst_inspect_frame)

    def test_importable_from_package(self):
        import zst
        assert hasattr(zst, "zst_inspect_frame")


class TestZstInspectFrameOutput:
    def test_returns_frame(self):
        from zst.zst_frame_inspector import zst_inspect_frame
        from zst.spec.frame.frame import Frame
        data = _make_compressed()
        frame = zst_inspect_frame(data)
        assert isinstance(frame, Frame)

    def test_frame_has_spec_qname(self):
        from zst.zst_frame_inspector import zst_inspect_frame
        frame = zst_inspect_frame(_make_compressed())
        assert hasattr(frame, "spec_qname")

    def test_frame_qname_value(self):
        from zst.zst_frame_inspector import zst_inspect_frame
        frame = zst_inspect_frame(_make_compressed())
        assert frame.spec_qname == "zst:frame"

    def test_frame_type_is_zstandard(self):
        from zst.zst_frame_inspector import zst_inspect_frame
        frame = zst_inspect_frame(_make_compressed())
        assert frame.frame_type == "zstandard"

    def test_invalid_magic_raises(self):
        from zst.zst_frame_inspector import zst_inspect_frame
        from zst.zst_codec import ZstInvalidFrameError
        with pytest.raises(ZstInvalidFrameError):
            zst_inspect_frame(b"\x00\x01\x02\x03garbage")

    def test_too_short_raises(self):
        from zst.zst_frame_inspector import zst_inspect_frame
        from zst.zst_codec import ZstInvalidFrameError
        with pytest.raises(ZstInvalidFrameError):
            zst_inspect_frame(b"\xfd")

    def test_consistent(self):
        from zst.zst_frame_inspector import zst_inspect_frame
        data = _make_compressed()
        f1 = zst_inspect_frame(data)
        f2 = zst_inspect_frame(data)
        assert f1.frame_type == f2.frame_type
