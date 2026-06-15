"""
pgm_parser.py — PGM (Portable Graymap) parser for format-factory-pgm.

Public API:
  parse_pgm(file_path)        — returns result dict (never raises)
  parse_pgm_strict(file_path) — raises PgmError on failure
  probe_pgm(file_path)        — returns header metadata without full parse

Implements Gate 4 prototype + Gate 5 neutral model.
Parses P2 (ASCII) and P5 (binary) PGM files.
Technology: Python stdlib only (open/read/split).

R55 Train F: P5 binary decode added (TC-BINARY-PGM-001).

License: Apache-2.0
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


MAX_FILE_SIZE = 64 * 1024 * 1024  # 64 MiB
MAX_DIMENSION = 65536
MAX_MAXVAL = 65535

# Magic number constants (Netpbm spec — FACT-PGM-001, FACT-PGM-002)
# FACT-PGM-001: "PGM ASCII format starts with magic 'P2' followed by whitespace"
# FACT-PGM-002: "PGM binary format starts with magic 'P5' followed by whitespace"
PGM_MAGIC_ASCII = "P2"   # FACT-PGM-001
PGM_MAGIC_BINARY = "P5"  # FACT-PGM-002


class PgmError(Exception):
    """Base exception for PGM parser errors."""


class PgmInvalidMagicError(PgmError):
    """Raised when file does not start with P2 or P5."""


class PgmInvalidHeaderError(PgmError):
    """Raised when header fields are invalid."""


class PgmSizeError(PgmError):
    """Raised when file or image dimensions exceed limits."""


class PgmDecodeError(PgmError):
    """Raised when pixel data is malformed."""


@dataclass
class PgmImage:
    width: int = 0
    height: int = 0
    maxval: int = 255
    magic: str = "P2"
    pixels: list[int] = field(default_factory=list)
    path: str = ""


def _strip_comments(text: str) -> str:
    """Remove # comments from PGM text."""
    lines = text.split("\n")
    cleaned = []
    for line in lines:
        idx = line.find("#")
        if idx >= 0:
            line = line[:idx]
        cleaned.append(line)
    return "\n".join(cleaned)


def _parse_netpbm_header_bytes(data: bytes, num_ints: int) -> tuple[list[int], int]:
    """Parse ASCII Netpbm header from raw bytes, skipping comments.

    Returns (values, data_offset) where data_offset is the byte position
    immediately after the single whitespace delimiter following the last
    header integer (i.e., where binary pixel data begins).
    """
    i = 0
    n = len(data)

    def skip_ws_and_comments() -> None:
        nonlocal i
        while i < n:
            b = data[i:i+1]
            if b in (b' ', b'\t', b'\n', b'\r'):
                i += 1
            elif b == b'#':
                while i < n and data[i:i+1] != b'\n':
                    i += 1
            else:
                break

    # Skip past the magic word
    skip_ws_and_comments()
    while i < n and data[i:i+1] not in (b' ', b'\t', b'\n', b'\r'):
        i += 1

    # Read num_ints integer tokens
    values: list[int] = []
    for _ in range(num_ints):
        skip_ws_and_comments()
        start = i
        while i < n and data[i:i+1] not in (b' ', b'\t', b'\n', b'\r'):
            i += 1
        if start == i:
            raise ValueError("Unexpected end of header")
        values.append(int(data[start:i]))

    # Consume exactly one whitespace byte (the separator before binary data)
    if i < n:
        i += 1

    return values, i


