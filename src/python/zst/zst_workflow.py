"""ZST installed-workflow module for Format Factory FOSS track."""
from __future__ import annotations

from .zst_codec import decompress_bytes, get_frame_info, ZSTD_MAGIC


def zst_installed_workflow(source: "bytes") -> dict:
    """ZST installed-workflow proof: decompress source and return format metadata.

    Args:
        source: Zstandard-compressed bytes.

    Returns:
        dict with keys: format, loaded, compressed_size, decompressed_size, magic_ok.
    """
    magic_ok = (
        isinstance(source, (bytes, bytearray))
        and len(source) >= 4
        and source[:4] == ZSTD_MAGIC
    )
    frame_info = get_frame_info(source) if magic_ok else {}
    try:
        decompressed = decompress_bytes(source)
        loaded = True
        decompressed_size = len(decompressed)
    except Exception:
        loaded = False
        decompressed_size = 0

    return {
        "format": "zstd",
        "loaded": loaded,
        "compressed_size": len(source) if isinstance(source, (bytes, bytearray)) else 0,
        "decompressed_size": decompressed_size,
        "magic_ok": magic_ok,
    }
