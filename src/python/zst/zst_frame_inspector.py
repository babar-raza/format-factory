"""
zst_frame_inspector.py — Spec-shaped frame inspection for ZST compressed data.

Authority: RFC 8878 — Zstandard Compression.
Spec QName: zst:frame (urn:ietf:rfc:8878:zstd)
"""
from __future__ import annotations

from .zst_codec import probe_frame, ZSTD_MAGIC, ZstInvalidFrameError
from .spec.frame.frame import Frame


def zst_inspect_frame(data: bytes) -> Frame:
    """Return a spec-shaped Frame object for the first frame in compressed data.

    Args:
        data: Zstandard-compressed bytes containing at least one frame.

    Returns:
        Frame instance (spec class: zst:frame, FACT-ZST-001).

    Raises:
        ZstInvalidFrameError: If data does not start with a valid Zstandard magic.
    """
    if not isinstance(data, (bytes, bytearray)) or len(data) < 4:
        raise ZstInvalidFrameError("Data too short to contain a valid ZST frame")
    if data[:4] != ZSTD_MAGIC:
        raise ZstInvalidFrameError("Data does not start with Zstandard magic bytes")

    frame_info = probe_frame(data)
    return Frame(frame_info)
