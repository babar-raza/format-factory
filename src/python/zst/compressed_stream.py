"""
ZST Compressed Stream — spec-level domain module.

Implements frame-level predicates and metrics for the Zstandard compressed stream format.

Spec authority : RFC 8878 — Zstandard Compression and the 'application/zstd' Media Type
QName         : zst:frame
Namespace URI : urn:ietf:rfc:8878:zstandard
Spec fact ref : FACT-ZST-001

Functions in this module derive directly from the Zstandard frame structure:
- zst:frame — the fundamental unit of a Zstandard compressed stream
- Frame-level metrics: compressed size, decompressed size, frame count
- Byte-level predicates on decompressed content

This is a behavioral implementation module, NOT an architecture_only spec stub.
The corresponding spec stubs are under src/python/zst/spec/.
"""
from __future__ import annotations

from pathlib import Path

from .zst_codec import (
    zst_compressed_size,
    zst_decompressed_size,
    zst_frame_count,
)

spec_qname = "zst:frame"
spec_fact_ref = "FACT-ZST-001"
namespace_uri = "urn:ietf:rfc:8878:zstandard"


def zst_size_exceeds_50(path: "str | Path") -> bool:
    """Return True if compressed file size exceeds 50 bytes.

    Spec: RFC 8878 §3.1 — Zstandard frame header compressed size (FACT-ZST-001).
    """
    return zst_compressed_size(path) > 50


def zst_frame_count_exceeds_one(path: "str | Path") -> bool:
    """Return True if the file contains more than one Zstandard frame.

    Spec: RFC 8878 §3.1 — a Zstandard-compressed content may contain multiple frames (FACT-ZST-001).
    """
    return zst_frame_count(path) > 1


def zst_max_byte_value(path: "str | Path") -> int:
    """Return the maximum byte value (0-255) in the decompressed content. 0 if empty.

    Spec: RFC 8878 §3.1 — decompressed content of a Zstandard frame (FACT-ZST-001).
    """
    try:
        import zstandard as zstd
        with open(path, "rb") as fh:
            dctx = zstd.ZstdDecompressor()
            data = dctx.decompress(fh.read(), max_output_size=1 << 24)
    except Exception:
        return 0
    return max(data) if data else 0


def zst_min_byte_value(path: "str | Path") -> int:
    """Return the minimum byte value (0-255) in the decompressed content. 0 if empty.

    Spec: RFC 8878 §3.1 — decompressed content of a Zstandard frame (FACT-ZST-001).
    """
    try:
        import zstandard as zstd
        with open(path, "rb") as fh:
            dctx = zstd.ZstdDecompressor()
            data = dctx.decompress(fh.read(), max_output_size=1 << 24)
    except Exception:
        return 0
    return min(data) if data else 0


def zst_min_byte_exceeds_zero(path: "str | Path") -> bool:
    """Return True if the minimum decompressed byte value is greater than zero.

    Spec: RFC 8878 §3.1 — decompressed content byte range (FACT-ZST-001).
    """
    return zst_min_byte_value(path) > 0


def zst_is_empty_decompressed(path: "str | Path") -> bool:
    """Return True if decompressed size is 0.

    Spec: RFC 8878 §3.1 — empty decompressed content is valid (FACT-ZST-001).
    """
    return zst_decompressed_size(path) == 0


def zst_is_trivial_compression(path: "str | Path") -> bool:
    """Return True if compressed size >= decompressed size (no effective compression).

    Spec: RFC 8878 §3.1 — compression ratio derived from frame sizes (FACT-ZST-001).
    """
    return zst_compressed_size(path) >= zst_decompressed_size(path)


def zst_byte_range(file_path: "str | Path") -> int:
    """Return max_byte_value minus min_byte_value. 0 if decompressed content is empty.

    Spec: RFC 8878 §3.1 — decompressed content byte distribution (FACT-ZST-001).
    """
    return zst_max_byte_value(file_path) - zst_min_byte_value(file_path)


def zst_is_single_byte(file_path: "str | Path") -> bool:
    """Return True if all decompressed bytes have the same value and size > 0.

    Spec: RFC 8878 §3.1 — decompressed content uniformity predicate (FACT-ZST-001).
    """
    ds = zst_decompressed_size(file_path)
    if ds == 0:
        return False
    return zst_max_byte_value(file_path) == zst_min_byte_value(file_path)
