"""Property-based tests for ZST codec.

TC-CERT-H-PBT certification hardening.
Uses hypothesis to generate random data and verify compress/decompress roundtrip.
"""
import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st

from zst.zst_codec import compress_bytes, decompress_bytes


@given(data=st.binary(min_size=0, max_size=10000))
@settings(max_examples=100)
def test_compress_decompress_roundtrip(data):
    """compress → decompress must return original data."""
    compressed = compress_bytes(data)
    assert isinstance(compressed, bytes)
    assert len(compressed) > 0
    decompressed = decompress_bytes(compressed)
    assert decompressed == data


@given(data=st.binary(min_size=1, max_size=5000))
@settings(max_examples=50)
def test_compressed_smaller_or_has_framing(data):
    """Compressed output must have valid Zstandard framing (magic bytes)."""
    compressed = compress_bytes(data)
    # Zstandard magic number: 0xFD2FB528
    assert compressed[:4] == b"\x28\xb5\x2f\xfd"


@given(data=st.binary(min_size=0, max_size=5000))
@settings(max_examples=50)
def test_double_compress_decompress(data):
    """Double compression must be reversible."""
    c1 = compress_bytes(data)
    c2 = compress_bytes(c1)
    d2 = decompress_bytes(c2)
    d1 = decompress_bytes(d2)
    assert d1 == data


@given(
    data=st.binary(min_size=100, max_size=5000),
    level=st.integers(min_value=1, max_value=9),
)
@settings(max_examples=30)
def test_compression_levels_all_roundtrip(data, level):
    """All compression levels must produce valid output that decompresses correctly."""
    compressed = compress_bytes(data, level=level)
    decompressed = decompress_bytes(compressed)
    assert decompressed == data


@given(data=st.binary(min_size=0, max_size=1000))
@settings(max_examples=30)
def test_max_output_size_respected(data):
    """decompress with max_output_size must not exceed limit."""
    compressed = compress_bytes(data)
    if len(data) > 100:
        from zst.zst_codec import ZstOutputLimitExceeded
        with pytest.raises(ZstOutputLimitExceeded):
            decompress_bytes(compressed, max_output_size=50)