def _parse_p5_binary(path: Path, data: bytes) -> "PgmImage":
    """Decode a P5 (binary) PGM file from raw bytes."""
    try:
        (width, height, maxval), data_offset = _parse_netpbm_header_bytes(data, 3)
    except (ValueError, IndexError) as exc:
        raise PgmInvalidHeaderError(f"Invalid P5 header: {exc}")

    if width <= 0 or height <= 0:
        raise PgmInvalidHeaderError(f"Invalid dimensions: {width}x{height}")
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        raise PgmSizeError(f"Dimensions {width}x{height} exceed limit of {MAX_DIMENSION}")
    if maxval <= 0 or maxval > MAX_MAXVAL:
        raise PgmInvalidHeaderError(f"Invalid maxval: {maxval}")

    bytes_per_sample = 2 if maxval > 255 else 1
    expected_pixels = width * height
    expected_bytes = expected_pixels * bytes_per_sample
    pixel_data = data[data_offset:]

    if len(pixel_data) < expected_bytes:
        raise PgmDecodeError(
            f"Not enough binary pixel data: expected {expected_bytes} bytes, "
            f"got {len(pixel_data)}"
        )

    pixels: list[int] = []
    if bytes_per_sample == 1:
        for i in range(expected_pixels):
            v = pixel_data[i]
            if v > maxval:
                raise PgmDecodeError(f"Pixel {i} value {v} out of range [0,{maxval}]")
            pixels.append(v)
    else:
        for i in range(expected_pixels):
            v = (pixel_data[i * 2] << 8) | pixel_data[i * 2 + 1]
            if v > maxval:
                raise PgmDecodeError(f"Pixel {i} value {v} out of range [0,{maxval}]")
            pixels.append(v)

    return PgmImage(
        width=width, height=height, maxval=maxval,
        magic="P5", pixels=pixels, path=str(path),
    )


def parse_pgm_strict(file_path: str | Path) -> PgmImage:
    """Parse a PGM (P2 ASCII or P5 binary) file, raising PgmError on any problem."""
    path = Path(file_path)
    if not path.exists():
        raise PgmError(f"File not found: {path}")

    size = os.path.getsize(path)
    if size > MAX_FILE_SIZE:
        raise PgmSizeError(f"File size {size} exceeds limit of {MAX_FILE_SIZE}")

    # Detect magic from first bytes (works for both ASCII and binary)
    data = path.read_bytes()
    header_probe = data[:16].decode("ascii", errors="replace").split()
    if not header_probe:
        raise PgmInvalidMagicError("Empty file")
    magic = header_probe[0]
    if magic not in ("P2", "P5"):
        raise PgmInvalidMagicError(f"Invalid magic: '{magic}', expected P2 or P5")

    if magic == "P5":
        return _parse_p5_binary(path, data)

    # P2 ASCII path
    raw = data.decode("ascii", errors="replace")
    cleaned = _strip_comments(raw)
    tokens = cleaned.split()

    if len(tokens) < 4:
        raise PgmInvalidHeaderError(
            f"Incomplete header: need magic, width, height, maxval; got {len(tokens)} tokens"
        )

    try:
        width = int(tokens[1])
        height = int(tokens[2])
        maxval = int(tokens[3])
    except ValueError as exc:
        raise PgmInvalidHeaderError(f"Invalid header values: {exc}")

    if width <= 0 or height <= 0:
        raise PgmInvalidHeaderError(f"Invalid dimensions: {width}x{height}")
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        raise PgmSizeError(
            f"Dimensions {width}x{height} exceed limit of {MAX_DIMENSION}"
        )
    if maxval <= 0 or maxval > MAX_MAXVAL:
        raise PgmInvalidHeaderError(f"Invalid maxval: {maxval}")

    expected_pixels = width * height
    pixel_tokens = tokens[4:]

    if len(pixel_tokens) < expected_pixels:
        raise PgmDecodeError(
            f"Not enough pixel data: expected {expected_pixels} values, got {len(pixel_tokens)}"
        )

    pixels: list[int] = []
    for i in range(expected_pixels):
        try:
            v = int(pixel_tokens[i])
        except (ValueError, IndexError) as exc:
            raise PgmDecodeError(f"Invalid pixel data at pixel {i}: {exc}")
        if v < 0 or v > maxval:
            raise PgmDecodeError(
                f"Pixel {i} value {v} out of range [0,{maxval}]"
            )
        pixels.append(v)

    return PgmImage(
        width=width,
        height=height,
        maxval=maxval,
        magic=magic,
        pixels=pixels,
        path=str(path),
    )


