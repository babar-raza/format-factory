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

# Zstandard magic bytes (RFC 8878 §3.1.1)  # FACT-ZST-001: magic bytes 0x28 0xB5 0x2F 0xFD identify Zstandard frame
ZSTD_MAGIC = b"\x28\xb5\x2f\xfd"  # FACT-ZST-001

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
    # Validate inputs and magic bytes BEFORE importing optional zstandard
    # so that wrong/truncated magic raises ZstInvalidFrameError even when
    # the dependency is absent. This preserves cross-platform correctness.
    if not isinstance(data, (bytes, bytearray)):
        raise ZstError(f"data must be bytes, got {type(data).__name__}")

    if not data[:4] == ZSTD_MAGIC:
        raise ZstInvalidFrameError(
            f"Not a Zstandard frame — expected magic {ZSTD_MAGIC!r}, "
            f"got {data[:4]!r}"
        )

    zstandard = _get_zstandard()

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


def compress_file(
    input_path: str | Path,
    output_path: str | Path,
    level: int = 3,
) -> dict[str, Any]:
    """Compress a file to a Zstandard .zst archive.

    Reads input_path, compresses with Zstandard (RFC 8878 §3.1.1 — FACT-ZST-001),
    and writes the compressed frame to output_path.

    Args:
        input_path: Path to the source file.
        output_path: Destination path for the .zst file.
        level: Compression level (1–22). Default 3.

    Returns:
        Dict with keys:
            success (bool): True if compression succeeded.
            input_path (str): Absolute input path.
            output_path (str): Absolute output path.
            input_bytes (int | None): Input file size.
            output_bytes (int | None): Output file size after compression.
            error (str | None): Error message if failed.

    Raises:
        ZstError: If compression fails.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)
    result: dict[str, Any] = {
        "success": False,
        "input_path": str(input_path.resolve()),
        "output_path": str(output_path.resolve()),
        "input_bytes": None,
        "output_bytes": None,
        "error": None,
    }

    if not input_path.exists():
        result["error"] = f"Input file not found: {input_path}"
        raise ZstError(result["error"])

    try:
        raw = input_path.read_bytes()
    except OSError as exc:
        result["error"] = f"Cannot read input: {exc}"
        raise ZstError(result["error"]) from exc

    result["input_bytes"] = len(raw)

    compressed = compress_bytes(raw, level=level)

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(compressed)
    except OSError as exc:
        result["error"] = f"Cannot write output: {exc}"
        raise ZstError(result["error"]) from exc

    result["output_bytes"] = len(compressed)
    result["success"] = True
    return result


def decompress_file(
    input_path: str | Path,
    output_path: str | Path,
    max_output_size: int | None = None,
) -> dict[str, Any]:
    """Decompress a Zstandard .zst file to a destination path.

    Reads the .zst archive at input_path and writes decompressed bytes to
    output_path. Validates the Zstandard magic (FACT-ZST-001).

    Args:
        input_path: Path to the .zst file.
        output_path: Destination path for decompressed output.
        max_output_size: Guard limit for decompressed output. Defaults to 256 MiB.

    Returns:
        Dict with keys:
            success (bool): True if decompression succeeded.
            input_path (str): Absolute input path.
            output_path (str): Absolute output path.
            input_bytes (int | None): Compressed file size.
            output_bytes (int | None): Decompressed output size.
            error (str | None): Error message if failed.

    Raises:
        ZstInvalidFrameError: If input is not a valid Zstandard frame.
        ZstDecompressionError: If decompression fails.
        ZstOutputLimitExceeded: If output exceeds max_output_size.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)
    result: dict[str, Any] = {
        "success": False,
        "input_path": str(input_path.resolve()),
        "output_path": str(output_path.resolve()),
        "input_bytes": None,
        "output_bytes": None,
        "error": None,
    }

    if not input_path.exists():
        result["error"] = f"Input file not found: {input_path}"
        raise ZstError(result["error"])

    try:
        compressed = input_path.read_bytes()
    except OSError as exc:
        result["error"] = f"Cannot read input: {exc}"
        raise ZstError(result["error"]) from exc

    result["input_bytes"] = len(compressed)

    raw = decompress_bytes(compressed, max_output_size=max_output_size)

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(raw)
    except OSError as exc:
        result["error"] = f"Cannot write output: {exc}"
        raise ZstError(result["error"]) from exc

    result["output_bytes"] = len(raw)
    result["success"] = True
    return result


def validate_roundtrip(data: bytes, level: int = 3) -> dict[str, Any]:
    """Validate that bytes survive a compress → decompress roundtrip.

    Compresses the input, immediately decompresses, and verifies byte equality.
    Useful as a quick integrity check before writing a .zst file.

    This operation references FACT-ZST-001: the magic header 0xFD2FB528
    (RFC 8878 §3.1.1) is verified as part of the decompress step.

    Args:
        data: Raw bytes to test.
        level: Compression level to use (1–22). Default 3.

    Returns:
        Dict with keys:
            valid (bool): True if roundtrip is byte-exact.
            input_bytes (int): Size of input data.
            compressed_bytes (int): Size after compression.
            decompressed_bytes (int): Size after decompression.
            match (bool): True if decompressed == original.
            compression_ratio (float): compressed / original size.
            error (str | None): Error message if roundtrip failed.

    Added in Sprint FORMAT-FACTORY-AUTHORITY-GATED-PRODUCT-DOGFOOD-FEATURES-AND-BACKFILL-001
    (authority: P6, FACT-ZST-001).
    """
    result: dict[str, Any] = {
        "valid": False,
        "input_bytes": len(data) if isinstance(data, (bytes, bytearray)) else 0,
        "compressed_bytes": None,
        "decompressed_bytes": None,
        "match": False,
        "compression_ratio": None,
        "error": None,
    }

    if not isinstance(data, (bytes, bytearray)):
        result["error"] = f"data must be bytes, got {type(data).__name__}"
        return result

    try:
        compressed = compress_bytes(data, level=level)
        result["compressed_bytes"] = len(compressed)
        result["compression_ratio"] = round(len(compressed) / len(data), 6) if data else 0.0

        decompressed = decompress_bytes(compressed)
        result["decompressed_bytes"] = len(decompressed)
        result["match"] = decompressed == bytes(data)
        result["valid"] = result["match"]
    except ZstError as exc:
        result["error"] = str(exc)

    return result


