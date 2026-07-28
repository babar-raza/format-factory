"""
zst_file_stats.py -- File-level statistics for ZST (Zstandard) archives.

Provides 6 derived analytics functions that accept a file path and return
summary properties useful for compression analysis and batch classification.

All functions delegate to compression_metrics helpers for raw data.

License: Apache-2.0
Package: format-factory-zst v0.1.0
"""
from __future__ import annotations

from pathlib import Path


def zst_is_well_compressed(path: "str | Path") -> bool:
    """Return True if the compressed size is less than 50% of the decompressed size.

    A compression ratio below 0.5 (compressed/decompressed) indicates the
    Zstandard encoder achieved at least 2:1 compression effectiveness.

    Args:
        path: Path to the .zst file.

    Returns:
        bool — True if compression_ratio < 0.5.
    """
    from .compression_metrics import zst_compression_ratio
    ratio = zst_compression_ratio(path)
    return ratio < 0.5


def zst_frames_are_equal_size(path: "str | Path") -> bool:
    """Return True if all frames in the ZST file are the same size.

    Compares the minimum and maximum compressed frame sizes. For single-frame
    files this always returns True.

    Args:
        path: Path to the .zst file.

    Returns:
        bool — True if min_frame_size == max_frame_size (or zero frames).
    """
    from .compression_metrics import zst_min_frame_size, zst_max_frame_size
    return zst_min_frame_size(path) == zst_max_frame_size(path)


def zst_is_tiny(path: "str | Path") -> bool:
    """Return True if the compressed file size is less than 100 bytes.

    Useful for quickly filtering trivially small ZST files (e.g., synthetic
    samples or empty-content archives with only format overhead).

    Args:
        path: Path to the .zst file.

    Returns:
        bool — True if compressed_size < 100.
    """
    from .compression_metrics import zst_compressed_size
    return zst_compressed_size(path) < 100


def zst_decompressed_per_frame(path: "str | Path") -> int:
    """Return the integer average decompressed bytes per frame.

    Divides total decompressed size by frame count to give an average frame
    payload size. Returns 0 if the file has no frames.

    Args:
        path: Path to the .zst file.

    Returns:
        int — floor(decompressed_size / frame_count), or 0 if frame_count is 0.
    """
    from .compression_metrics import zst_decompressed_size, zst_frame_count
    frames = zst_frame_count(path)
    if frames == 0:
        return 0
    return zst_decompressed_size(path) // frames


def zst_is_size_reducing(path: "str | Path") -> bool:
    """Return True if the compressed file is smaller than its decompressed content.

    A ZST file is size-reducing when compression_ratio < 1.0, i.e., when the
    Zstandard format overhead does not exceed the space savings from compression.

    Args:
        path: Path to the .zst file.

    Returns:
        bool — True if compressed_size < decompressed_size.
    """
    from .compression_metrics import zst_compressed_size, zst_decompressed_size
    return zst_compressed_size(path) < zst_decompressed_size(path)


def zst_byte_overhead(path: "str | Path") -> int:
    """Return the byte difference between compressed and decompressed sizes.

    A positive value indicates the compressed file is larger than the original
    content (overhead). A negative value indicates space savings.

    Args:
        path: Path to the .zst file.

    Returns:
        int — compressed_size - decompressed_size.
              Negative = space saved; positive = format overhead.
    """
    from .compression_metrics import zst_compressed_size, zst_decompressed_size
    return zst_compressed_size(path) - zst_decompressed_size(path)


def zst_compressed_size_kb(path: "str | Path") -> float:
    """Return the compressed file size in kilobytes.

    Spec: Zstandard frame compressed size (SAL-ZST-00001)
    """
    from .compression_metrics import zst_compressed_size
    return zst_compressed_size(path) / 1024.0