def parse_pgm(file_path: str | Path) -> dict[str, Any]:
    """Parse a PGM file, returning a result dict (never raises)."""
    try:
        img = parse_pgm_strict(file_path)
        return {
            "ok": True,
            "path": img.path,
            "width": img.width,
            "height": img.height,
            "maxval": img.maxval,
            "magic": img.magic,
            "pixel_count": len(img.pixels),
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc), "error_type": type(exc).__name__}


def probe_pgm(file_path: str | Path) -> dict[str, Any]:
    """Probe a PGM file for header metadata without full parse."""
    path = Path(file_path)
    result: dict[str, Any] = {"path": str(path), "exists": path.exists()}
    if not path.exists():
        return result
    try:
        raw = path.read_bytes()[:1024].decode("ascii", errors="replace")
        cleaned = _strip_comments(raw)
        tokens = cleaned.split()
        if not tokens or tokens[0] not in ("P2", "P5"):
            result["valid_header"] = False
            result["error"] = f"Invalid magic: {tokens[0] if tokens else 'empty'}"
            return result
        result["valid_header"] = True
        result["magic"] = tokens[0]
        if len(tokens) >= 4:
            result["width"] = int(tokens[1])
            result["height"] = int(tokens[2])
            result["maxval"] = int(tokens[3])
    except Exception as exc:
        result["valid_header"] = False
        result["error"] = str(exc)
    return result


# ---------------------------------------------------------------------------
# R73 Train G: image pixel statistics API
# ---------------------------------------------------------------------------

def image_pixel_stats(file_path: str | Path) -> dict[str, Any]:
    """Return pixel-level statistics for a PGM image.

    Returns a dict with:
      ok: bool
      min_value: int  — minimum pixel value found
      max_value: int  — maximum pixel value found
      mean_approx: float  — approximate mean pixel value
      total_pixels: int
      maxval: int, width: int, height: int, magic: str
    """
    try:
        img = parse_pgm_strict(file_path)
        total = len(img.pixels)
        if total == 0:
            return {
                "ok": True,
                "min_value": 0,
                "max_value": 0,
                "mean_approx": 0.0,
                "total_pixels": 0,
                "maxval": img.maxval,
                "width": img.width,
                "height": img.height,
                "magic": img.magic,
            }
        return {
            "ok": True,
            "min_value": min(img.pixels),
            "max_value": max(img.pixels),
            "mean_approx": round(sum(img.pixels) / total, 4),
            "total_pixels": total,
            "maxval": img.maxval,
            "width": img.width,
            "height": img.height,
            "magic": img.magic,
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc), "error_type": type(exc).__name__}


# ---------------------------------------------------------------------------
# Gate 5 — Neutral model: capability declaration
# ---------------------------------------------------------------------------

SUPPORTED_FEATURES: frozenset[str] = frozenset({
    "p2_ascii_parse",
    "p5_binary_parse",
    "grayscale_pixel_decode",
    "comment_stripping",
    "probe",
    "dimension_extraction",
    "maxval_validation",
    "size_guard",
})

UNSUPPORTED_FEATURES: frozenset[str] = frozenset({
    "ppm_color",
    "pbm_bitmap",
    "pam_arbitrary_map",
    "16bit_values",
    "encoding_to_pgm",
    "color_profiles",
    "metadata_extraction",
    "streaming_decode",
})


def get_capabilities() -> dict[str, Any]:
    """Return a capability descriptor for the PGM parser (Gate 5 neutral model)."""
    return {
        "format": "pgm",
        "gate": 5,
        "supported": sorted(SUPPORTED_FEATURES),
        "unsupported": sorted(UNSUPPORTED_FEATURES),
        "commercial_product_ready": False,
    }


