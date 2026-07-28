"""Domain model classes for ZST (Zstandard compressed stream).

Classes:
    ZstDocument — typed wrapper providing frame-level metrics via zst_codec

spec_qname: zst:frame
spec_fact_ref: see shared/qname-registry/zst.yaml
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar


class ZstDocument:
    """Typed domain model for a Zstandard (.zst) compressed stream.

    Wraps path-based frame metrics from zst_codec.
    The ZST format is a compressed container; the model exposes
    frame-level statistics without decompressing the full content.
    """

    spec_qname: ClassVar[str] = "zst:frame"
    spec_fact_ref: ClassVar[str] = "SAL-ZST-00001"
    namespace_uri: ClassVar[str] = "urn:ietf:rfc:8878:zstandard"
    local_name: ClassVar[str] = "frame"
    facade_names: ClassVar[list] = []

    def __init__(self, path: str | Path, data: dict[str, Any] | None = None) -> None:
        self._path = Path(path)
        self._data: dict[str, Any] = data or {}

    @classmethod
    def from_file(cls, path: str | Path) -> "ZstDocument":
        """Load frame-level metrics from a .zst file."""
        from .zst_codec import (
            zst_compressed_size,
            zst_decompressed_size,
            zst_frame_count,
        )
        p = Path(path)
        data = {
            "compressed_size": zst_compressed_size(p),
            "decompressed_size": zst_decompressed_size(p),
            "frame_count": zst_frame_count(p),
        }
        return cls(p, data)

    @property
    def compressed_size(self) -> int:
        """Compressed file size in bytes."""
        return int(self._data.get("compressed_size", 0))

    @property
    def decompressed_size(self) -> int:
        """Decompressed content size in bytes."""
        return int(self._data.get("decompressed_size", 0))

    @property
    def frame_count(self) -> int:
        """Number of Zstandard frames in the stream."""
        return int(self._data.get("frame_count", 0))

    @property
    def path(self) -> Path:
        """Path to the source .zst file."""
        return self._path

    @property
    def has_multiple_frames(self) -> bool:
        """True if the stream contains more than one Zstandard frame."""
        return self.frame_count > 1

    @property
    def is_empty(self) -> bool:
        """True if no frames are present (e.g. empty or unrecognised file)."""
        return self.frame_count == 0

    @property
    def compressed_size_kb(self) -> float:
        """Compressed size in kilobytes (compressed_size / 1024.0)."""
        return self.compressed_size / 1024.0

    @property
    def compression_ratio(self) -> float:
        """Ratio of decompressed to compressed size.

        Returns 0.0 if compressed_size is 0.
        A value > 1.0 means the file compresses well.
        """
        if self.compressed_size == 0:
            return 0.0
        return self.decompressed_size / self.compressed_size

    # Additional frame properties (SAL-ZST-00001, SAL-ZST-00002)

    @property
    def is_single_frame(self) -> bool:
        """True if the stream contains exactly one Zstandard frame."""
        return self.frame_count == 1

    @property
    def decompressed_size_kb(self) -> float:
        """Decompressed content size in kilobytes."""
        return self.decompressed_size / 1024.0

    @property
    def is_large(self) -> bool:
        """True if the compressed size is >= 1 MB (1,048,576 bytes)."""
        return self.compressed_size >= 1_048_576

    # Additional size analysis properties (SAL-ZST-00001)

    @property
    def is_heavily_compressed(self) -> bool:
        """True if the compression ratio is >= 5.0 (very high compression)."""
        return self.compression_ratio >= 5.0

    @property
    def decompressed_size_mb(self) -> float:
        """Decompressed content size in megabytes."""
        return self.decompressed_size / 1_048_576.0

    @property
    def is_tiny(self) -> bool:
        """True if the compressed size is less than 1 KB (1,024 bytes)."""
        return self.compressed_size < 1_024

    # Compression quality properties (SAL-ZST-00001, SAL-ZST-00002)

    @property
    def compressed_size_mb(self) -> float:
        """Compressed file size in megabytes."""
        return self.compressed_size / 1_048_576.0

    @property
    def savings_ratio(self) -> float:
        """Fraction of space saved by compression (0.0 if no decompressed data).

        Computed as 1 - (compressed_size / decompressed_size).
        Returns 0.0 when decompressed_size is 0.
        May be negative if compressed file is larger than decompressed.
        """
        if self.decompressed_size == 0:
            return 0.0
        return 1.0 - (self.compressed_size / self.decompressed_size)

    @property
    def is_lossless_verified(self) -> bool:
        """True if compressed_size > 0 and compressed_size < decompressed_size."""
        return self.compressed_size > 0 and self.compressed_size < self.decompressed_size

    @property
    def space_saved_bytes(self) -> int:
        """Bytes saved by compression (0 if no savings or expansion)."""
        return max(0, self.decompressed_size - self.compressed_size)

    @property
    def is_highly_compressible(self) -> bool:
        """True if savings_ratio > 0.9 (more than 90% space saved)."""
        return self.savings_ratio > 0.9

    @property
    def frames_per_mb(self) -> float:
        """Frame count per decompressed MB (0.0 if no decompressed data)."""
        if self.decompressed_size == 0:
            return 0.0
        return self.frame_count / self.decompressed_size_mb

    @property
    def is_multi_frame(self) -> bool:
        """True if the stream contains more than one Zstandard frame."""
        return self.frame_count > 1

    @property
    def compression_class(self) -> str:
        """Classify compression level from savings_ratio.

        Returns one of: 'none', 'low', 'moderate', 'high', 'very_high'.
        """
        r = self.savings_ratio
        if r <= 0.0:
            return "none"
        if r <= 0.5:
            return "low"
        if r <= 0.8:
            return "moderate"
        if r <= 0.9:
            return "high"
        return "very_high"

    @property
    def avg_frame_size_kb(self) -> float:
        """Average compressed bytes per frame in KB (0.0 if no frames)."""
        if self.frame_count == 0:
            return 0.0
        return (self.compressed_size / self.frame_count) / 1024.0

    def to_dict(self) -> dict[str, Any]:
        """Return frame metrics as a dict."""
        return {
            "path": str(self._path),
            **self._data,
        }

    def __repr__(self) -> str:
        return (
            f"ZstDocument(path={self._path.name!r}, "
            f"compressed_size={self.compressed_size}, "
            f"frame_count={self.frame_count})"
        )
