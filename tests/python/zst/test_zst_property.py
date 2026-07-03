"""
test_zst_property.py -- Property-based tests for the ZST codec.

TC-PBT-001 (2026-07-03): First Hypothesis-backed property tests for ZST.

Properties tested:
  P1  compress_bytes never raises on any bytes input
  P2  Roundtrip: compress → decompress returns original bytes
  P3  Compressed output is always a valid zstd frame (starts with ZSTD magic)
  P4  Compressed size is always > 0
  P5  Decompressing compressed output of N bytes yields N bytes back
"""
from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st

from zst.zst_codec import compress_bytes, decompress_bytes, ZSTD_MAGIC


# ---------------------------------------------------------------------------
# P1: compress_bytes never raises
# ---------------------------------------------------------------------------

@given(data=st.binary(min_size=0, max_size=4096))
@settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
def test_compress_never_raises(data):
    """compress_bytes must not raise on any binary input."""
    result = compress_bytes(data)
    assert isinstance(result, bytes), "compress_bytes must return bytes"


# ---------------------------------------------------------------------------
# P2: Roundtrip identity — compress then decompress returns original
# ---------------------------------------------------------------------------

@given(data=st.binary(min_size=0, max_size=4096))
@settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
def test_roundtrip_identity(data):
    """compress then decompress must return the original bytes exactly."""
    compressed = compress_bytes(data)
    recovered = decompress_bytes(compressed)
    assert recovered == data, (
        f"Roundtrip failed: len(original)={len(data)}, len(recovered)={len(recovered)}"
    )


# ---------------------------------------------------------------------------
# P3: Compressed output begins with ZSTD magic bytes
# ---------------------------------------------------------------------------

@given(data=st.binary(min_size=1, max_size=4096))
@settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow])
def test_compressed_starts_with_magic(data):
    """Output of compress_bytes must begin with the 4-byte ZSTD magic number."""
    compressed = compress_bytes(data)
    assert len(compressed) >= 4, "Compressed frame must be at least 4 bytes"
    magic_bytes = compressed[:4]
    # ZSTD_MAGIC is already bytes in zst_codec
    expected = ZSTD_MAGIC if isinstance(ZSTD_MAGIC, bytes) else ZSTD_MAGIC.to_bytes(4, "little")
    assert magic_bytes == expected, (
        f"Magic mismatch: got {magic_bytes.hex()}, expected {expected.hex()}"
    )


# ---------------------------------------------------------------------------
# P4: Compressed output is always non-empty
# ---------------------------------------------------------------------------

@given(data=st.binary(min_size=0, max_size=4096))
@settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow])
def test_compressed_output_is_nonempty(data):
    """compress_bytes must always produce a non-empty byte string (frame header)."""
    compressed = compress_bytes(data)
    assert len(compressed) > 0, "compress_bytes must never return empty bytes"


# ---------------------------------------------------------------------------
# P5: Decompressed length equals original length
# ---------------------------------------------------------------------------

@given(data=st.binary(min_size=0, max_size=4096))
@settings(max_examples=40, suppress_health_check=[HealthCheck.too_slow])
def test_decompressed_length_matches_original(data):
    """After compress → decompress, the byte length must equal the original."""
    compressed = compress_bytes(data)
    recovered = decompress_bytes(compressed)
    assert len(recovered) == len(data), (
        f"Length mismatch: original={len(data)}, recovered={len(recovered)}"
    )
