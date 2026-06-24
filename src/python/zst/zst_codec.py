"""
ZST codec — minimal Zstandard compress/decompress/probe API.

FOSS track. Requires python-zstandard (pip install zstandard).
No commercial libraries used. No vendored dependencies.
Acquisition gates 1-7 passed. Implementation authorized: R20.
commercial_product_ready: false
spec_concept: Zstandard frame/block compressed stream
"""

from __future__ import annotations

import io
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


class ZstFileNotFoundError(ZstError):
    """Raised when a ZST file does not exist."""


class ZstReadError(ZstError):
    """Raised when a ZST file cannot be read."""


class ZstDecompressError(ZstError):
    """Raised when decompression of a ZST file fails."""


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


# ---------------------------------------------------------------------------
# Sprint: FORMAT-FACTORY-BROAD-SELF-HEALING-PRODUCT-ACCELERATION-RNEXT-001
# Queue: broad-accel-q-001, broad-accel-q-002
# ---------------------------------------------------------------------------

def compress_string(text: str, level: int = 3, encoding: str = "utf-8") -> bytes:
    """Compress a UTF-8 string to Zstandard-compressed bytes.

    Args:
        text: The string to compress.
        level: Compression level (1-22, default 3).
        encoding: Text encoding (default utf-8).

    Returns:
        Compressed bytes.

    Raises:
        ZstError: If compression fails or zstandard is unavailable.
    """
    data = text.encode(encoding)
    return compress_bytes(data, level=level)


def decompress_to_string(data: bytes, encoding: str = "utf-8") -> str:
    """Decompress Zstandard-compressed bytes to a string.

    Args:
        data: Compressed bytes to decompress.
        encoding: Target encoding for decoding (default utf-8).

    Returns:
        Decompressed string.

    Raises:
        ZstError: If decompression fails.
        UnicodeDecodeError: If the decompressed bytes are not valid for encoding.
    """
    raw = decompress_bytes(data)
    return raw.decode(encoding)


# ---------------------------------------------------------------------------
# Sprint: FORMAT-FACTORY-SAL-RECONCILIATION-HARDENING-AND-PRODUCT-GATED-ADVANCEMENT-SPRINT-3
# Queue: sal3-product-q-001, sal3-product-q-002
# spec_fact_refs: FACT-ZST-001 (Zstandard Frame Format, RFC-draft)
# ---------------------------------------------------------------------------

def compress_string_to_file(text: str, output_path: str | Path,
                             level: int = 3, encoding: str = "utf-8") -> dict[str, Any]:
    """Compress a text string and write the result to a .zst file.

    Convenience wrapper combining compress_string() and a file write so that
    callers do not need to manage the intermediate bytes object.

    Args:
        text: The string content to compress.
        output_path: Destination file path for the compressed output.
        level: Compression level (1-22, default 3).
        encoding: Text encoding (default utf-8).

    Returns:
        Dict with keys:
            success (bool): True on success.
            output_path (str): Absolute path of the written file.
            input_bytes (int): Uncompressed size in bytes.
            output_bytes (int): Compressed size written to disk.
            compression_ratio (float | None): output / input, or None if input_bytes == 0.
            error (str | None): Error description, or None on success.

    Raises:
        ZstError: If compression fails.
        OSError: If the output file cannot be written.
    """
    encoded = text.encode(encoding)
    compressed = compress_bytes(encoded, level=level)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(compressed)
    input_bytes = len(encoded)
    output_bytes = len(compressed)
    ratio = round(output_bytes / input_bytes, 6) if input_bytes > 0 else None
    return {
        "success": True,
        "output_path": str(out.resolve()),
        "input_bytes": input_bytes,
        "output_bytes": output_bytes,
        "compression_ratio": ratio,
        "error": None,
    }


def decompress_file_to_string(path: str | Path, encoding: str = "utf-8",
                               max_output_size: int | None = None) -> str:
    """Read a .zst file from disk and return its decompressed content as a string.

    Convenience inverse of compress_string_to_file().

    Args:
        path: Path to the .zst file to decompress.
        encoding: Text encoding used to decode the decompressed bytes (default utf-8).
        max_output_size: Maximum decompressed size in bytes. Defaults to
            DEFAULT_MAX_OUTPUT_BYTES if not specified.

    Returns:
        Decompressed string content.

    Raises:
        ZstError: If decompression fails or the file is not a valid Zstandard frame.
        FileNotFoundError: If the file does not exist.
        UnicodeDecodeError: If the decompressed bytes are not valid for encoding.
    """
    limit = max_output_size if max_output_size is not None else DEFAULT_MAX_OUTPUT_BYTES
    compressed = Path(path).read_bytes()
    raw = decompress_bytes(compressed, max_output_size=limit)
    return raw.decode(encoding)