def write_pgm(
    pixels: list[int],
    width: int,
    height: int,
    maxval: int,
    file_path: str | Path,
    *,
    comment: str = "",
) -> None:
    """Write a PGM P2 (ASCII portable graymap) file.

    Pixels must be a flat list of integer values in row-major order.
    The list length must equal width * height.
    Each pixel value must be in range [0, maxval].

    Args:
        pixels: Flat row-major list of grayscale pixel values.
        width: Image width in pixels.
        height: Image height in pixels.
        maxval: Maximum pixel value (1-65535).
        file_path: Destination file path.
        comment: Optional comment line to include in the header (no newlines).

    Raises:
        ValueError: If pixels length does not match width * height, or maxval out of range.
        PgmSizeError: If dimensions exceed MAX_DIMENSION.

    Added in R84 Train M as Netpbm write/roundtrip product advancement.
    """
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        raise PgmSizeError(f"Dimension {width}x{height} exceeds limit {MAX_DIMENSION}")
    if not (1 <= maxval <= MAX_MAXVAL):
        raise ValueError(f"maxval {maxval} must be in range 1-{MAX_MAXVAL}")
    if len(pixels) != width * height:
        raise ValueError(
            f"pixels length {len(pixels)} does not match width*height {width * height}"
        )

    out_path = Path(file_path)
    lines = ["P2"]
    if comment:
        safe_comment = comment.replace("\n", " ").replace("\r", " ")
        lines.append(f"# {safe_comment}")
    lines.append(f"{width} {height}")
    lines.append(str(maxval))
    for row_idx in range(height):
        row_start = row_idx * width
        row_pixels = pixels[row_start : row_start + width]
        row_str = " ".join(str(p) for p in row_pixels)
        lines.append(row_str)

    out_path.write_text("\n".join(lines) + "\n", encoding="ascii")


def pixel_count(file_path: str | Path) -> int:
    """Return the total pixel count (width * height) of a PGM image."""
    img = parse_pgm_strict(file_path)
    return img.width * img.height


def average_gray(file_path: str | Path) -> float:
    """Return the average gray value of a PGM image."""
    img = parse_pgm_strict(file_path)
    if not img.pixels:
        return 0.0
    return sum(img.pixels) / len(img.pixels)


def count_above_threshold(file_path: str | Path, threshold: int) -> int:
    """Return the count of pixels with value strictly above the threshold."""
    img = parse_pgm_strict(file_path)
    return sum(1 for p in img.pixels if p > threshold)


def min_max_gray(file_path: str | Path) -> tuple[int, int]:
    """Return (min, max) gray values in a PGM image."""
    img = parse_pgm_strict(file_path)
    if not img.pixels:
        return (0, 0)
    return (min(img.pixels), max(img.pixels))


def flip_horizontal(file_path: str | Path, dest_path: str | Path) -> dict[str, Any]:
    """Flip a PGM image horizontally (mirror left-right) and write the result."""
    img = parse_pgm_strict(file_path)
    flipped: list[int] = []
    for row in range(img.height):
        row_start = row * img.width
        row_pixels = img.pixels[row_start:row_start + img.width]
        flipped.extend(reversed(row_pixels))
    write_pgm(flipped, img.width, img.height, img.maxval, dest_path)
    return {"ok": True, "width": img.width, "height": img.height, "pixel_count": len(flipped)}


def get_dimensions(file_path: str | Path) -> tuple[int, int]:
    """Return (width, height) of a PGM image without full pixel decode.

    Parses only the header. Useful for quick dimension checks.

    Args:
        file_path: Path to a P2 or P5 PGM file.

    Returns:
        Tuple (width, height).

    Raises:
        PgmError: If the file cannot be parsed or does not exist.
    """
    img = parse_pgm_strict(file_path)
    return (img.width, img.height)


