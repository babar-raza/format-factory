"""Security tests: decompression bomb protection for ZST.

TC-CERT-H-SEC certification hardening.
"""
import pytest

from zst.zst_codec import (
    compress_bytes,
    decompress_bytes,
    ZstOutputLimitExceeded,
    DEFAULT_MAX_OUTPUT_BYTES,
)


def test_decompression_bomb_limit_enforced():
    """decompress_bytes must reject output exceeding max_output_size."""
    # Create data that compresses well (repeat pattern)
    small_data = b"A" * 1024 * 1024  # 1 MiB of repeated bytes
    compressed = compress_bytes(small_data)

    # Decompress with a tiny limit
    with pytest.raises(ZstOutputLimitExceeded):
        decompress_bytes(compressed, max_output_size=1024)


def test_default_max_output_bytes_is_reasonable():
    """DEFAULT_MAX_OUTPUT_BYTES should be set (not infinite)."""
    assert DEFAULT_MAX_OUTPUT_BYTES > 0
    assert DEFAULT_MAX_OUTPUT_BYTES <= 512 * 1024 * 1024  # <= 512 MiB


def test_max_output_size_zero_disables_guard():
    """max_output_size=0 should disable the guard (explicit opt-out)."""
    data = b"test data for compression"
    compressed = compress_bytes(data)
    result = decompress_bytes(compressed, max_output_size=0)
    assert result == data


def test_invalid_magic_rejected():
    """Non-Zstandard data must be rejected."""
    from zst.zst_codec import ZstInvalidFrameError
    with pytest.raises(ZstInvalidFrameError):
        decompress_bytes(b"not a zstandard frame at all")
