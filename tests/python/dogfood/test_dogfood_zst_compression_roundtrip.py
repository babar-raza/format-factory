"""Dogfood: ZST compression roundtrip pipeline.

Demonstrates: string → compress to file → decompress → verify + file compress/decompress.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

pytest.importorskip("zstandard", reason="python-zstandard not installed")

from src.python.zst.zst_codec import (
    compress_string_to_file,
    decompress_file_to_string,
    compress_file,
    decompress_file,
    zst_compressed_size,
    zst_decompressed_size,
)

_SAMPLE_TEXT = """Format Factory is a multi-format file conversion and analytics library.
It supports many document, spreadsheet, image, and archive formats.
This text will be compressed using Zstandard compression and then decompressed
to verify a complete roundtrip through the ZST codec pipeline.
The quick brown fox jumps over the lazy dog.
""" * 10  # Repeat to get reasonable compression ratio


class TestDogfoodZstCompressionRoundtrip:
    def test_string_compress_creates_file(self, tmp_path):
        """compress_string_to_file creates a .zst file."""
        zst_path = tmp_path / "sample.zst"
        result = compress_string_to_file(_SAMPLE_TEXT, str(zst_path))
        assert zst_path.exists()
        assert zst_path.stat().st_size > 0
        assert isinstance(result, dict)

    def test_string_roundtrip(self, tmp_path):
        """String survives compress → decompress roundtrip."""
        zst_path = tmp_path / "roundtrip.zst"
        compress_string_to_file(_SAMPLE_TEXT, str(zst_path))
        recovered = decompress_file_to_string(str(zst_path))
        assert recovered == _SAMPLE_TEXT

    def test_compression_ratio(self, tmp_path):
        """Compressed file is smaller than original text."""
        zst_path = tmp_path / "ratio.zst"
        compress_string_to_file(_SAMPLE_TEXT, str(zst_path))
        original_size = len(_SAMPLE_TEXT.encode("utf-8"))
        compressed_size = zst_path.stat().st_size
        assert compressed_size < original_size

    def test_file_compress_decompress(self, tmp_path):
        """File-based compress → decompress roundtrip works."""
        src_path = tmp_path / "input.txt"
        src_path.write_text(_SAMPLE_TEXT, encoding="utf-8")
        zst_path = tmp_path / "output.zst"
        out_path = tmp_path / "recovered.txt"
        compress_file(str(src_path), str(zst_path))
        assert zst_path.exists()
        decompress_file(str(zst_path), str(out_path))
        assert out_path.exists()
        assert out_path.read_text(encoding="utf-8") == _SAMPLE_TEXT

    def test_compressed_size(self, tmp_path):
        """zst_compressed_size returns the correct file size."""
        zst_path = tmp_path / "size.zst"
        compress_string_to_file(_SAMPLE_TEXT, str(zst_path))
        size = zst_compressed_size(str(zst_path))
        assert size == zst_path.stat().st_size

    def test_decompressed_size(self, tmp_path):
        """zst_decompressed_size returns the original data size."""
        zst_path = tmp_path / "decsz.zst"
        compress_string_to_file(_SAMPLE_TEXT, str(zst_path))
        dec_size = zst_decompressed_size(str(zst_path))
        original_size = len(_SAMPLE_TEXT.encode("utf-8"))
        assert dec_size == original_size
