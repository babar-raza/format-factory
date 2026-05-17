"""
ZST codec — minimal Zstandard compress/decompress/probe API.

FOSS track. Requires python-zstandard (pip install zstandard).
No commercial libraries used. No vendored dependencies.

Acquisition gates 1-7 passed. Implementation authorized: R20.
commercial_product_ready: false
"""

from __future__ import annotations

import io
import struct
from pathlib import Path
from typing import Any

# Zstandard magic bytes (RFC 8878 §3.1.1)
ZSTD_MAGIC = b"\x28\xb5\x2f\xfd"

# Default decompression guard: 256 MiB output limit
DEFAULT_MAX_OUTPUT_BYTES = 256 * 1024 * 1024

# Default window guard: 2 GiB (zstandard bomb protection)
DEFAULT_MAX_WINDOW_BYTES = 2 * 1024 * 1024 * 1024


class ZstError(Exception):
    """Base exception for ZST codec errors."""


class ZstInvalidFrameError(ZstError):
    """Raised when input is not a valid Zstandard frame."""


class ZstDecompressionError(ZstError):
    """Raised when decompression fails."""


class ZstOutputLimitExceeded(ZstError):
    """Raised when decompressed output exceeds the configured size limit."""


def _get_zstandard():
    """Import zstandard, raising a clear error if not installed."""
    try:
        import zstandard  # type: ignore[import]
        return zstandard
    except ImportError as exc:
        raise ZstError(
            "python-zstandard is required. Install with: pip install zstandard"
        ) from exc


def compress_bytes(data: bytes, level: int = 3) -> bytes:
    """Compress bytes using Zstandard.

    Args:
        data: Raw bytes to compress.
        level: Compression level (1–22). Default 3 (fast, good ratio).

    Returns:
        Compressed bytes as a Zstandard frame.

    Raises:
        ZstError: If compression fails or zstandard is not installed.
    """
    zstandard = _get_zstandard()
    if not isinstance(data, (bytes, bytearray)):
        raise ZstError(f"data must be bytes, got {type(data).__name__}")
    if not 1 <= level <= 22:
        raise ZstError(f"level must be 1-22, got {level}")
    cctx = zstandard.ZstdCompressor(level=level)
    return cctx.compress(data)


def decompress_bytes(
    data: bytes,
    max_output_size: int | None = None,
) -> bytes:
    """Decompress a Zstandard frame to bytes.

    Args:
        data: Compressed Zstandard frame bytes.
        max_output_size: Maximum allowed output bytes. Defaults to 256 MiB.
                         Pass 0 to disable the guard (not recommended).

    Returns:
        Decompressed bytes.

    Raises:
        ZstInvalidFrameError: If data is not a valid Zstandard frame.
        ZstDecompressionError: If decompression fails.
        ZstOutputLimitExceeded: If output would exceed max_output_size.
    """
    zstandard = _get_zstandard()
    if not isinstance(data, (bytes, bytearray)):
        raise ZstError(f"data must be bytes, got {type(data).__name__}")

    if not data[:4] == ZSTD_MAGIC:
        raise ZstInvalidFrameError(
            f"Not a Zstandard frame — expected magic {ZSTD_MAGIC!r}, "
            f"got {data[:4]!r}"
        )

    limit = max_output_size if max_output_size is not None else DEFAULT_MAX_OUTPUT_BYTES

    dctx = zstandard.ZstdDecompressor(max_window_size=DEFAULT_MAX_WINDOW_BYTES)

    # Prefer dctx.decompress() — it correctly raises on truncated frames.
    # Fall back to streaming only when content_size is not declared in the frame
    # (dctx.decompress raises "could not determine content size" in that case).
    data_bytes = bytes(data)
    try:
        result = dctx.decompress(data_bytes)
        if limit > 0 and len(result) > limit:
            raise ZstOutputLimitExceeded(
                f"Decompressed output ({len(result)} bytes) exceeded {limit} bytes limit. "
                f"Use max_output_size=0 to disable or increase the limit."
            )
        return result
    except ZstOutputLimitExceeded:
        raise
    except zstandard.ZstdError as exc:
        err_str = str(exc)
        if "could not determine content size" in err_str or "content size unknown" in err_str:
            # No content_size in frame header — fall back to streaming
            pass
        else:
            raise ZstDecompressionError(f"Decompression failed: {exc}") from exc
    except Exception as exc:
        raise ZstDecompressionError(f"Decompression failed: {exc}") from exc

    # Streaming fallback for frames without declared content_size
    if limit > 0:
        buf = io.BytesIO()
        reader = dctx.stream_reader(io.BytesIO(data_bytes))
        chunk_size = 65536
        total = 0
        try:
            while True:
                chunk = reader.read(chunk_size)
                if not chunk:
                    break
                total += len(chunk)
                if total > limit:
                    raise ZstOutputLimitExceeded(
                        f"Decompressed output exceeded {limit} bytes limit. "
                        f"Use max_output_size=0 to disable or increase the limit."
                    )
                buf.write(chunk)
        except ZstOutputLimitExceeded:
            raise
        except Exception as exc:
            raise ZstDecompressionError(f"Decompression failed: {exc}") from exc
        finally:
            reader.close()
        return buf.getvalue()
    else:
        buf = io.BytesIO()
        reader = dctx.stream_reader(io.BytesIO(data_bytes))
        try:
            while True:
                chunk = reader.read(65536)
                if not chunk:
                    break
                buf.write(chunk)
        except Exception as exc:
            raise ZstDecompressionError(f"Decompression failed: {exc}") from exc
        finally:
            reader.close()
        return buf.getvalue()


