"""
tests/python/zst/test_r197_zst_analytics.py

Sprint: FORMAT-FACTORY-ABW-ZST-DEEPENING-001
Tests for get_frame_size_stats(), zst_compressed_size(), zst_is_valid_file().
"""
from __future__ import annotations

import sys
import tempfile
import os
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from zst import compress_bytes, get_frame_size_stats, zst_compressed_size, zst_is_valid_file


_DATA = b"Hello world ZST test data repeated for compression. " * 10


def _make_zst_file():
    compressed = compress_bytes(_DATA)
    fd, path = tempfile.mkstemp(suffix=".zst")
    with os.fdopen(fd, "wb") as f:
        f.write(compressed)
    return path


class TestGetFrameSizeStats:
    def test_returns_dict(self):
        compressed = compress_bytes(_DATA)
        result = get_frame_size_stats(compressed)
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        compressed = compress_bytes(_DATA)
        result = get_frame_size_stats(compressed)
        assert "compressed_bytes" in result
        assert "decompressed_bytes" in result
        assert "valid" in result

    def test_valid_is_true_for_valid_data(self):
        compressed = compress_bytes(_DATA)
        result = get_frame_size_stats(compressed)
        assert result["valid"] is True

    def test_compressed_bytes_positive(self):
        compressed = compress_bytes(_DATA)
        result = get_frame_size_stats(compressed)
        assert result["compressed_bytes"] > 0

    def test_decompressed_bytes_larger_for_repetitive_data(self):
        compressed = compress_bytes(_DATA)
        result = get_frame_size_stats(compressed)
        assert result["decompressed_bytes"] > result["compressed_bytes"]

    def test_space_saved_pct_between_0_and_100(self):
        compressed = compress_bytes(_DATA)
        result = get_frame_size_stats(compressed)
        assert 0 <= result.get("space_saved_pct", 0) <= 100


class TestZstCompressedSize:
    def test_returns_int(self):
        path = _make_zst_file()
        try:
            result = zst_compressed_size(path)
            assert isinstance(result, int)
        finally:
            os.unlink(path)

    def test_positive_for_valid_file(self):
        path = _make_zst_file()
        try:
            result = zst_compressed_size(path)
            assert result > 0
        finally:
            os.unlink(path)

    def test_matches_file_size(self):
        path = _make_zst_file()
        try:
            result = zst_compressed_size(path)
            file_size = os.path.getsize(path)
            assert result == file_size
        finally:
            os.unlink(path)


class TestZstIsValidFile:
    def test_valid_zst_file_returns_true(self):
        path = _make_zst_file()
        try:
            assert zst_is_valid_file(path) is True
        finally:
            os.unlink(path)

    def test_returns_bool(self):
        path = _make_zst_file()
        try:
            result = zst_is_valid_file(path)
            assert isinstance(result, bool)
        finally:
            os.unlink(path)
