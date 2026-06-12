"""
test_zst_compress_bytes_decompress_bytes.py

Sprint: FORMAT-FACTORY-GAP-DRIVEN-PRODUCT-RNEXT-001
Gap IDs: GAP-ZST-FOSS-COMPRESS_BY-001, GAP-ZST-FOSS-DECOMPRESS_-001

Focused tests for compress_bytes and decompress_bytes functions.
Closes missing_test_coverage gaps for both functions.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

try:
    from zst.zst_codec import compress_bytes, decompress_bytes, ZstError
    _ZST_AVAILABLE = True
except Exception:
    _ZST_AVAILABLE = False

pytestmark = pytest.mark.skipif(not _ZST_AVAILABLE, reason="zstandard not installed")


class TestCompressBytes:
    def test_compress_returns_bytes(self):
        result = compress_bytes(b"hello world")
        assert isinstance(result, bytes)

    def test_compress_output_smaller_or_same_for_repetitive(self):
        data = b"aaaa" * 1000
        compressed = compress_bytes(data)
        assert len(compressed) < len(data)

    def test_compress_nonempty_input_nonempty_output(self):
        result = compress_bytes(b"test data")
        assert len(result) > 0

    def test_compress_empty_bytes(self):
        result = compress_bytes(b"")
        assert isinstance(result, bytes)

    def test_compress_invalid_level_raises(self):
        with pytest.raises(ZstError):
            compress_bytes(b"data", level=0)

    def test_compress_invalid_level_too_high_raises(self):
        with pytest.raises(ZstError):
            compress_bytes(b"data", level=23)

    def test_compress_non_bytes_raises(self):
        with pytest.raises(ZstError):
            compress_bytes("not bytes")  # type: ignore[arg-type]

    def test_compress_level_1(self):
        result = compress_bytes(b"hello", level=1)
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_compress_level_22(self):
        result = compress_bytes(b"hello", level=22)
        assert isinstance(result, bytes)
        assert len(result) > 0


class TestDecompressBytes:
    def test_roundtrip_small(self):
        original = b"hello world"
        compressed = compress_bytes(original)
        result = decompress_bytes(compressed)
        assert result == original

    def test_roundtrip_large(self):
        original = b"repeat " * 10000
        compressed = compress_bytes(original)
        result = decompress_bytes(compressed)
        assert result == original

    def test_roundtrip_empty(self):
        original = b""
        compressed = compress_bytes(original)
        result = decompress_bytes(compressed)
        assert result == original

    def test_invalid_frame_raises(self):
        with pytest.raises(ZstError):
            decompress_bytes(b"not a zstd frame")

    def test_result_is_bytes(self):
        data = b"some test data for compression"
        compressed = compress_bytes(data)
        result = decompress_bytes(compressed)
        assert isinstance(result, bytes)
