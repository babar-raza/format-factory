"""
ZST analytics — pure functions extracted from primary codec/parser.
"""
from __future__ import annotations


spec_qname = "zst:frame"
spec_fact_ref = "SAL-ZST-00001"
namespace_uri = "urn:facebook:zstandard"

from pathlib import Path

from .zst_codec import (
    ZstError,
    ZstDecompressError,
    ZstFileNotFoundError,
    ZstReadError,
)


def zst_compressed_size(path: "str | Path") -> int:
    """Return the file size in bytes of a .zst compressed file.

    Args:
        path: Path to a .zst file.

    Returns:
        Integer byte count of the compressed file.

    Raises:
        FileNotFoundError: If the path does not exist.
        ValueError: If the path is not a file.
    """
    from pathlib import Path as _Path
    p = _Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {p}")
    if not p.is_file():
        raise ValueError(f"Not a file: {p}")
    return p.stat().st_size


def zst_is_valid_file(path: "str | Path") -> bool:
    """Return True if the file at path is a valid Zstandard-compressed file.

    Reads the first 4 bytes to check for the Zstandard magic number
    (0x28B52FFD little-endian). Returns False for missing, empty, or
    non-Zstandard files.

    Args:
        path: Path to the file to check.

    Returns:
        True if the file starts with the Zstandard magic number; False otherwise.
    """
    from pathlib import Path as _Path
    ZST_MAGIC = b'\x28\xb5\x2f\xfd'
    p = _Path(path)
    if not p.exists() or not p.is_file():
        return False
    try:
        header = p.read_bytes()[:4]
    except OSError:
        return False
    return header == ZST_MAGIC


def zst_decompressed_size(path: "str | Path") -> int:
    """Return the byte length of the decompressed content of a ZST file.

    Args:
        path: Path to a Zstandard-compressed file.

    Returns:
        Integer byte count of the decompressed data.

    Raises:
        ZstError subclasses on read or decompression failure.
    """
    from pathlib import Path as _Path
    import zstandard
    p = _Path(path)
    if not p.exists():
        raise ZstFileNotFoundError(f"File not found: {path}")
    try:
        compressed = p.read_bytes()
        dctx = zstandard.ZstdDecompressor()
        try:
            return len(dctx.decompress(compressed))
        except zstandard.ZstdError:
            # Fallback for frames without content size in header
            chunks = []
            with dctx.stream_reader(compressed) as reader:
                while True:
                    chunk = reader.read(65536)
                    if not chunk:
                        break
                    chunks.append(chunk)
            return sum(len(c) for c in chunks)
    except Exception as exc:
        raise ZstDecompressError(f"Failed to decompress {path}: {exc}") from exc


def zst_frame_count(path: "str | Path") -> int:
    """Return the number of Zstandard frames in a ZST file.

    Counts frames by scanning for the Zstandard magic number (0xFD2FB528).
    Standard single-frame files return 1; multi-frame concatenated files return >1.

    Args:
        path: Path to a Zstandard-compressed file.

    Returns:
        Integer count of frames. Returns 0 if the file is empty or not a ZST file.

    Raises:
        ZstError subclasses on read failure.
    """
    from pathlib import Path as _Path
    p = _Path(path)
    if not p.exists():
        raise ZstFileNotFoundError(f"File not found: {path}")
    try:
        data = p.read_bytes()
    except OSError as exc:
        raise ZstReadError(f"Failed to read {path}: {exc}") from exc
    magic = b"\x28\xb5\x2f\xfd"
    count = 0
    pos = 0
    while True:
        idx = data.find(magic, pos)
        if idx == -1:
            break
        count += 1
        pos = idx + 4
    return count


