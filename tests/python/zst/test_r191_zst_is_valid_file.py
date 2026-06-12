"""
tests/python/zst/test_r191_zst_is_valid_file.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT60-001
Tests for zst_is_valid_file() — boolean check for valid Zstandard file.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.zst import zst_is_valid_file, compress_bytes

SAMPLES = _REPO / "samples" / "by-format" / "zst" / "valid"


class TestZstIsValidFile:
    def test_valid_zst_file_returns_true(self):
        """Known valid .zst file returns True."""
        assert zst_is_valid_file(SAMPLES / "minimal-synthetic.zst") is True

    def test_random_data_zst_returns_true(self):
        """Another valid .zst file returns True."""
        assert zst_is_valid_file(SAMPLES / "random-data.zst") is True

    def test_nonexistent_file_returns_false(self):
        """Non-existent file returns False."""
        assert zst_is_valid_file("/does/not/exist.zst") is False

    def test_non_zst_file_returns_false(self, tmp_path):
        """A plain text file returns False (wrong magic)."""
        f = tmp_path / "notazst.txt"
        f.write_bytes(b"Hello, world!")
        assert zst_is_valid_file(f) is False

    def test_compressed_bytes_written_to_file_returns_true(self, tmp_path):
        """Freshly compressed data written to file returns True."""
        compressed = compress_bytes(b"test data for zst validity")
        f = tmp_path / "test.zst"
        f.write_bytes(compressed)
        assert zst_is_valid_file(f) is True

    def test_result_is_bool(self):
        """Result is always a bool."""
        result = zst_is_valid_file(SAMPLES / "minimal-synthetic.zst")
        assert isinstance(result, bool)