def normalize(file_path: str | Path, dest_path: str | Path, new_maxval: int = 255) -> dict[str, Any]:
    """Normalize a PGM image to a new maxval range and write the result.

    Reads a PGM file, rescales all pixel values proportionally to
    [0, new_maxval], and writes the result as P2 ASCII to dest_path.

    Args:
        file_path: Source PGM file path.
        dest_path: Destination PGM file path.
        new_maxval: Target maximum value (default 255).

    Returns:
        Dict with keys: ok, width, height, old_maxval, new_maxval, pixel_count.

    Raises:
        PgmError: If the source file cannot be parsed.
        ValueError: If new_maxval is out of range.
    """
    if not (1 <= new_maxval <= MAX_MAXVAL):
        raise ValueError(f"new_maxval {new_maxval} must be in range 1-{MAX_MAXVAL}")
    img = parse_pgm_strict(file_path)
    old_maxval = img.maxval
    if old_maxval == new_maxval:
        normalized = list(img.pixels)
    else:
        normalized = [round(p * new_maxval / old_maxval) for p in img.pixels]
    write_pgm(normalized, img.width, img.height, new_maxval, dest_path)
    return {
        "ok": True,
        "width": img.width,
        "height": img.height,
        "old_maxval": old_maxval,
        "new_maxval": new_maxval,
        "pixel_count": len(normalized),
    }


def histogram(file_path: str | Path) -> dict[str, Any]:
    """Compute a pixel value histogram for a PGM image.

    Returns a dict mapping each pixel value (0..maxval) that appears
    to its count.

    Args:
        file_path: Path to a PGM file.

    Returns:
        Dict with keys: ok, width, height, maxval, histogram (dict[int,int]),
        unique_values (int).

    Raises:
        PgmError: If the file cannot be parsed.
    """
    img = parse_pgm_strict(file_path)
    hist: dict[int, int] = {}
    for p in img.pixels:
        hist[p] = hist.get(p, 0) + 1
    return {
        "ok": True,
        "width": img.width,
        "height": img.height,
        "maxval": img.maxval,
        "histogram": hist,
        "unique_values": len(hist),
    }


def threshold(file_path: str | Path, dest_path: str | Path,
              value: int) -> dict[str, Any]:
    """Apply a binary threshold to a PGM image, producing a PBM-like result.

    Pixels >= value become 1 (black), pixels < value become 0 (white).
    Output is written as a PGM with maxval=1.

    Args:
        file_path: Source PGM file path.
        dest_path: Destination PGM file path.
        value: Threshold value (0..maxval).

    Returns:
        Dict with keys: ok, width, height, threshold, above_count, below_count.

    Raises:
        PgmError: If the source file cannot be parsed.
    """
    img = parse_pgm_strict(file_path)
    above = 0
    below = 0
    result_pixels: list[int] = []
    for p in img.pixels:
        if p >= value:
            result_pixels.append(1)
            above += 1
        else:
            result_pixels.append(0)
            below += 1
    write_pgm(result_pixels, img.width, img.height, 1, dest_path)
    return {
        "ok": True,
        "width": img.width,
        "height": img.height,
        "threshold": value,
        "above_count": above,
        "below_count": below,
    }


def rotate_90(file_path: str | Path, dest_path: str | Path) -> dict[str, Any]:
    """Rotate a PGM image 90 degrees clockwise and write the result.

    The output image has width=original_height and height=original_width.
    Pixel at (row, col) in the original maps to (col, height-1-row) in the result.

    Args:
        file_path: Source PGM file path.
        dest_path: Destination PGM file path.

    Returns:
        Dict with keys: ok, width, height, pixel_count.

    Raises:
        PgmError: If source cannot be parsed.
    """
    img = parse_pgm_strict(file_path)
    new_w = img.height
    new_h = img.width
    rotated: list[int] = [0] * (new_w * new_h)
    for row in range(img.height):
        for col in range(img.width):
            src_idx = row * img.width + col
            dst_row = col
            dst_col = img.height - 1 - row
            dst_idx = dst_row * new_w + dst_col
            rotated[dst_idx] = img.pixels[src_idx]
    write_pgm(rotated, new_w, new_h, img.maxval, dest_path)
    return {"ok": True, "width": new_w, "height": new_h, "pixel_count": len(rotated)}


def grayscale_variance(file_path: str | Path) -> float:
    """Return the variance of pixel grayscale values in a PGM image.

    Computes population variance of all pixel values.

    Args:
        file_path: Path to a PGM file.

    Returns:
        Float variance. Returns 0.0 for empty images.
    """
    img = parse_pgm_strict(file_path)
    n = len(img.pixels)
    if n == 0:
        return 0.0
    mean = sum(img.pixels) / n
    return sum((p - mean) ** 2 for p in img.pixels) / n


