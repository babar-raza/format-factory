# R93 Train N: ZST compress/decompress round-trip tests
# Governed skill: /add-python-object-model-feature
# Ledger: R93-GOVERNED-PYTHON-ZST-ROUNDTRIP-001
# Sprint: FORMAT-FACTORY-R93-CONTEXT-PACK-SUPERVISOR-MCP-ACCELERATION-POC-PARALLEL-MEGA-TRAIN-001

import pytest

from zst.zst_codec import (
    compress_bytes,
    decompress_bytes,
    ZstError,
    ZstInvalidFrameError,
    ZSTD_MAGIC,
)


def test_roundtrip_simple_bytes():
    """compress then decompress returns original bytes."""
    original = b"hello world from format factory zst roundtrip"
    compressed = compress_bytes(original)
    result = decompress_bytes(compressed)
    assert result == original


def test_roundtrip_empty_bytes():
    """Compressing and decompressing empty bytes yields empty bytes."""
    original = b""
    compressed = compress_bytes(original)
    result = decompress_bytes(compressed)
    assert result == original


def test_roundtrip_binary_data():
    """Arbitrary binary bytes survive a round-trip."""
    original = bytes(range(256)) * 100
    compressed = compress_bytes(original)
    result = decompress_bytes(compressed)
    assert result == original


def test_compressed_starts_with_zstd_magic():
    """Compressed output always starts with the Zstandard magic bytes."""
    compressed = compress_bytes(b"test data")
    assert compressed[:4] == ZSTD_MAGIC


def test_compressed_smaller_than_large_input():
    """Compressible data should produce output smaller than input."""
    original = b"a" * 10_000
    compressed = compress_bytes(original)
    assert len(compressed) < len(original)


def test_invalid_magic_raises_ZstInvalidFrameError():
    """Passing bytes without Zstandard magic raises ZstInvalidFrameError."""
    with pytest.raises(ZstInvalidFrameError):
        decompress_bytes(b"notazstdframe1234")


def test_compression_level_range():
    """All legal compression levels (1-22) produce valid round-trip output."""
    original = b"level test " * 20
    for level in (1, 3, 9, 22):
        compressed = compress_bytes(original, level=level)
        assert decompress_bytes(compressed) == original


def test_invalid_level_raises_ZstError():
    """Compression level outside 1-22 raises ZstError."""
    with pytest.raises(ZstError):
        compress_bytes(b"data", level=0)
    with pytest.raises(ZstError):
        compress_bytes(b"data", level=23)
