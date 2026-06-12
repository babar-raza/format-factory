"""
format-factory: ZST (Zstandard) FOSS Python track.

Minimal FOSS implementation for Zstandard (.zst) format support.
Acquisition Gates 1-7 PASSED. Implementation authorized: R20 sprint prompt.

FOSS track only — no commercial readiness implied.
See: acquisition-packs/zst/ for gate evidence.
"""

from .zst_codec import (
    ZstError,
    ZstDecompressionError,
    ZstInvalidFrameError,
    ZstOutputLimitExceeded,
    compress_bytes,
    decompress_bytes,
    compress_file,
    decompress_file,
    validate_roundtrip,
    probe_frame,
    validate_file,
    get_frame_info,
    estimate_ratio,
    batch_compress,
    batch_decompress,
    # Sprint 3 (FORMAT-FACTORY-SAL-RECONCILIATION-HARDENING-SPRINT-3, spec_fact_refs=FACT-ZST-001)
    compress_string,
    decompress_to_string,
    # RNEXT (FORMAT-FACTORY-SAL-ENFORCEMENT-CLOSEOUT-AND-PRODUCT-ACCELERATION-RNEXT-001)
    compress_string_to_file,
    decompress_file_to_string,
    get_frame_size_stats,
    is_valid_frame,
    compress_with_dict,
    decompress_with_dict,
    zst_compressed_size,
    zst_is_valid_file,
    zst_decompressed_size,
    zst_frame_count,
)

__all__ = [
    "ZstError",
    "ZstDecompressionError",
    "ZstInvalidFrameError",
    "ZstOutputLimitExceeded",
    "compress_bytes",
    "decompress_bytes",
    "compress_file",
    "decompress_file",
    "validate_roundtrip",
    "probe_frame",
    "validate_file",
    "get_frame_info",
    "estimate_ratio",
    "batch_compress",
    "batch_decompress",
    "compress_string",
    "decompress_to_string",
    "compress_string_to_file",
    "decompress_file_to_string",
    "get_frame_size_stats",
    "is_valid_frame",
    "compress_with_dict",
    "decompress_with_dict",
    "zst_compressed_size",
    "zst_is_valid_file",
    "zst_decompressed_size",
    "zst_frame_count",
]

__version__ = "0.1.0.dev0"
__track__ = "python-foss"
__commercial_ready__ = False
__capability_level__ = "alpha-foss-preview"
