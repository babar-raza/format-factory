# R111 Wave 6: ZST dictionary compression workflow tests
# Tests compress_bytes/decompress_bytes with varying levels and data patterns

import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src/python"))

from zst.zst_codec import compress_bytes, decompress_bytes


def test_compress_decompress_roundtrip_level1():
    data = b"Hello ZST dictionary workflow " * 100
    compressed = compress_bytes(data, level=1)
    decompressed = decompress_bytes(compressed)
    assert decompressed == data


def test_compress_decompress_roundtrip_level10():
    data = b"High compression level test data pattern " * 200
    compressed = compress_bytes(data, level=10)
    decompressed = decompress_bytes(compressed)
    assert decompressed == data


def test_higher_level_produces_smaller_output():
    data = b"Compressible repeated pattern for ratio test " * 500
    c1 = compress_bytes(data, level=1)
    c10 = compress_bytes(data, level=10)
    # Higher level should generally produce smaller or equal output
    assert len(c10) <= len(c1)


def test_compress_empty_bytes():
    compressed = compress_bytes(b"")
    decompressed = decompress_bytes(compressed)
    assert decompressed == b""


def test_compress_single_byte():
    data = b"\x42"
    compressed = compress_bytes(data, level=3)
    decompressed = decompress_bytes(compressed)
    assert decompressed == data


def test_compress_binary_data():
    data = bytes(range(256)) * 10
    compressed = compress_bytes(data, level=5)
    decompressed = decompress_bytes(compressed)
    assert decompressed == data


def test_compress_large_repetitive_data():
    data = b"A" * 100_000
    compressed = compress_bytes(data, level=3)
    assert len(compressed) < len(data) // 10  # significant compression
    decompressed = decompress_bytes(compressed)
    assert decompressed == data


def test_compress_non_bytes_raises():
    with pytest.raises(Exception):
        compress_bytes("not bytes", level=3)
