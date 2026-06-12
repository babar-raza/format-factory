"""R112 FOSS: ZST multi-frame / large payload compress/decompress hardening."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src", "python"))
from zst.zst_codec import compress_bytes, decompress_bytes


class TestR112ZstMultiframeHardening:
    def test_compress_empty_bytes(self):
        result = compress_bytes(b"")
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_roundtrip_empty_bytes(self):
        compressed = compress_bytes(b"")
        decompressed = decompress_bytes(compressed)
        assert decompressed == b""

    def test_roundtrip_1kb(self):
        data = b"A" * 1024
        compressed = compress_bytes(data)
        decompressed = decompress_bytes(compressed)
        assert decompressed == data

    def test_roundtrip_64kb(self):
        data = os.urandom(65536)
        compressed = compress_bytes(data)
        decompressed = decompress_bytes(compressed)
        assert decompressed == data

    def test_roundtrip_1mb(self):
        data = os.urandom(1024 * 1024)
        compressed = compress_bytes(data)
        decompressed = decompress_bytes(compressed)
        assert decompressed == data

    def test_compression_ratio_repetitive(self):
        data = b"ABCDEFGH" * 10000
        compressed = compress_bytes(data)
        assert len(compressed) < len(data) // 2

    def test_roundtrip_level_1(self):
        data = b"level test " * 500
        compressed = compress_bytes(data, level=1)
        decompressed = decompress_bytes(compressed)
        assert decompressed == data

    def test_roundtrip_level_22(self):
        data = b"max level " * 500
        compressed = compress_bytes(data, level=22)
        decompressed = decompress_bytes(compressed)
        assert decompressed == data
