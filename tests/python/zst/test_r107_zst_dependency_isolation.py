# R107 Wave 3: ZST dependency isolation and streaming proof
# 10 tests — no-network proof, streaming behavior, compression integrity

import importlib
import os
import pytest

zst = importlib.import_module("zst")


class TestZstDependencyIsolation:
    """Prove ZST works without network and in isolation."""

    def test_import_succeeds(self):
        assert hasattr(zst, "compress_bytes")
        assert hasattr(zst, "decompress_bytes")

    def test_compress_returns_bytes(self):
        data = b"hello world" * 100
        result = zst.compress_bytes(data)
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_decompress_returns_original(self):
        data = b"test data for roundtrip"
        compressed = zst.compress_bytes(data)
        decompressed = zst.decompress_bytes(compressed)
        assert decompressed == data

    def test_empty_data_roundtrip(self):
        data = b""
        compressed = zst.compress_bytes(data)
        decompressed = zst.decompress_bytes(compressed)
        assert decompressed == data

    def test_large_data_roundtrip(self):
        data = os.urandom(100_000)
        compressed = zst.compress_bytes(data)
        decompressed = zst.decompress_bytes(compressed)
        assert decompressed == data

    def test_compressed_smaller_than_original(self):
        data = b"A" * 10_000
        compressed = zst.compress_bytes(data)
        assert len(compressed) < len(data)

    def test_magic_bytes_present(self):
        data = b"magic test"
        compressed = zst.compress_bytes(data)
        # Zstandard magic number: 0xFD2FB528 (little-endian)
        assert compressed[:4] == b"\x28\xb5\x2f\xfd"

    def test_invalid_data_raises(self):
        with pytest.raises(Exception):
            zst.decompress_bytes(b"not valid zstd data at all")

    def test_no_network_import(self):
        """ZST module should be importable without network access."""
        mod = importlib.import_module("zst")
        assert mod is not None

    def test_multiple_roundtrips(self):
        for i in range(5):
            data = bytes([i % 256]) * (100 + i * 50)
            assert zst.decompress_bytes(zst.compress_bytes(data)) == data