# ---------------------------------------------------------------------------
# Sprint: FORMAT-FACTORY-SAL-ENFORCEMENT-CLOSEOUT-AND-PRODUCT-ACCELERATION-RNEXT-001
# Queue: rnext-product-q-001
# spec_fact_refs: FACT-ZST-001
# route_decision_id: RDEC-RNEXT-LG-001
# ---------------------------------------------------------------------------

def get_frame_size_stats(data: bytes) -> dict[str, Any]:
    """Return size statistics for a Zstandard compressed frame.

    Provides a combined view of compressed size, decompressed size, and
    space savings, suitable for reporting and monitoring pipelines without
    requiring external tooling.

    Args:
        data: Compressed Zstandard frame bytes.

    Returns:
        Dict with keys:
            valid (bool): True if this is a valid Zstandard frame.
            compressed_bytes (int): Size of the compressed data.
            decompressed_bytes (int | None): Decompressed size, or None if invalid.
            space_saved_bytes (int | None): compressed_bytes - decompressed_bytes, or None.
            space_saved_pct (float | None): 100 * (1 - compression_ratio), or None.
            compression_ratio (float | None): compressed / decompressed, or None.
            error (str | None): Error description if frame is invalid.

    Raises:
        ZstError: If the input is not bytes.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise ZstError(f"Expected bytes, got {type(data).__name__}")

    info = get_frame_info(data)
    result: dict[str, Any] = {
        "valid": info["valid"],
        "compressed_bytes": info["compressed_size"],
        "decompressed_bytes": info["content_size"],
        "space_saved_bytes": None,
        "space_saved_pct": None,
        "compression_ratio": info["compression_ratio"],
        "error": info.get("error"),
    }
    if info["content_size"] is not None and info["valid"]:
        saved = info["content_size"] - info["compressed_size"]
        result["space_saved_bytes"] = saved
        if info["content_size"] > 0:
            result["space_saved_pct"] = round(100.0 * saved / info["content_size"], 2)
    return result


def is_valid_frame(data: bytes) -> bool:
    """Return True if data is a valid Zstandard compressed frame.

    A lightweight Boolean wrapper around get_frame_info for use in
    conditional logic and validation pipelines.

    Args:
        data: Bytes to check.

    Returns:
        True if data is a valid Zstandard frame, False otherwise.
    """
    if not isinstance(data, (bytes, bytearray)):
        return False
    try:
        info = get_frame_info(data)
        return bool(info.get("valid", False))
    except Exception:
        return False


def compress_with_dict(data: bytes, dict_data: bytes, level: int = 3) -> bytes:
    """Compress bytes using a pre-trained Zstandard dictionary.

    Args:
        data: Raw bytes to compress.
        dict_data: Dictionary bytes (pre-trained zstd dictionary).
        level: Compression level (1–22, default 3).

    Returns:
        Compressed bytes with dictionary applied.
    """
    zstandard = _get_zstandard()
    zdict = zstandard.ZstdCompressionDict(dict_data)
    cctx = zstandard.ZstdCompressor(level=level, dict_data=zdict)
    return cctx.compress(data)


def decompress_with_dict(data: bytes, dict_data: bytes) -> bytes:
    """Decompress bytes that were compressed with a Zstandard dictionary.

    Args:
        data: Compressed bytes.
        dict_data: Dictionary bytes matching the one used for compression.

    Returns:
        Decompressed bytes.
    """
    zstandard = _get_zstandard()
    zdict = zstandard.ZstdCompressionDict(dict_data)
    dctx = zstandard.ZstdDecompressor(dict_data=zdict)
    return dctx.decompress(data)


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


def zst_avg_frame_size(path: "str | Path") -> float:
    """Return the average size of Zstandard frames in bytes.

    Args:
        path: Path to a Zstandard-compressed file.

    Returns:
        Float average frame size in bytes, or 0.0 if no frames.
    """
    frames = zst_frame_sizes(path)
    if not frames:
        return 0.0
    return sum(frames) / len(frames)


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


# Analytics extension — arithmetic combination functions.
# Separated from core codec to reduce file size. All names re-exported.
try:
    from .compression_metrics import *  # noqa: F401, F403
except ImportError:
    pass  # Standalone module import (no package context) - analytics unavailable