def zst_frame_sizes(path: "str | Path") -> "list[int]":
    """Return the compressed size in bytes of each Zstandard frame in a file.

    Scans the file for Zstandard magic bytes and uses the frame header to
    determine each frame's total size (header + compressed data + checksum).
    For standard single-frame files, returns a list with one element.

    Args:
        path: Path to a Zstandard-compressed file.

    Returns:
        List of frame sizes in bytes, one per frame. Empty list if no frames found.

    Raises:
        ZstFileNotFoundError: If the file does not exist.
        ZstReadError: If the file cannot be read.
    """
    from pathlib import Path as _Path
    p = _Path(path)
    if not p.exists():
        raise ZstFileNotFoundError(f"File not found: {path}")
    try:
        data = p.read_bytes()
    except OSError as exc:
        raise ZstReadError(f"Failed to read {path}: {exc}") from exc

    magic = b"\x28\xb5\x2f\xfd"
    sizes: list[int] = []
    pos = 0
    while True:
        idx = data.find(magic, pos)
        if idx == -1:
            break
        # Find the next frame start (or end of data) to determine frame size
        next_idx = data.find(magic, idx + 4)
        if next_idx == -1:
            frame_size = len(data) - idx
        else:
            frame_size = next_idx - idx
        sizes.append(frame_size)
        pos = idx + 4
    return sizes


def zst_file_info(path: "str | Path") -> dict:
    """Return consolidated analytics for a Zstandard-compressed file.

    Combines compressed_size, decompressed_size, frame_count, compression_ratio,
    and is_valid into a single dict so callers avoid multiple separate calls.

    Args:
        path: Path to a Zstandard-compressed file.

    Returns:
        Dict with keys:
            compressed_size (int): Size of the .zst file in bytes.
            decompressed_size (int): Size after decompression in bytes, or 0 on error.
            frame_count (int): Number of Zstandard frames in the file.
            compression_ratio (float): compressed_size / decompressed_size,
                or 0.0 if decompressed_size is 0.
            is_valid (bool): True if the file passes zst_is_valid_file check.

    Raises:
        ZstFileNotFoundError: If the file does not exist.
        ZstReadError: If the file cannot be read.
    """
    from pathlib import Path as _Path
    p = _Path(path)
    if not p.exists():
        raise ZstError(f"File not found: {path}")
    c_size = zst_compressed_size(path)
    try:
        d_size = zst_decompressed_size(path)
    except Exception:
        d_size = 0
    frames = zst_frame_count(path)
    valid = zst_is_valid_file(path)
    ratio = round(c_size / d_size, 4) if d_size > 0 else 0.0
    return {
        "compressed_size": c_size,
        "decompressed_size": d_size,
        "frame_count": frames,
        "compression_ratio": ratio,
        "is_valid": valid,
    }


def zst_compression_ratio(path: "str | Path") -> float:
    """Return the compression ratio (compressed_size / decompressed_size).

    Returns 0.0 if the file cannot be decompressed or decompressed_size is 0.

    Args:
        path: Path to a Zstandard-compressed file.

    Returns:
        Float ratio, or 0.0 if decompressed size is unavailable.
    """
    c_size = zst_compressed_size(path)
    try:
        d_size = zst_decompressed_size(path)
    except Exception:
        d_size = 0
    if d_size == 0:
        return 0.0
    return c_size / d_size


def zst_is_single_frame(path: "str | Path") -> bool:
    """Return True if the ZST file contains exactly one frame."""
    return zst_frame_count(path) == 1


def zst_max_frame_size(path: "str | Path") -> int:
    """Return the size of the largest frame in bytes; 0 if no frames."""
    frames = zst_frame_sizes(path)
    if not frames:
        return 0
    return max(frames)


def zst_min_frame_size(path: "str | Path") -> int:
    """Return the size of the smallest frame in bytes; 0 if no frames."""
    frames = zst_frame_sizes(path)
    if not frames:
        return 0
    return min(frames)


def zst_is_small_file(path: "str | Path") -> bool:
    """Return True if the compressed file size is less than 128 bytes."""
    return zst_compressed_size(path) < 128


def zst_total_frame_size(path: "str | Path") -> int:
    """Return the sum of all frame sizes in bytes; 0 if no frames."""
    return sum(zst_frame_sizes(path))


def zst_has_multiple_frames(path: "str | Path") -> bool:
    """Return True if the ZST file contains more than one frame."""
    return zst_frame_count(path) > 1