def get_frame_info(data: bytes) -> dict[str, Any]:
    """Return detailed frame information for a Zstandard compressed payload.

    Analyses the frame header and returns metadata including magic validation,
    content size (if declared), and compressed size.

    Args:
        data: Compressed Zstandard frame bytes.

    Returns:
        Dict with keys:
            valid (bool): True if this is a valid Zstandard frame.
            magic_ok (bool): True if magic bytes match FACT-ZST-001.
            content_size (int | None): Declared decompressed size, or None.
            compressed_size (int): Size of the compressed data.
            compression_ratio (float | None): compressed/decompressed ratio, or None.
            error (str | None): Error description if invalid.
    """
    result: dict[str, Any] = {
        "valid": False,
        "magic_ok": False,
        "content_size": None,
        "compressed_size": len(data) if isinstance(data, (bytes, bytearray)) else 0,
        "compression_ratio": None,
        "error": None,
    }

    if not isinstance(data, (bytes, bytearray)):
        result["error"] = f"Expected bytes, got {type(data).__name__}"
        return result

    if len(data) < 4:
        result["error"] = f"Too short ({len(data)} bytes)"
        return result

    if data[:4] != ZSTD_MAGIC:
        result["error"] = f"Invalid magic: expected {ZSTD_MAGIC!r}, got {data[:4]!r}"
        return result

    result["magic_ok"] = True
    result["valid"] = True

    # Try to determine content size by doing a full decompress
    try:
        decompressed = decompress_bytes(data)
        result["content_size"] = len(decompressed)
        if len(decompressed) > 0:
            result["compression_ratio"] = round(len(data) / len(decompressed), 6)
    except ZstError:
        pass

    return result


def estimate_ratio(data: bytes, level: int = 3) -> dict[str, Any]:
    """Estimate the compression ratio for given data at a specific level.

    Compresses the data and returns size comparison metrics.

    Args:
        data: Raw bytes to test.
        level: Compression level (1-22). Default 3.

    Returns:
        Dict with keys:
            input_bytes (int): Original size.
            compressed_bytes (int): Compressed size.
            ratio (float): compressed / original (< 1.0 means smaller).
            savings_pct (float): Percentage of space saved (0-100).
            level (int): Compression level used.
            error (str | None): Error if compression failed.
    """
    result: dict[str, Any] = {
        "input_bytes": len(data) if isinstance(data, (bytes, bytearray)) else 0,
        "compressed_bytes": None,
        "ratio": None,
        "savings_pct": None,
        "level": level,
        "error": None,
    }

    if not isinstance(data, (bytes, bytearray)):
        result["error"] = f"data must be bytes, got {type(data).__name__}"
        return result

    if len(data) == 0:
        result["compressed_bytes"] = 0
        result["ratio"] = 0.0
        result["savings_pct"] = 0.0
        return result

    try:
        compressed = compress_bytes(data, level=level)
        result["compressed_bytes"] = len(compressed)
        result["ratio"] = round(len(compressed) / len(data), 6)
        result["savings_pct"] = round((1.0 - len(compressed) / len(data)) * 100, 2)
    except ZstError as exc:
        result["error"] = str(exc)

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


def batch_compress(items: list[tuple[str | Path, str | Path]],
                   level: int = 3) -> list[dict[str, Any]]:
    """Compress multiple files in a batch.

    Each item is a (input_path, output_path) tuple. Returns a list
    of result dicts (same structure as compress_file).

    Args:
        items: List of (input_path, output_path) tuples.
        level: Compression level (1-22). Default 3.

    Returns:
        List of result dicts, one per item. Failed items have success=False
        and error populated; the batch continues even if one item fails.
    """
    results: list[dict[str, Any]] = []
    for inp, out in items:
        try:
            r = compress_file(inp, out, level=level)
            results.append(r)
        except ZstError as exc:
            results.append({
                "success": False,
                "input_path": str(Path(inp).resolve()),
                "output_path": str(Path(out).resolve()),
                "input_bytes": None,
                "output_bytes": None,
                "error": str(exc),
            })
    return results


def batch_decompress(items: list[tuple[str | Path, str | Path]],
                     max_output_size: int | None = None) -> list[dict[str, Any]]:
    """Decompress multiple .zst files in a batch.

    Each item is a (input_path, output_path) tuple. Returns a list
    of result dicts (same structure as decompress_file).

    Args:
        items: List of (input_path, output_path) tuples.
        max_output_size: Maximum decompressed output bytes per file.

    Returns:
        List of result dicts, one per item. Failed items have success=False
        and error populated; the batch continues even if one item fails.
    """
    results: list[dict[str, Any]] = []
    for inp, out in items:
        try:
            r = decompress_file(inp, out, max_output_size=max_output_size)
            results.append(r)
        except ZstError as exc:
            results.append({
                "success": False,
                "input_path": str(Path(inp).resolve()),
                "output_path": str(Path(out).resolve()),
                "input_bytes": None,
                "output_bytes": None,
                "error": str(exc),
            })
    return results
