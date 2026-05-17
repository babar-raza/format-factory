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
    probe_frame,
    validate_file,
)

__all__ = [
    "ZstError",
    "ZstDecompressionError",
    "ZstInvalidFrameError",
    "ZstOutputLimitExceeded",
    "compress_bytes",
    "decompress_bytes",
    "probe_frame",
    "validate_file",
]

__version__ = "0.1.0.dev0"
__track__ = "python-foss"
__commercial_ready__ = False