def pgm_bright_pixel_ratio(file_path: str | Path, threshold: int = 128) -> float:
    """Return the fraction of pixels with value strictly above the threshold.

    Args:
        file_path: Path to a PGM file.
        threshold: Brightness threshold (default 128). Pixels > threshold are "bright".

    Returns:
        Float in [0.0, 1.0]. Returns 0.0 for empty images.

    Raises:
        PgmError: If the file cannot be parsed.
    """
    img = parse_pgm_strict(file_path)
    total = len(img.pixels)
    if total == 0:
        return 0.0
    bright = sum(1 for p in img.pixels if p > threshold)
    return bright / total


def pgm_dark_pixel_count(file_path: str | Path, threshold: int = 64) -> int:
    """Return the count of pixels with value at or below the threshold (dark pixels).

    Args:
        file_path: Path to a PGM file.
        threshold: Darkness threshold (default 64). Pixels <= threshold are "dark".

    Returns:
        Integer count of dark pixels. Returns 0 for empty images.

    Raises:
        PgmError: If the file cannot be parsed.
    """
    img = parse_pgm_strict(file_path)
    return sum(1 for p in img.pixels if p <= threshold)


def pgm_max_pixel_value(file_path: str | Path) -> int:
    """Return the maximum pixel value in a PGM image.

    Args:
        file_path: Path to a PGM file.

    Returns:
        Integer maximum pixel value in [0, maxval]. Returns 0 for empty images.

    Raises:
        PgmError: If the file cannot be parsed.
    """
    img = parse_pgm_strict(file_path)
    if not img.pixels:
        return 0
    return max(img.pixels)


def pgm_min_pixel_value(file_path: str | Path) -> int:
    """Return the minimum pixel value in a PGM image.

    Args:
        file_path: Path to a PGM file.

    Returns:
        Integer minimum pixel value in [0, maxval]. Returns 0 for empty images.

    Raises:
        PgmError: If the file cannot be parsed.
    """
    img = parse_pgm_strict(file_path)
    if not img.pixels:
        return 0
    return min(img.pixels)


def pgm_average_brightness(file_path: str | Path) -> float:
    """Return the average pixel brightness (mean gray value) of a PGM image.

    Args:
        file_path: Path to a PGM file.

    Returns:
        Float mean pixel value in [0.0, maxval]. Returns 0.0 for empty images.

    Raises:
        PgmError: If the file cannot be parsed.
    """
    img = parse_pgm_strict(file_path)
    if not img.pixels:
        return 0.0
    return sum(img.pixels) / len(img.pixels)


def pgm_contrast_range(file_path: str | Path) -> int:
    """Return the contrast range (dynamic range) of a PGM image.

    The contrast range is defined as ``max_gray - min_gray``, giving the span
    of gray values present in the image. A value of 0 means the image is
    perfectly uniform (all pixels the same shade).

    Args:
        file_path: Path to a PGM file.

    Returns:
        Integer contrast range in [0, maxval]. Returns 0 for empty images.

    Raises:
        PgmError: If the file cannot be parsed.
    """
    img = parse_pgm_strict(file_path)
    if not img.pixels:
        return 0
    return max(img.pixels) - min(img.pixels)


def pgm_median_pixel_value(file_path: str | Path) -> int:
    """Return the median pixel value of a PGM image.

    The median is the middle value when all pixels are sorted. For even-length
    pixel arrays, returns the lower of the two middle values (integer result).

    Args:
        file_path: Path to a PGM file.

    Returns:
        Integer median pixel value. Returns 0 for empty images.

    Raises:
        PgmError: If the file cannot be parsed.
    """
    img = parse_pgm_strict(file_path)
    if not img.pixels:
        return 0
    sorted_px = sorted(img.pixels)
    mid = len(sorted_px) // 2
    if len(sorted_px) % 2 == 1:
        return sorted_px[mid]
    return sorted_px[mid - 1]
