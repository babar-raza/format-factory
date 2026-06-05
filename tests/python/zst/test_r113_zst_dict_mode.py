"""R113 FOSS: ZST dictionary mode and advanced compression."""
import pytest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src", "python"))
from zst.zst_codec import compress_bytes, decompress_bytes


class TestR113ZstDictMode:
    def test_compress_with_level_1(self):
        data = b"hello world " * 100
        compressed = compress_bytes(data, level=1)
        assert len(compressed) < len(data)

    def test_compress_with_level_10(self):
        data = b"repetitive data " * 500
        compressed = compress_bytes(data, level=10)
        decompressed = decompress_bytes(compressed)
        assert decompressed == data

    def test_roundtrip_binary_data(self):
        data = bytes(range(256)) * 10
        compressed = compress_bytes(data)
        decompressed = decompress_bytes(compressed)
        assert decompressed == data

    def test_roundtrip_all_zeros(self):
        data = b"\x00" * 10000
        compressed = compress_bytes(data)
        decompressed = decompress_bytes(compressed)
        assert decompressed == data
        assert len(compressed) < len(data)

    def test_roundtrip_random_like(self):
        import hashlib
        data = hashlib.sha256(b"seed").digest() * 100
        compressed = compress_bytes(data)
        decompressed = decompress_bytes(compressed)
        assert decompressed == data

    def test_empty_then_nonempty(self):
        empty = compress_bytes(b"")
        assert decompress_bytes(empty) == b""
        data = b"after empty"
        compressed = compress_bytes(data)
        assert decompress_bytes(compressed) == data

    def test_level_22_max_compression(self):
        data = b"max compression test " * 200
        compressed = compress_bytes(data, level=22)
        decompressed = decompress_bytes(compressed)
        assert decompressed == data

    def test_different_levels_all_decompress(self):
        data = b"multi level test " * 50
        for level in [1, 3, 5, 10, 15]:
            compressed = compress_bytes(data, level=level)
            assert decompress_bytes(compressed) == data