def zst_frame_size_variance(path: "str | Path") -> float:
    """Return the variance of frame sizes. 0.0 if fewer than 2 frames."""
    frames = zst_frame_sizes(path)
    if len(frames) < 2:
        return 0.0
    mean = sum(frames) / len(frames)
    return sum((f - mean) ** 2 for f in frames) / len(frames)


def zst_largest_frame_ratio(path: "str | Path") -> float:
    """Return the ratio of the largest frame to the total size. 0.0 if no frames."""
    total = zst_total_frame_size(path)
    if total == 0:
        return 0.0
    return zst_max_frame_size(path) / total


def zst_smallest_frame_ratio(path: "str | Path") -> float:
    """Return the ratio of the smallest frame to the total size. 0.0 if no frames."""
    total = zst_total_frame_size(path)
    if total == 0:
        return 0.0
    return zst_min_frame_size(path) / total


def zst_frame_count_is_one(path: "str | Path") -> bool:
    """Return True if the file contains exactly one frame."""
    return zst_frame_count(path) == 1


def zst_decompressed_to_compressed_ratio(path: "str | Path") -> float:
    """Return the ratio of decompressed size to compressed size.

    Returns 0.0 if the file cannot be decompressed or compressed_size is 0.

    Args:
        path: Path to a Zstandard-compressed file.

    Returns:
        Float ratio (decompressed / compressed), or 0.0 if unavailable.
    """
    c_size = zst_compressed_size(path)
    if c_size == 0:
        return 0.0
    try:
        d_size = zst_decompressed_size(path)
        return d_size / c_size
    except Exception:
        return 0.0


