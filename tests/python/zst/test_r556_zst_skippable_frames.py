"""Tests for ZST skippable frame support.

FACT-ZST-002: Skippable frames start with 4-byte magic in range
              0x184D2A50 to 0x184D2A5F (16 valid values, little-endian).
FACT-ZST-004: Two frame formats co-exist: Zstandard frames and skippable frames.

Sprint R556 — add-python-object-model-feature
"""
import struct
import pytest


def _make_skippable_frame(payload: bytes, magic: int = 0x184D2A50) -> bytes:
    """Construct a minimal skippable frame (RFC 8878 §3.1.2)."""
    return struct.pack("<II", magic, len(payload)) + payload


class TestIsSkippableFrame:
    """Unit tests for is_skippable_frame."""

    def test_valid_skippable_magic_low(self):
        from zst import is_skippable_frame
        frame = _make_skippable_frame(b"meta")
        assert is_skippable_frame(frame) is True

    def test_valid_skippable_magic_high(self):
        from zst import is_skippable_frame
        frame = _make_skippable_frame(b"meta", magic=0x184D2A5F)
        assert is_skippable_frame(frame) is True

    def test_valid_skippable_magic_mid(self):
        from zst import is_skippable_frame
        frame = _make_skippable_frame(b"x" * 10, magic=0x184D2A57)
        assert is_skippable_frame(frame) is True

    def test_zstandard_frame_is_not_skippable(self):
        from zst import is_skippable_frame
        zstd_magic = b"\x28\xb5\x2f\xfd"
        assert is_skippable_frame(zstd_magic + b"\x00" * 10) is False

    def test_empty_bytes_is_not_skippable(self):
        from zst import is_skippable_frame
        assert is_skippable_frame(b"") is False

    def test_too_short_is_not_skippable(self):
        from zst import is_skippable_frame
        assert is_skippable_frame(b"\x50\x2a\x4d") is False  # only 3 bytes

    def test_random_bytes_not_skippable(self):
        from zst import is_skippable_frame
        assert is_skippable_frame(b"\xff\xff\xff\xff") is False

    def test_magic_just_below_range_not_skippable(self):
        from zst import is_skippable_frame
        below = struct.pack("<I", 0x184D2A4F)  # one below 0x184D2A50
        assert is_skippable_frame(below + b"\x00" * 4) is False

    def test_magic_just_above_range_not_skippable(self):
        from zst import is_skippable_frame
        above = struct.pack("<I", 0x184D2A60)  # one above 0x184D2A5F
        assert is_skippable_frame(above + b"\x00" * 4) is False


class TestHasSkippableFrames:
    """Unit tests for has_skippable_frames."""

    def test_single_skippable_frame(self):
        from zst import has_skippable_frames
        frame = _make_skippable_frame(b"custom metadata")
        assert has_skippable_frames(frame) is True

    def test_no_skippable_frames_empty(self):
        from zst import has_skippable_frames
        assert has_skippable_frames(b"") is False

    def test_no_skippable_frames_random(self):
        from zst import has_skippable_frames
        assert has_skippable_frames(b"\x00" * 16) is False

    def test_multiple_skippable_frames(self):
        from zst import has_skippable_frames
        stream = _make_skippable_frame(b"frame1") + _make_skippable_frame(b"frame2")
        assert has_skippable_frames(stream) is True


class TestGetSkippableFrameCount:
    """Unit tests for get_skippable_frame_count."""

    def test_zero_count_empty(self):
        from zst import get_skippable_frame_count
        assert get_skippable_frame_count(b"") == 0

    def test_single_frame_count(self):
        from zst import get_skippable_frame_count
        frame = _make_skippable_frame(b"payload")
        assert get_skippable_frame_count(frame) == 1

    def test_two_frames_count(self):
        from zst import get_skippable_frame_count
        stream = (
            _make_skippable_frame(b"meta1", magic=0x184D2A50)
            + _make_skippable_frame(b"meta2", magic=0x184D2A5F)
        )
        assert get_skippable_frame_count(stream) == 2

    def test_three_frames_count(self):
        from zst import get_skippable_frame_count
        stream = (
            _make_skippable_frame(b"a")
            + _make_skippable_frame(b"bb", magic=0x184D2A51)
            + _make_skippable_frame(b"ccc", magic=0x184D2A52)
        )
        assert get_skippable_frame_count(stream) == 3

    def test_no_skippable_in_random_bytes(self):
        from zst import get_skippable_frame_count
        assert get_skippable_frame_count(b"\x00\x01\x02\x03" * 4) == 0

    def test_empty_payload_frame(self):
        from zst import get_skippable_frame_count
        frame = _make_skippable_frame(b"")
        assert get_skippable_frame_count(frame) == 1


class TestExtractSkippableFrames:
    """Unit tests for extract_skippable_frames."""

    def test_single_frame_extraction(self):
        from zst import extract_skippable_frames
        payload = b"my metadata"
        frame = _make_skippable_frame(payload)
        result = extract_skippable_frames(frame)
        assert len(result) == 1
        assert result[0] == payload

    def test_two_frames_extraction(self):
        from zst import extract_skippable_frames
        p1 = b"first"
        p2 = b"second payload"
        stream = _make_skippable_frame(p1) + _make_skippable_frame(p2)
        result = extract_skippable_frames(stream)
        assert len(result) == 2
        assert result[0] == p1
        assert result[1] == p2

    def test_empty_stream_returns_empty_list(self):
        from zst import extract_skippable_frames
        assert extract_skippable_frames(b"") == []

    def test_no_skippable_returns_empty_list(self):
        from zst import extract_skippable_frames
        assert extract_skippable_frames(b"\x00" * 20) == []

    def test_empty_payload_frame(self):
        from zst import extract_skippable_frames
        frame = _make_skippable_frame(b"")
        result = extract_skippable_frames(frame)
        assert len(result) == 1
        assert result[0] == b""

    def test_binary_payload_preserved(self):
        from zst import extract_skippable_frames
        payload = bytes(range(256))
        frame = _make_skippable_frame(payload)
        result = extract_skippable_frames(frame)
        assert result[0] == payload

    def test_different_magic_values_all_extracted(self):
        from zst import extract_skippable_frames
        p1 = b"alpha"
        p2 = b"beta"
        p3 = b"gamma"
        stream = (
            _make_skippable_frame(p1, magic=0x184D2A50)
            + _make_skippable_frame(p2, magic=0x184D2A55)
            + _make_skippable_frame(p3, magic=0x184D2A5F)
        )
        result = extract_skippable_frames(stream)
        assert result == [p1, p2, p3]
