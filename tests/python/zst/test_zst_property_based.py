"""Property-based tests for ZST codec using Hypothesis.

TC-CERT-R2-003 certification hardening.
"""
import pytest
from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st

from zst import compress_bytes, decompress_bytes, validate_roundtrip


@given(data=st.binary(min_size=0, max_size=10000))
@settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
def test_compress_decompress_roundtrip(data):
    """compress -> decompress must return original bytes (lossless)."""
    compressed = compress_bytes(data)
    decompressed = decompress_bytes(compressed, max_output_size=0)
    assert decompressed == data


@given(data=st.binary(min_size=1, max_size=5000))
@settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow])
def test_validate_roundtrip_agrees(data):
    """validate_roundtrip must return valid=True for valid data."""
    result = validate_roundtrip(data)
    assert result["valid"] is True


@given(data=st.binary(min_size=0, max_size=8000))
@settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow])
def test_compression_is_deterministic(data):
    """Compressing the same data twice must yield identical output."""
    c1 = compress_bytes(data)
    c2 = compress_bytes(data)
    assert c1 == c2


@given(data=st.binary(min_size=0, max_size=5000))
@settings(max_examples=20, suppress_health_check=[HealthCheck.too_slow])
def test_compressed_starts_with_magic(data):
    """All compressed output must start with the Zstandard magic bytes."""
    compressed = compress_bytes(data)
    assert compressed[:4] == b"\x28\xb5\x2f\xfd"