def zst_decompressed_size_kb(path: "str | Path") -> float:
    """Return the decompressed content size in kilobytes.

    Spec: Zstandard frame decompressed content size (SAL-ZST-00001)
    """
    from .compression_metrics import zst_decompressed_size
    return zst_decompressed_size(path) / 1024.0


def zst_has_space_savings(path: "str | Path") -> bool:
    """Return True if the compressed size is strictly less than decompressed size.

    Spec: Zstandard compression effectiveness (SAL-ZST-00001)
    """
    from .compression_metrics import zst_compressed_size, zst_decompressed_size
    return zst_compressed_size(path) < zst_decompressed_size(path)


def zst_ratio_below_half(path: "str | Path") -> bool:
    """Return True if the compression ratio is below 0.5 (high compression).

    Ratio = compressed_size / decompressed_size. Returns False when
    decompressed_size is 0.

    Spec: Zstandard compression ratio (SAL-ZST-00001)
    """
    from .compression_metrics import zst_compressed_size, zst_decompressed_size
    ds = zst_decompressed_size(path)
    if ds == 0:
        return False
    return zst_compressed_size(path) / ds < 0.5


def zst_size_category(path: "str | Path") -> str:
    """Return a size category string based on decompressed content size.

    Categories: 'empty' (0 bytes), 'tiny' (<1 KB), 'small' (<1 MB),
    'medium' (<100 MB), 'large' (>=100 MB).

    Spec: Zstandard decompressed content size (SAL-ZST-00001)
    """
    from .compression_metrics import zst_decompressed_size
    ds = zst_decompressed_size(path)
    if ds == 0:
        return "empty"
    if ds < 1024:
        return "tiny"
    if ds < 1024 * 1024:
        return "small"
    if ds < 100 * 1024 * 1024:
        return "medium"
    return "large"


def zst_is_ratio_above_one(path: "str | Path") -> bool:
    """Return True if compressed size exceeds decompressed size (expansion).

    This occurs when Zstandard cannot compress the content effectively.

    Spec: Zstandard compression ratio (SAL-ZST-00001)
    """
    from .compression_metrics import zst_compressed_size, zst_decompressed_size
    return zst_compressed_size(path) > zst_decompressed_size(path)


def zst_frame_count(path: "str | Path") -> int:
    """Return the number of Zstandard frames in the file.

    Spec: Zstandard frame format (SAL-ZST-00001)
    """
    from .compression_metrics import zst_frame_count as _frame_count
    return _frame_count(path)


def zst_is_single_frame(path: "str | Path") -> bool:
    """Return True if the ZST file contains exactly one frame.

    Spec: Zstandard frame format (SAL-ZST-00001)
    """
    from .compression_metrics import zst_is_single_frame as _is_single
    return _is_single(path)


def zst_magic_valid(path: "str | Path") -> bool:
    """Return True if the file begins with a valid Zstandard magic number.

    Spec: Zstandard frame header magic (SAL-ZST-00001)
    """
    from .compression_metrics import zst_magic_valid as _magic_valid
    return _magic_valid(path)


def zst_is_valid_file(path: "str | Path") -> bool:
    """Return True if the file is a structurally valid Zstandard archive.

    Spec: Zstandard file format (SAL-ZST-00001)
    """
    from .compression_metrics import zst_is_valid_file as _is_valid
    return _is_valid(path)


def zst_bytes_saved(path: "str | Path") -> int:
    """Return the number of bytes saved by compression (decompressed - compressed).

    Negative when the compressed file is larger than the original.

    Spec: Zstandard compression effectiveness (SAL-ZST-00001)
    """
    from .compression_metrics import zst_bytes_saved as _bytes_saved
    return _bytes_saved(path)


def zst_is_empty_content(path: "str | Path") -> bool:
    """Return True if the decompressed content is empty (zero bytes).

    Spec: Zstandard decompressed content (SAL-ZST-00001)
    """
    from .compression_metrics import zst_is_empty_content as _is_empty
    return _is_empty(path)
