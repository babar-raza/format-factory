"""Tests for ZST is_valid_frame function (rnext39)."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from zst.zst_codec import is_valid_frame, compress_bytes


class TestIsValidFrame:
    def test_valid_compressed_data(self):
        data = compress_bytes(b"hello world")
        assert is_valid_frame(data) is True

    def test_empty_bytes(self):
        assert is_valid_frame(b"") is False

    def test_random_bytes(self):
        assert is_valid_frame(b"\x00\x01\x02\x03garbage") is False

    def test_not_bytes_returns_false(self):
        assert is_valid_frame("not bytes") is False

    def test_large_input(self):
        data = compress_bytes(b"A" * 10000)
        assert is_valid_frame(data) is True

    def test_returns_bool(self):
        data = compress_bytes(b"test")
        result = is_valid_frame(data)
        assert isinstance(result, bool)