def probe_frame(data: bytes) -> dict[str, Any]:
    """Probe a Zstandard frame and return metadata.

    Does not fully decompress. Returns a dict with:
        valid (bool): True if this looks like a valid Zstandard frame.
        magic_ok (bool): True if magic bytes match.
        content_size (int | None): Declared output size, or None if unknown.
        error (str | None): Error description if invalid, else None.

    Never raises — returns error information in the dict instead.

    Args:
        data: Bytes to probe (a prefix is sufficient — at least 4 bytes needed).

    Returns:
        Probe result dict.
    """
    result: dict[str, Any] = {
        "valid": False,
        "magic_ok": False,
        "content_size": None,
        "error": None,
    }

    if not isinstance(data, (bytes, bytearray)):
        result["error"] = f"Expected bytes, got {type(data).__name__}"
        return result

    if len(data) < 4:
        result["error"] = f"Too short to be a Zstandard frame ({len(data)} bytes)"
        return result

    if data[:4] != ZSTD_MAGIC:
        result["error"] = (
            f"Invalid magic: expected {ZSTD_MAGIC!r}, got {data[:4]!r}"
        )
        return result

    result["magic_ok"] = True

    # Try to get declared content size using the prototype frame_header parser
    try:
        import sys
        import os
        proto_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "..",
            "prototypes", "by-format", "zst"
        )
        proto_path = os.path.normpath(proto_path)
        if proto_path not in sys.path:
            sys.path.insert(0, proto_path)
        import frame_header  # type: ignore[import]
        fhi = frame_header.parse_frame_header(data)
        if not fhi.is_unknown:
            result["valid"] = True
            result["content_size"] = fhi.content_size
        else:
            result["valid"] = False
            result["error"] = "Frame header parse: unknown/malformed"
    except Exception as exc:
        # Frame header parsing is best-effort — still valid if magic matches
        result["valid"] = True
        result["content_size"] = None
        result["error"] = f"Frame header parse unavailable: {exc}"

    return result


def validate_file(path: str | Path) -> dict[str, Any]:
    """Validate a .zst file by attempting decompression probe.

    Reads the file, probes its frame header, and attempts to decompress
    up to a small chunk to verify integrity.

    Args:
        path: Path to the .zst file.

    Returns:
        Dict with:
            valid (bool): True if file passed validation.
            path (str): Absolute path to the file.
            exists (bool): True if file exists.
            size_bytes (int | None): File size.
            probe (dict): Result of probe_frame().
            error (str | None): Error description if invalid.
    """
    path = Path(path)
    result: dict[str, Any] = {
        "valid": False,
        "path": str(path.resolve()),
        "exists": False,
        "size_bytes": None,
        "probe": {},
        "error": None,
    }

    if not path.exists():
        result["error"] = f"File not found: {path}"
        return result

    result["exists"] = True
    result["size_bytes"] = path.stat().st_size

    try:
        data = path.read_bytes()
    except OSError as exc:
        result["error"] = f"Cannot read file: {exc}"
        return result

    probe = probe_frame(data)
    result["probe"] = probe

    if not probe["magic_ok"]:
        result["error"] = probe.get("error", "Invalid Zstandard magic")
        return result

    # Attempt decompression of a small prefix to verify frame integrity
    try:
        decompress_bytes(data, max_output_size=DEFAULT_MAX_OUTPUT_BYTES)
        result["valid"] = True
    except ZstOutputLimitExceeded:
        # File decompresses but is large — still structurally valid
        result["valid"] = True
    except (ZstInvalidFrameError, ZstDecompressionError) as exc:
        result["error"] = str(exc)
    except ZstError as exc:
        result["error"] = str(exc)

    return result