def zst_frame_median_size(path: "str | Path") -> int:
    """Return the median frame size. 0 if no frames."""
    frames = zst_frame_sizes(path)
    if not frames:
        return 0
    frames_sorted = sorted(frames)
    n = len(frames_sorted)
    if n % 2 == 1:
        return frames_sorted[n // 2]
    return (frames_sorted[n // 2 - 1] + frames_sorted[n // 2]) // 2


def zst_is_large_file(path: "str | Path") -> bool:
    """Return True if compressed size exceeds 1 MiB (1,000,000 bytes)."""
    return zst_compressed_size(path) > 1_000_000


def zst_frame_size_range(path: "str | Path") -> int:
    """Return max frame size minus min frame size. 0 if fewer than 2 frames."""
    frames = zst_frame_sizes(path)
    if len(frames) < 2:
        return 0
    return max(frames) - min(frames)


def zst_is_multi_frame(path: "str | Path") -> bool:
    """Return True if file contains more than one frame."""
    return zst_frame_count(path) > 1


def zst_is_compressible(path: "str | Path") -> bool:
    """Return True if compressed size is less than decompressed size."""
    return zst_compressed_size(path) < zst_decompressed_size(path)


def zst_compression_saving(path: "str | Path") -> int:
    """Return bytes saved by compression. 0 if compressed size >= decompressed size."""
    saving = zst_decompressed_size(path) - zst_compressed_size(path)
    return max(0, saving)


def zst_is_highly_compressed(path: "str | Path") -> bool:
    """Return True if compression ratio exceeds 2.0 (decompressed is >2x compressed).

    A ratio > 2.0 means the decompressed content is more than twice the size
    of the compressed data, indicating high compression effectiveness.

    Args:
        path: Path to a .zst file.

    Returns:
        True if zst_compression_ratio(path) > 2.0, False otherwise.
    """
    return zst_compression_ratio(path) > 2.0


def zst_compression_efficiency(path: "str | Path") -> float:
    """Return the compression efficiency as a fraction of the decompressed size saved.

    Defined as: (decompressed - compressed) / decompressed.
    Bounded to [0.0, 1.0]. Returns 0.0 if decompressed size is 0.

    Args:
        path: Path to a .zst file.

    Returns:
        Float in [0.0, 1.0] representing the fraction of bytes saved.
    """
    decompressed = zst_decompressed_size(path)
    if decompressed == 0:
        return 0.0
    compressed = zst_compressed_size(path)
    saving = decompressed - compressed
    efficiency = saving / decompressed
    return max(0.0, min(1.0, efficiency))


def zst_savings_ratio(path: "str | Path") -> float:
    """Return (decompressed - compressed) / compressed. 0.0 if compressed is 0."""
    compressed = zst_compressed_size(path)
    if compressed == 0:
        return 0.0
    decompressed = zst_decompressed_size(path)
    return (decompressed - compressed) / compressed


def zst_is_rle_efficient(path: "str | Path") -> bool:
    """Return True if decompressed size is more than 100x the compressed size."""
    compressed = zst_compressed_size(path)
    if compressed == 0:
        return False
    return zst_decompressed_size(path) / compressed > 100


def zst_avg_frame_size(path: "str | Path") -> float:
    """Return average frame size in bytes. 0.0 if no frames."""
    frames = zst_frame_count(path)
    if frames == 0:
        return 0.0
    return zst_total_frame_size(path) / frames


def zst_compressed_ratio(path: "str | Path") -> float:
    """Return compressed size divided by decompressed size. 0.0 if decompressed is 0."""
    decompressed = zst_decompressed_size(path)
    if decompressed == 0:
        return 0.0
    return zst_compressed_size(path) / decompressed


def zst_file_size_bytes(path: "str | Path") -> int:
    """Return the size of the ZST file in bytes."""
    from pathlib import Path as _Path
    return _Path(path).stat().st_size


def zst_is_empty_content(path: "str | Path") -> bool:
    """Return True if the decompressed size is zero."""
    return zst_decompressed_size(path) == 0


def zst_decompressed_per_frame(path: "str | Path") -> float:
    """Return average decompressed bytes per frame. 0.0 if no frames."""
    frames = zst_frame_count(path)
    if frames == 0:
        return 0.0
    return zst_decompressed_size(path) / frames


def zst_density(path: "str | Path") -> float:
    """Return compressed-to-decompressed ratio (0.0-1.0). Lower = better compression."""
    decompressed = zst_decompressed_size(path)
    if decompressed == 0:
        return 0.0
    return zst_compressed_size(path) / decompressed


def zst_unique_frame_size_count(path: "str | Path") -> int:
    """Return count of distinct frame sizes. 0 if no frames."""
    sizes = zst_frame_sizes(path)
    return len(set(sizes))


def zst_is_uniform_frames(path: "str | Path") -> bool:
    """Return True if all frames have the same size."""
    sizes = zst_frame_sizes(path)
    return len(set(sizes)) <= 1


def zst_content_type_hint(path: "str | Path") -> str:
    """Return a hint about the content type based on compression characteristics.

    Returns one of: 'highly_compressible', 'moderately_compressible', 'incompressible', 'empty'.
    """
    ratio = zst_compression_ratio(path)
    if ratio == 0.0:
        return "empty"
    elif ratio > 5.0:
        return "highly_compressible"
    elif ratio > 1.5:
        return "moderately_compressible"
    else:
        return "incompressible"


def zst_frame_header_descriptor(path: "str | Path") -> int:
    """Return the frame header descriptor byte (byte at offset 4) of the first ZST frame.

    Returns 0 if the file is too short to contain the descriptor byte.
    """
    data = Path(path).read_bytes()
    return data[4] if len(data) > 4 else 0


def zst_is_minimal_frame(path: "str | Path") -> bool:
    """Return True if the compressed file size is 10 bytes or fewer (minimal frame)."""
    return zst_file_size_bytes(path) <= 10


def zst_magic_valid(path: "str | Path") -> bool:
    """Return True if the file starts with the ZST magic bytes (0xFD2FB528)."""
    data = Path(path).read_bytes()
    return len(data) >= 4 and data[:4] == b"\x28\xb5\x2f\xfd"


def zst_ratio_vs_uncompressed(path: "str | Path") -> float:
    """Return compressed_size / decompressed_size ratio. 0.0 if decompressed is 0."""
    frames = zst_frame_count(path)
    if frames == 0:
        return 0.0
    decomp = zst_decompressed_size(path)
    if decomp == 0:
        return 0.0
    return zst_file_size_bytes(path) / decomp


def zst_bytes_saved(path: "str | Path") -> int:
    """Return decompressed_size - compressed_size (bytes saved). 0 if not compressing."""
    decomp = zst_decompressed_size(path)
    comp = zst_file_size_bytes(path)
    result = decomp - comp
    return max(0, result)


def zst_header_size(path: "str | Path") -> int:
    """Return the ZST frame header size in bytes (minimum 6: magic + FHD + checksum + EOF)."""
    data = Path(path).read_bytes()
    return min(6, len(data))


def zst_frame_count_ratio(path: "str | Path") -> float:
    """Return frames per kilobyte of compressed data."""
    size = zst_file_size_bytes(path)
    if size == 0:
        return 0.0
    return zst_frame_count(path) / (size / 1024.0)


def zst_overhead_bytes(path: "str | Path") -> int:
    """Return compressed_size - sum(frame_sizes). Represents header/metadata overhead."""
    total_frames = sum(zst_frame_sizes(path))
    compressed = zst_file_size_bytes(path)
    return max(0, compressed - total_frames)


def zst_avg_compression_per_byte(path: "str | Path") -> float:
    """Return decompressed_size / compressed_size per byte. 0.0 if compressed is 0."""
    comp = zst_file_size_bytes(path)
    if comp == 0:
        return 0.0
    return zst_decompressed_size(path) / comp


def zst_is_smaller_than_1kb(path: "str | Path") -> bool:
    """Return True if the compressed file size is less than 1024 bytes (1 KiB)."""
    return zst_file_size_bytes(path) < 1024


def zst_size_exceeds_100k(path: "str | Path") -> bool:
    """Return True if the compressed file size exceeds 100,000 bytes."""
    return zst_file_size_bytes(path) > 100_000


def zst_content_entropy(path: "str | Path") -> float:
    """Return Shannon entropy (bits/byte) of the decompressed content. 0.0 if empty."""
    import math
    try:
        import zstandard as zstd
        with open(path, "rb") as fh:
            dctx = zstd.ZstdDecompressor()
            data = dctx.decompress(fh.read(), max_output_size=1 << 24)
    except Exception:
        return 0.0
    if not data:
        return 0.0
    counts: dict[int, int] = {}
    for b in data:
        counts[b] = counts.get(b, 0) + 1
    total = len(data)
    return -sum((c / total) * math.log2(c / total) for c in counts.values())


def zst_avg_byte_value(path: "str | Path") -> float:
    """Return average byte value (0-255) of the decompressed content. 0.0 if empty."""
    try:
        import zstandard as zstd
        with open(path, "rb") as fh:
            dctx = zstd.ZstdDecompressor()
            data = dctx.decompress(fh.read(), max_output_size=1 << 24)
    except Exception:
        return 0.0
    if not data:
        return 0.0
    return sum(data) / len(data)


def zst_size_per_frame(path: "str | Path") -> float:
    """Return compressed file size divided by frame count. 0.0 if no frames."""
    fc = zst_frame_count(path)
    if fc == 0:
        return 0.0
    return zst_file_size_bytes(path) / fc


def zst_byte_ratio(path: "str | Path") -> float:
    """Return ratio of decompressed size to compressed size. 0.0 if no compressed data."""
    cs = zst_file_size_bytes(path)
    if cs == 0:
        return 0.0
    try:
        import zstandard as zstd
        with open(path, "rb") as fh:
            dctx = zstd.ZstdDecompressor()
            data = dctx.decompress(fh.read(), max_output_size=1 << 24)
        return len(data) / cs
    except Exception:
        return 0.0


def zst_compression_savings_ratio(path: "str | Path") -> float:
    """Return (decompressed - compressed) / decompressed. 0.0 if decompressed is 0."""
    try:
        import zstandard as zstd
        with open(path, "rb") as fh:
            dctx = zstd.ZstdDecompressor()
            data = dctx.decompress(fh.read(), max_output_size=1 << 24)
        ds = len(data)
        if ds == 0:
            return 0.0
        cs = zst_file_size_bytes(path)
        return (ds - cs) / ds
    except Exception:
        return 0.0


def zst_size_exceeds_1k(path: "str | Path") -> bool:
    """Return True if compressed file size exceeds 1000 bytes."""
    return zst_compressed_size(path) > 1000
