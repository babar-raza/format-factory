# R96 Train O: ZST Error Handling Tests
# Governed skill: /add-python-object-model-feature
# Ledger: R96-GOVERNED-PYTHON-ZST-ERROR-HANDLING-001
# Sprint: FORMAT-FACTORY-R96-AUTONOMOUS-CONTINUATION-POC-PRODUCT-DEEPENING-MEGA-TRAIN-001

"""Tests for ZST error handling — invalid input, corrupt data, boundary conditions."""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src", "python"))

from zst.zst_codec import compress_bytes, decompress_bytes


class TestZstErrorHandling:
    """R96 ZST error handling and boundary tests."""

    def test_decompress_invalid_data_raises(self):
        """Decompressing non-ZST data should raise."""
        with pytest.raises(Exception):
            decompress_bytes(b"this is not zst data")

    def test_decompress_empty_raises(self):
        """Decompressing empty bytes should raise."""
        with pytest.raises(Exception):
            decompress_bytes(b"")

    def test_compress_string_raises(self):
        """Compressing a string (not bytes) should raise."""
        with pytest.raises((TypeError, Exception)):
            compress_bytes("this is a string not bytes")

    def test_compress_large_repetitive(self):
        """Large repetitive data compresses efficiently."""
        data = b"X" * 100_000
        compressed = compress_bytes(data)
        assert len(compressed) < len(data) / 10

    def test_roundtrip_unicode_encoded(self):
        """UTF-8 encoded unicode roundtrips."""
        text = "Hello \u00e9\u00e8\u00ea \u4e16\u754c"
        data = text.encode("utf-8")
        assert decompress_bytes(compress_bytes(data)) == data

    def test_compress_at_boundary_level(self):
        """Level 3 (common default) roundtrips correctly."""
        data = b"boundary test " * 100
        compressed = compress_bytes(data, level=3)
        assert decompress_bytes(compressed) == data

    def test_multiple_sequential_roundtrips(self):
        """Multiple sequential compress/decompress cycles work."""
        for i in range(5):
            data = f"iteration {i} data".encode() * 50
            assert decompress_bytes(compress_bytes(data)) == data

    def test_compress_returns_different_from_input(self):
        """Compressed output should differ from input (for non-trivial data)."""
        data = b"Non-trivial test data pattern " * 20
        compressed = compress_bytes(data)
        assert compressed != data
