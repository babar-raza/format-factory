"""Tests for zst_file_info() — consolidated ZST file analytics.

Taskcard: FOSS-ZST-FILE-INFO-001
Sprint: FORMAT-FACTORY-FORCED-CONTINUATION-EXECUTION-20260613
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.zst import zst_codec as zst


@pytest.fixture()
def zst_file(tmp_path):
    """Create a small .zst file for testing."""
    data = b"hello world format-factory " * 500
    compressed = zst.compress_bytes(data, level=3)
    p = tmp_path / "test.zst"
    p.write_bytes(compressed)
    return p, len(data)


class TestZstFileInfoBasic:
    def test_returns_dict(self, zst_file):
        path, _ = zst_file
        result = zst.zst_file_info(path)
        assert isinstance(result, dict)

    def test_has_all_keys(self, zst_file):
        path, _ = zst_file
        result = zst.zst_file_info(path)
        assert set(result.keys()) == {
            "compressed_size",
            "decompressed_size",
            "frame_count",
            "compression_ratio",
            "is_valid",
        }

    def test_compressed_size_matches_file_size(self, zst_file):
        path, _ = zst_file
        result = zst.zst_file_info(path)
        assert result["compressed_size"] == path.stat().st_size

    def test_decompressed_size_matches_original(self, zst_file):
        path, original_size = zst_file
        result = zst.zst_file_info(path)
        assert result["decompressed_size"] == original_size

    def test_frame_count_is_one(self, zst_file):
        path, _ = zst_file
        result = zst.zst_file_info(path)
        assert result["frame_count"] == 1

    def test_is_valid_true(self, zst_file):
        path, _ = zst_file
        result = zst.zst_file_info(path)
        assert result["is_valid"] is True

    def test_compression_ratio_gt_zero(self, zst_file):
        path, _ = zst_file
        result = zst.zst_file_info(path)
        assert result["compression_ratio"] > 0.0

    def test_compression_ratio_lt_one(self, zst_file):
        """Compressed should be smaller than decompressed for repetitive data."""
        path, _ = zst_file
        result = zst.zst_file_info(path)
        assert result["compression_ratio"] < 1.0


class TestZstFileInfoErrors:
    def test_nonexistent_file_raises(self, tmp_path):
        with pytest.raises(zst.ZstError):
            zst.zst_file_info(tmp_path / "no_such_file.zst")

    def test_accepts_string_path(self, zst_file):
        path, _ = zst_file
        result = zst.zst_file_info(str(path))
        assert isinstance(result, dict)
        assert result["is_valid"] is True
