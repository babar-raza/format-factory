# R95 Train O: ZST Compression Level Variation Tests
# Governed skill: /add-python-object-model-feature
# Ledger: R95-GOVERNED-PYTHON-ZST-LEVEL-VARIATIONS-001
# Sprint: FORMAT-FACTORY-R95-PARALLEL-SPRINT-INTELLIGENCE-CONTEXT-PACK-ACCELERATION-POC-MEGA-TRAIN-001

"""Tests for ZST compression at different levels and with varied data patterns."""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src", "python"))

from zst.zst_codec import compress_bytes, decompress_bytes


class TestZstLevelVariations:
    """R95 ZST compression level and data pattern tests."""

    def test_default_level_roundtrip(self):
        """Default compression level roundtrips correctly."""
        data = b"Hello Format Factory " * 100
        compressed = compress_bytes(data)
        assert decompress_bytes(compressed) == data

    def test_high_level_produces_smaller_output(self):
        """Higher level should produce same or smaller output than default."""
        data = b"Repetitive data pattern " * 500
        default_compressed = compress_bytes(data)
        high_compressed = compress_bytes(data, level=19)
        assert len(high_compressed) <= len(default_compressed) + 10

    def test_level_1_fast_roundtrip(self):
        """Level 1 (fastest) still roundtrips correctly."""
        data = b"Fast compression test " * 200
        compressed = compress_bytes(data, level=1)
        assert decompress_bytes(compressed) == data

    def test_binary_data_roundtrip(self):
        """Binary data with all byte values roundtrips."""
        data = bytes(range(256)) * 50
        compressed = compress_bytes(data)
        assert decompress_bytes(compressed) == data

    def test_empty_bytes_roundtrip(self):
        """Empty bytes roundtrip."""
        compressed = compress_bytes(b"")
        assert decompress_bytes(compressed) == b""

    def test_single_byte_roundtrip(self):
        """Single byte roundtrip."""
        compressed = compress_bytes(b"\x42")
        assert decompress_bytes(compressed) == b"\x42"

    def test_compressed_is_smaller_for_repetitive(self):
        """Compressed output should be smaller than input for repetitive data."""
        data = b"A" * 10000
        compressed = compress_bytes(data)
        assert len(compressed) < len(data)

    def test_compressed_returns_bytes_type(self):
        """compress_bytes returns bytes type."""
        result = compress_bytes(b"test")
        assert isinstance(result, bytes)
