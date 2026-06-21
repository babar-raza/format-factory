"""
format-factory: ZST (Zstandard) FOSS Python track.

Minimal FOSS implementation for Zstandard (.zst) format support.
Acquisition Gates 1-7 PASSED. Implementation authorized: R20 sprint prompt.

FOSS track only — no commercial readiness implied.
See: acquisition-packs/zst/ for gate evidence.
"""

# Import all core codec functions and exception classes
from .zst_codec import *  # noqa: F401, F403

# Analytics functions available for backwards compatibility
try:
    from .zst_analytics import *  # noqa: F401, F403
except ImportError:
    pass

# Explicit public API — 32 core functions + exceptions for Gate 11
__all__ = [
    # Exception hierarchy
    "ZstError",
    "ZstDecompressionError",
    "ZstInvalidFrameError",
    "ZstOutputLimitExceeded",
    # Core compress / decompress
    "compress_bytes",
    "decompress_bytes",
    "compress_file",
    "decompress_file",
    # Roundtrip / validation
    "validate_roundtrip",
    "probe_frame",
    "validate_file",
    # Introspection / metadata
    "get_frame_info",
    "estimate_ratio",
    # Batch operations
    "batch_compress",
    "batch_decompress",
    # String convenience wrappers
    "compress_string",
    "decompress_to_string",
    "compress_string_to_file",
    "decompress_file_to_string",
    # Frame statistics
    "get_frame_size_stats",
    "is_valid_frame",
    # Dictionary-based compression
    "compress_with_dict",
    "decompress_with_dict",
    # Derived metrics (spec-backed per FACT-ZST-001)
    "zst_compressed_size",
    "zst_is_valid_file",
    "zst_decompressed_size",
    "zst_frame_count",
    "zst_frame_sizes",
    "zst_avg_frame_size",
    "zst_compression_ratio",
    "zst_max_frame_size",
    "zst_is_single_frame",
]

__version__ = "0.1.0.dev0"
__track__ = "python-foss"
__commercial_ready__ = False
__capability_level__ = "alpha-foss-preview"
