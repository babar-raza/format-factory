"""Security tests: decompression bomb protection for ZST codec.

TC-CERT-R1-002 certification hardening.
"""
import pytest

from zst import compress_bytes, decompress_bytes, ZstOutputLimitExceeded


def test_decompression_bomb_rejected():
    """decompress_bytes must enforce max_output_size and raise ZstOutputLimitExceeded."""
    # Create data that compresses well (1 MB of zeros -> tiny compressed frame)
    large_data = b"\x00" * (1024 * 1024)
    compressed = compress_bytes(large_data)

    # Attempt to decompress with a limit smaller than the actual output
    with pytest.raises(ZstOutputLimitExceeded):
        decompress_bytes(compressed, max_output_size=1024)


def test_decompression_within_limit_succeeds():
    """decompress_bytes succeeds when output is within limit."""
    small_data = b"hello world" * 10
    compressed = compress_bytes(small_data)
    result = decompress_bytes(compressed, max_output_size=1024 * 1024)
    assert result == small_data


def test_decompression_default_limit_allows_normal_data():
    """Default limit (256 MiB) allows normal-sized data."""
    data = b"test data for compression" * 100
    compressed = compress_bytes(data)
    result = decompress_bytes(compressed)
    assert result == data


def test_zero_limit_disables_guard():
    """max_output_size=0 disables the decompression bomb guard."""
    large_data = b"\x00" * (1024 * 1024)
    compressed = compress_bytes(large_data)
    result = decompress_bytes(compressed, max_output_size=0)
    assert result == large_data
