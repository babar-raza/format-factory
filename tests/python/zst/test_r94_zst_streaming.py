# R94 Train P: ZST Streaming Compression Tests
# Governed skill: /add-python-object-model-feature
# Ledger: R94-GOVERNED-PYTHON-ZST-STREAMING-001
# Sprint: FORMAT-FACTORY-R94-CONTEXT-PACK-SELF-CONTAINED-DECLARATION-REVIEW-ACCELERATION-POC-PARALLEL-MEGA-TRAIN-001

"""Tests for ZST streaming compression patterns — chunked input, large payloads."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src", "python"))

from zst.zst_codec import compress_bytes, decompress_bytes


class TestZstStreaming:
    """R94 ZST streaming/chunked pattern tests."""

    def test_large_payload_roundtrip(self):
        """1 MB payload compresses and decompresses correctly."""
        data = b"A" * (1024 * 1024)
        compressed = compress_bytes(data)
        assert len(compressed) < len(data), "Should compress repetitive data"
        result = decompress_bytes(compressed)
        assert result == data

    def test_incompressible_data(self):
        """Random-like data still round-trips even if not smaller."""
        import hashlib
        data = hashlib.sha256(b"seed").digest() * 100
        compressed = compress_bytes(data)
        result = decompress_bytes(compressed)
        assert result == data

    def test_multiple_sequential_compressions(self):
        """Multiple calls produce independent compressed blobs."""
        d1 = b"Hello World"
        d2 = b"Goodbye World"
        c1 = compress_bytes(d1)
        c2 = compress_bytes(d2)
        assert c1 != c2
        assert decompress_bytes(c1) == d1
        assert decompress_bytes(c2) == d2

    def test_single_byte(self):
        """Single-byte input round-trips."""
        data = b"\x42"
        result = decompress_bytes(compress_bytes(data))
        assert result == data

    def test_unicode_encoded_payload(self):
        """UTF-8 encoded text round-trips through ZST."""
        text = "Format Factory — ZST compression test 日本語テスト"
        data = text.encode("utf-8")
        result = decompress_bytes(compress_bytes(data))
        assert result.decode("utf-8") == text

    def test_all_byte_values(self):
        """All 256 byte values round-trip."""
        data = bytes(range(256))
        result = decompress_bytes(compress_bytes(data))
        assert result == data

    def test_compressed_smaller_than_zero_entropy(self):
        """All-zeros should compress very well."""
        data = b"\x00" * 10000
        compressed = compress_bytes(data)
        assert len(compressed) < 100, f"Expected high compression, got {len(compressed)} bytes"

    def test_decompression_returns_bytes(self):
        """Decompressed output is always bytes type."""
        data = b"type check"
        result = decompress_bytes(compress_bytes(data))
        assert isinstance(result, bytes)
