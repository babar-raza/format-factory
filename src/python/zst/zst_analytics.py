"""
ZST analytics functions.

Arithmetic combination and derivative functions extracted from zst_codec.py to keep
the core codec file within its baseline_loc_cap of 4210 lines.

Core domain functions remain in zst_codec. These functions are re-exported via
zst_codec's 'from .zst_analytics import *' for backward compatibility.

Do NOT add new functions to this file without a corresponding GAP-ledger entry.
"""
from __future__ import annotations

from pathlib import Path

from .zst_codec import (
    zst_compressed_size,
    zst_decompressed_size,
    zst_file_size_bytes,
    zst_frame_count,
    zst_header_size,
    zst_overhead_bytes,
)


def zst_size_exceeds_50(path: "str | Path") -> bool:
    """Return True if compressed file size exceeds 50 bytes."""
    return zst_compressed_size(path) > 50

def zst_frame_count_exceeds_one(path: "str | Path") -> bool:
    """Return True if the file contains more than one Zstandard frame."""
    return zst_frame_count(path) > 1

def zst_max_byte_value(path: "str | Path") -> int:
    """Return the maximum byte value (0-255) in the decompressed content. 0 if empty."""
    try:
        import zstandard as zstd
        with open(path, "rb") as fh:
            dctx = zstd.ZstdDecompressor()
            data = dctx.decompress(fh.read(), max_output_size=1 << 24)
    except Exception:
        return 0
    return max(data) if data else 0

def zst_min_byte_value(path: "str | Path") -> int:
    """Return the minimum byte value (0-255) in the decompressed content. 0 if empty."""
    try:
        import zstandard as zstd
        with open(path, "rb") as fh:
            dctx = zstd.ZstdDecompressor()
            data = dctx.decompress(fh.read(), max_output_size=1 << 24)
    except Exception:
        return 0
    return min(data) if data else 0

def zst_min_byte_exceeds_zero(path: "str | Path") -> bool:
    """Return True if the minimum decompressed byte value is greater than zero."""
    return zst_min_byte_value(path) > 0

def zst_is_empty_decompressed(path: "str | Path") -> bool:
    """Return True if decompressed size is 0."""
    return zst_decompressed_size(path) == 0

def zst_is_trivial_compression(path: "str | Path") -> bool:
    """Return True if compressed size >= decompressed size (no effective compression)."""
    return zst_compressed_size(path) >= zst_decompressed_size(path)

def zst_byte_range(file_path: "str | Path") -> int:
    """Return max_byte_value minus min_byte_value. 0 if decompressed is empty."""
    return zst_max_byte_value(file_path) - zst_min_byte_value(file_path)

def zst_is_single_byte(file_path: "str | Path") -> bool:
    """Return True if all decompressed bytes have the same value and size > 0."""
    ds = zst_decompressed_size(file_path)
    if ds == 0:
        return False
    return zst_max_byte_value(file_path) == zst_min_byte_value(file_path)
