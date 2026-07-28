"""
test_r153_zst_file_ops.py

Sprint: FORMAT-FACTORY-AUTHORITY-GATED-PRODUCT-PROGRESS-AND-FORMAT-BACKFILL-MEGA-TRAIN-001
Added: 2026-06-09

Tests for new ZST file-level API:
- compress_file(input_path, output_path, level) -> dict
- decompress_file(input_path, output_path) -> dict

Authority: P6 (SAL-ZST-00001: Zstandard magic 0xFD2FB528, RFC 8878 §3.1.1)
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.zst.zst_codec import (
    compress_file,
    decompress_file,
    ZSTD_MAGIC,
    ZstError,
    ZstInvalidFrameError,
)


class TestCompressFile:
    """compress_file: compress a file to a Zstandard .zst archive."""

    def test_compress_file_produces_output(self, tmp_path):
        """compress_file must produce a non-empty output file."""
        src = tmp_path / "input.txt"
        src.write_bytes(b"Hello from compress_file test!" * 20)
        dst = tmp_path / "output.zst"
        result = compress_file(src, dst)
        assert result["success"] is True
        assert dst.exists()
        assert result["output_bytes"] > 0

    def test_compress_file_result_keys(self, tmp_path):
        """compress_file result dict must contain expected keys."""
        src = tmp_path / "data.bin"
        src.write_bytes(b"\x00" * 100)
        dst = tmp_path / "data.zst"
        result = compress_file(src, dst)
        assert "success" in result
        assert "input_bytes" in result
        assert "output_bytes" in result
        assert "input_path" in result
        assert "output_path" in result
        assert result["error"] is None

    def test_compress_file_input_bytes_matches(self, tmp_path):
        """compress_file must report correct input_bytes."""
        data = b"test data" * 50
        src = tmp_path / "src.txt"
        src.write_bytes(data)
        dst = tmp_path / "src.zst"
        result = compress_file(src, dst)
        assert result["input_bytes"] == len(data)

    def test_compress_file_output_is_valid_zstd(self, tmp_path):
        """compress_file output must begin with Zstandard magic (SAL-ZST-00001)."""
        src = tmp_path / "payload.txt"
        src.write_bytes(b"Zstandard magic test" * 10)
        dst = tmp_path / "payload.zst"
        compress_file(src, dst)
        assert dst.read_bytes()[:4] == ZSTD_MAGIC

    def test_compress_file_missing_input_raises(self, tmp_path):
        """compress_file must raise ZstError for missing input."""
        with pytest.raises(ZstError):
            compress_file(tmp_path / "nonexistent.txt", tmp_path / "out.zst")

    def test_compress_file_custom_level(self, tmp_path):
        """compress_file accepts custom compression level."""
        src = tmp_path / "data.bin"
        src.write_bytes(b"level test " * 100)
        dst1 = tmp_path / "lvl1.zst"
        dst9 = tmp_path / "lvl9.zst"
        r1 = compress_file(src, dst1, level=1)
        r9 = compress_file(src, dst9, level=9)
        assert r1["success"] is True
        assert r9["success"] is True
        assert dst1.read_bytes()[:4] == ZSTD_MAGIC
        assert dst9.read_bytes()[:4] == ZSTD_MAGIC


class TestDecompressFile:
    """decompress_file: decompress a .zst file to original bytes."""

    def test_decompress_file_roundtrip(self, tmp_path):
        """decompress_file must produce the original bytes after compress_file."""
        original = b"Round trip data: " + b"x" * 200
        src = tmp_path / "original.txt"
        src.write_bytes(original)
        zst_path = tmp_path / "compressed.zst"
        compress_file(src, zst_path)

        out_path = tmp_path / "decompressed.txt"
        result = decompress_file(zst_path, out_path)
        assert result["success"] is True
        assert out_path.read_bytes() == original

    def test_decompress_file_result_keys(self, tmp_path):
        """decompress_file result dict must contain expected keys."""
        src = tmp_path / "src.txt"
        src.write_bytes(b"keys check" * 10)
        zst_path = tmp_path / "src.zst"
        compress_file(src, zst_path)
        out_path = tmp_path / "out.txt"
        result = decompress_file(zst_path, out_path)
        assert "success" in result
        assert "input_bytes" in result
        assert "output_bytes" in result
        assert result["error"] is None

    def test_decompress_file_output_bytes_correct(self, tmp_path):
        """decompress_file must report correct output_bytes."""
        data = b"size check " * 50
        src = tmp_path / "src.bin"
        src.write_bytes(data)
        zst_path = tmp_path / "src.zst"
        compress_file(src, zst_path)
        out_path = tmp_path / "out.bin"
        result = decompress_file(zst_path, out_path)
        assert result["output_bytes"] == len(data)

    def test_decompress_file_missing_input_raises(self, tmp_path):
        """decompress_file must raise ZstError for missing input."""
        with pytest.raises(ZstError):
            decompress_file(tmp_path / "ghost.zst", tmp_path / "out.txt")

    def test_decompress_file_invalid_magic_raises(self, tmp_path):
        """decompress_file must raise ZstInvalidFrameError for bad magic."""
        bad = tmp_path / "bad.zst"
        bad.write_bytes(b"\xFF\xFF\xFF\xFF not zstd")
        with pytest.raises(ZstInvalidFrameError):
            decompress_file(bad, tmp_path / "out.txt")
