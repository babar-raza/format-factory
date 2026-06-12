"""R170 — ZST compress_with_dict and decompress_with_dict tests.

Sprint: FORMAT-FACTORY-PROOF-CLOSED-SELF-HEALING-PROFESSIONALIZE-PRODUCT-READINESS-RNEXT-001
"""
from __future__ import annotations

import pytest

from src.python.zst.zst_codec import (
    compress_with_dict,
    decompress_with_dict,
    _get_zstandard,
)


def _make_dict_data() -> bytes:
    """Create a minimal zstd dictionary from repeated content."""
    zstandard = _get_zstandard()
    # Use training data similar to what we'll compress
    samples = [b"Hello World! Format Factory Test Data. " * 10] * 5
    try:
        return zstandard.ZstdCompressionDict(samples[0]).as_bytes()
    except Exception:
        # Fallback: use raw bytes as dict (works for testing)
        return samples[0]


_SAMPLE_DATA = b"Hello World! Format Factory. " * 50
_DICT_DATA = b"Hello World! Format Factory. " * 100


class TestCompressWithDict:
    def test_returns_bytes(self):
        result = compress_with_dict(_SAMPLE_DATA, _DICT_DATA)
        assert isinstance(result, bytes)

    def test_compressed_is_non_empty(self):
        result = compress_with_dict(_SAMPLE_DATA, _DICT_DATA)
        assert len(result) > 0

    def test_compressed_differs_from_input(self):
        result = compress_with_dict(_SAMPLE_DATA, _DICT_DATA)
        assert result != _SAMPLE_DATA

    def test_roundtrip_decompresses_correctly(self):
        compressed = compress_with_dict(_SAMPLE_DATA, _DICT_DATA)
        decompressed = decompress_with_dict(compressed, _DICT_DATA)
        assert decompressed == _SAMPLE_DATA

    def test_small_data_roundtrip(self):
        data = b"small test"
        compressed = compress_with_dict(data, _DICT_DATA)
        decompressed = decompress_with_dict(compressed, _DICT_DATA)
        assert decompressed == data

    def test_empty_data_roundtrip(self):
        data = b""
        compressed = compress_with_dict(data, _DICT_DATA)
        decompressed = decompress_with_dict(compressed, _DICT_DATA)
        assert decompressed == data

    def test_function_in_all(self):
        from src.python.zst import __all__ as zst_all
        assert "compress_with_dict" in zst_all


class TestDecompressWithDict:
    def test_returns_bytes(self):
        compressed = compress_with_dict(_SAMPLE_DATA, _DICT_DATA)
        result = decompress_with_dict(compressed, _DICT_DATA)
        assert isinstance(result, bytes)

    def test_decompressed_matches_original(self):
        compressed = compress_with_dict(_SAMPLE_DATA, _DICT_DATA)
        result = decompress_with_dict(compressed, _DICT_DATA)
        assert result == _SAMPLE_DATA

    def test_roundtrip_preserves_length(self):
        data = b"x" * 1000
        compressed = compress_with_dict(data, _DICT_DATA)
        result = decompress_with_dict(compressed, _DICT_DATA)
        assert len(result) == len(data)

    def test_function_in_all(self):
        from src.python.zst import __all__ as zst_all
        assert "decompress_with_dict" in zst_all
