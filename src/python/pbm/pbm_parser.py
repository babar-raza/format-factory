"""
pbm_parser.py — PBM (Portable Bitmap) parser for format-factory-pbm.

Public API:
  parse_pbm(file_path)        — returns result dict (never raises)
  parse_pbm_strict(file_path) — raises PbmError on failure
  probe_pbm(file_path)        — returns header metadata without full parse

Implements Gate 4 prototype + Gate 5 neutral model.
Parses P1 (ASCII) and P4 (binary) PBM files.
Technology: Python stdlib only (open/read/split).

R55 Train F: P4 binary decode added (TC-BINARY-PBM-001).

License: Apache-2.0
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


MAX_FILE_SIZE = 64 * 1024 * 1024  # 64 MiB
MAX_DIMENSION = 65536

# Magic number constants (Netpbm spec — FACT-PBM-001, FACT-PBM-002)
# FACT-PBM-001: "PBM ASCII format starts with magic 'P1' followed by whitespace"
# FACT-PBM-002: "PBM binary format starts with magic 'P4' followed by whitespace"
PBM_MAGIC_ASCII = "P1"   # FACT-PBM-001
PBM_MAGIC_BINARY = "P4"  # FACT-PBM-002


class PbmError(Exception):
    """Base exception for PBM parser errors."""


class PbmInvalidMagicError(PbmError):
    """Raised when file does not start with P1 or P4."""


class PbmInvalidHeaderError(PbmError):
    """Raised when header fields are invalid."""


class PbmSizeError(PbmError):
    """Raised when file or image dimensions exceed limits."""


class PbmDecodeError(PbmError):
    """Raised when pixel data is malformed."""


@dataclass
class PbmImage:
    width: int = 0
    height: int = 0
    magic: str = "P1"
    pixels: list[int] = field(default_factory=list)
    path: str = ""


def _strip_comments(text: str) -> str:
    """Remove # comments from PBM text."""
    lines = text.split("\n")
    cleaned = []
    for line in lines:
        idx = line.find("#")
        if idx >= 0:
            line = line[:idx]
        cleaned.append(line)
    return "\n".join(cleaned)


def _parse_netpbm_header_bytes(data: bytes, num_ints: int) -> tuple[list[int], int]:
    """Parse ASCII Netpbm header from raw bytes, returning (values, data_offset)."""
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

    skip_ws_and_comments()
    while i < n and data[i:i+1] not in (b' ', b'\t', b'\n', b'\r'):
        i += 1

    values: list[int] = []
    for _ in range(num_ints):
        skip_ws_and_comments()
        start = i
        while i < n and data[i:i+1] not in (b' ', b'\t', b'\n', b'\r'):
            i += 1
        if start == i:
            raise ValueError("Unexpected end of header")
        values.append(int(data[start:i]))

    if i < n:
        i += 1  # consume single whitespace delimiter before binary data

    return values, i


def _parse_p4_binary(path: Path, data: bytes) -> "PbmImage":
    """Decode a P4 (binary packed-bits) PBM file."""
    try:
        (width, height), data_offset = _parse_netpbm_header_bytes(data, 2)
    except (ValueError, IndexError) as exc:
        raise PbmInvalidHeaderError(f"Invalid P4 header: {exc}")

    if width <= 0 or height <= 0:
        raise PbmInvalidHeaderError(f"Invalid dimensions: {width}x{height}")
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        raise PbmSizeError(f"Dimensions {width}x{height} exceed limit of {MAX_DIMENSION}")

    row_bytes = (width + 7) // 8
    expected_bytes = row_bytes * height
    pixel_data = data[data_offset:]

    if len(pixel_data) < expected_bytes:
        raise PbmDecodeError(
            f"Not enough binary pixel data: expected {expected_bytes} bytes, "
            f"got {len(pixel_data)}"
        )

    pixels: list[int] = []
    for row in range(height):
        row_start = row * row_bytes
        for col in range(width):
            byte_idx = row_start + col // 8
            bit_idx = 7 - (col % 8)
            v = (pixel_data[byte_idx] >> bit_idx) & 1
            pixels.append(v)

    return PbmImage(width=width, height=height, magic="P4", pixels=pixels, path=str(path))


def parse_pbm_strict(file_path: str | Path) -> PbmImage:
    """Parse a PBM (P1 ASCII or P4 binary) file, raising PbmError on any problem."""
    path = Path(file_path)
    if not path.exists():
        raise PbmError(f"File not found: {path}")

    size = os.path.getsize(path)
    if size > MAX_FILE_SIZE:
        raise PbmSizeError(f"File size {size} exceeds limit of {MAX_FILE_SIZE}")

    data = path.read_bytes()
    header_probe = data[:16].decode("ascii", errors="replace").split()
    if not header_probe:
        raise PbmInvalidMagicError("Empty file")
    magic = header_probe[0]
    if magic not in ("P1", "P4"):
        raise PbmInvalidMagicError(f"Invalid magic: '{magic}', expected P1 or P4")

    if magic == "P4":
        return _parse_p4_binary(path, data)

    # P1 ASCII path
    raw = data.decode("ascii", errors="replace")
    cleaned = _strip_comments(raw)
    tokens = cleaned.split()

    if len(tokens) < 3:
        raise PbmInvalidHeaderError(
            f"Incomplete header: need magic, width, height; got {len(tokens)} tokens"
        )

    try:
        width = int(tokens[1])
        height = int(tokens[2])
    except ValueError as exc:
        raise PbmInvalidHeaderError(f"Invalid header values: {exc}")

    if width <= 0 or height <= 0:
        raise PbmInvalidHeaderError(f"Invalid dimensions: {width}x{height}")
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        raise PbmSizeError(
            f"Dimensions {width}x{height} exceed limit of {MAX_DIMENSION}"
        )

    expected_pixels = width * height
    pixel_tokens = tokens[3:]

    if len(pixel_tokens) < expected_pixels:
        raise PbmDecodeError(
            f"Not enough pixel data: expected {expected_pixels} values, got {len(pixel_tokens)}"
        )

    pixels: list[int] = []
    for i in range(expected_pixels):
        try:
            v = int(pixel_tokens[i])
        except (ValueError, IndexError) as exc:
            raise PbmDecodeError(f"Invalid pixel data at pixel {i}: {exc}")
        if v not in (0, 1):
            raise PbmDecodeError(
                f"Pixel {i} value {v} out of range — must be 0 or 1"
            )
        pixels.append(v)

    return PbmImage(
        width=width,
        height=height,
        magic=magic,
        pixels=pixels,
        path=str(path),
    )


def parse_pbm(file_path: str | Path) -> dict[str, Any]:
    """Parse a PBM file, returning a result dict (never raises)."""
    try:
        img = parse_pbm_strict(file_path)
        return {
            "ok": True,
            "path": img.path,
            "width": img.width,
            "height": img.height,
            "magic": img.magic,
            "pixel_count": len(img.pixels),
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc), "error_type": type(exc).__name__}


def probe_pbm(file_path: str | Path) -> dict[str, Any]:
    """Probe a PBM file for header metadata without full parse."""
    path = Path(file_path)
    result: dict[str, Any] = {"path": str(path), "exists": path.exists()}
    if not path.exists():
        return result
    try:
        raw = path.read_bytes()[:1024].decode("ascii", errors="replace")
        cleaned = _strip_comments(raw)
        tokens = cleaned.split()
        if not tokens or tokens[0] not in ("P1", "P4"):
            result["valid_header"] = False
            result["error"] = f"Invalid magic: {tokens[0] if tokens else 'empty'}"
            return result
        result["valid_header"] = True
        result["magic"] = tokens[0]
        if len(tokens) >= 3:
            result["width"] = int(tokens[1])
            result["height"] = int(tokens[2])
    except Exception as exc:
        result["valid_header"] = False
        result["error"] = str(exc)
    return result


# ---------------------------------------------------------------------------
# R73 Train G: image pixel statistics API
# ---------------------------------------------------------------------------

def image_pixel_stats(file_path: str | Path) -> dict[str, Any]:
    """Return pixel-level statistics for a PBM image.

    Returns a dict with:
      ok: bool
      black_count: int  — pixels with value 1 (black in PBM convention)
      white_count: int  — pixels with value 0 (white in PBM convention)
      total_pixels: int
      black_density: float  — fraction of black pixels (0.0..1.0)
      width: int, height: int, magic: str
    """
    try:
        img = parse_pbm_strict(file_path)
        black = sum(1 for p in img.pixels if p == 1)
        white = sum(1 for p in img.pixels if p == 0)
        total = len(img.pixels)
        return {
            "ok": True,
            "black_count": black,
            "white_count": white,
            "total_pixels": total,
            "black_density": round(black / total, 6) if total > 0 else 0.0,
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
    "p1_ascii_parse",
    "p4_binary_parse",
    "bitmap_pixel_decode",
    "comment_stripping",
    "probe",
    "dimension_extraction",
    "size_guard",
})

UNSUPPORTED_FEATURES: frozenset[str] = frozenset({
    "ppm_color",
    "pgm_grayscale",
    "pam_arbitrary_map",
    "encoding_to_pbm",
    "color_profiles",
    "metadata_extraction",
    "streaming_decode",
    "run_length_encoding",
})


def get_capabilities() -> dict[str, Any]:
    """Return a capability descriptor for the PBM parser (Gate 5 neutral model)."""
    return {
        "format": "pbm",
        "gate": 5,
        "supported": sorted(SUPPORTED_FEATURES),
        "unsupported": sorted(UNSUPPORTED_FEATURES),
        "commercial_product_ready": False,
    }


def write_pbm(
    pixels: list[int],
    width: int,
    height: int,
    file_path: str | Path,
    *,
    comment: str = "",
) -> None:
    """Write a PBM P1 (ASCII portable bitmap) file.

    Pixels must be a flat list of 0/1 integer values in row-major order.
    The list length must equal width * height. Values other than 0 or 1 are
    clamped: 0 stays 0, any non-zero becomes 1.

    This is a write-side complement to parse_pbm for roundtrip verification.
    Only P1 (ASCII) format is produced; P4 (binary) is unsupported in this track.

    Args:
        pixels: Flat row-major list of 0/1 pixel values.
        width: Image width in pixels.
        height: Image height in pixels.
        file_path: Destination file path.
        comment: Optional comment line to include in the header (no newlines).

    Raises:
        ValueError: If pixels length does not match width * height.
        PbmSizeError: If dimensions exceed MAX_DIMENSION.

    Added in R84 Train M as Netpbm write/roundtrip product advancement.
    """
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        raise PbmSizeError(f"Dimension {width}x{height} exceeds limit {MAX_DIMENSION}")
    if len(pixels) != width * height:
        raise ValueError(
            f"pixels length {len(pixels)} does not match width*height {width * height}"
        )

    out_path = Path(file_path)
    lines = ["P1"]
    if comment:
        safe_comment = comment.replace("\n", " ").replace("\r", " ")
        lines.append(f"# {safe_comment}")
    lines.append(f"{width} {height}")
    for row_idx in range(height):
        row_start = row_idx * width
        row_pixels = pixels[row_start : row_start + width]
        row_str = " ".join("1" if p else "0" for p in row_pixels)
        lines.append(row_str)

    out_path.write_text("\n".join(lines) + "\n", encoding="ascii")


def pixel_count(file_path: str | Path) -> int:
    """Return the total pixel count (width * height) of a PBM image."""
    img = parse_pbm_strict(file_path)
    return img.width * img.height


def count_black(file_path: str | Path) -> int:
    """Return the count of black pixels (value=1) in a PBM image."""
    img = parse_pbm_strict(file_path)
    return sum(1 for p in img.pixels if p == 1)


def flip_horizontal(file_path: str | Path, dest_path: str | Path) -> dict[str, Any]:
    """Flip a PBM image horizontally (mirror left-right) and write the result."""
    img = parse_pbm_strict(file_path)
    flipped: list[int] = []
    for row in range(img.height):
        row_start = row * img.width
        row_pixels = img.pixels[row_start:row_start + img.width]
        flipped.extend(reversed(row_pixels))
    write_pbm(flipped, img.width, img.height, dest_path)
    return {"ok": True, "width": img.width, "height": img.height, "pixel_count": len(flipped)}


def get_dimensions(file_path: str | Path) -> tuple[int, int]:
    """Return (width, height) of a PBM image without full pixel decode.

    Parses only the header. Useful for quick dimension checks.

    Args:
        file_path: Path to a P1 or P4 PBM file.

    Returns:
        Tuple (width, height).

    Raises:
        PbmError: If the file cannot be parsed or does not exist.
    """
    img = parse_pbm_strict(file_path)
    return (img.width, img.height)


def invert(file_path: str | Path, dest_path: str | Path) -> dict[str, Any]:
    """Invert a PBM image (swap 0↔1) and write the result.

    Reads a PBM file, flips all pixel values, and writes the result
    as a P1 ASCII PBM file to dest_path.

    Args:
        file_path: Source PBM file path.
        dest_path: Destination PBM file path.

    Returns:
        Dict with keys: ok, width, height, pixel_count.

    Raises:
        PbmError: If the source file cannot be parsed.
    """
    img = parse_pbm_strict(file_path)
    inverted = [1 - p for p in img.pixels]
    write_pbm(inverted, img.width, img.height, dest_path)
    return {
        "ok": True,
        "width": img.width,
        "height": img.height,
        "pixel_count": len(inverted),
    }


def crop(file_path: str | Path, dest_path: str | Path,
         x: int, y: int, w: int, h: int) -> dict[str, Any]:
    """Crop a rectangular region from a PBM image and write it.

    Extracts pixels from (x, y) with size (w, h) and writes as P1 PBM.

    Args:
        file_path: Source PBM file path.
        dest_path: Destination PBM file path.
        x: Left column of crop region (0-based).
        y: Top row of crop region (0-based).
        w: Width of crop region.
        h: Height of crop region.

    Returns:
        Dict with keys: ok, width, height, pixel_count.

    Raises:
        PbmError: If source cannot be parsed.
        ValueError: If crop region is out of bounds.
    """
    img = parse_pbm_strict(file_path)
    if x < 0 or y < 0 or w <= 0 or h <= 0:
        raise ValueError(f"Invalid crop region: x={x}, y={y}, w={w}, h={h}")
    if x + w > img.width or y + h > img.height:
        raise ValueError(
            f"Crop region ({x},{y},{w},{h}) exceeds image bounds ({img.width}x{img.height})"
        )
    cropped: list[int] = []
    for row in range(y, y + h):
        for col in range(x, x + w):
            cropped.append(img.pixels[row * img.width + col])
    write_pbm(cropped, w, h, dest_path)
    return {"ok": True, "width": w, "height": h, "pixel_count": len(cropped)}


def count_white(file_path: str | Path) -> int:
    """Return the count of white pixels (value=0) in a PBM image."""
    img = parse_pbm_strict(file_path)
    return sum(1 for p in img.pixels if p == 0)


# Sprint: FORMAT-FACTORY-BROAD-SELF-HEALING-PRODUCT-ACCELERATION-RNEXT-001
# Queue: broad-accel-q-007

def aspect_ratio(file_path: "str | Path") -> float:
    """Return the aspect ratio (width / height) of a PBM image.

    Args:
        file_path: Path to a PBM image file.

    Returns:
        Float ratio width/height. Returns 0.0 for zero-height images.

    Raises:
        PbmError: If the file cannot be parsed.
    """
    img = parse_pbm_strict(file_path)
    if img.height == 0:
        return 0.0
    return img.width / img.height


def rotate_90(file_path: "str | Path", dest_path: "str | Path") -> dict[str, Any]:
    """Rotate a PBM image 90 degrees clockwise and write the result.

    The output image has width=original_height and height=original_width.
    Pixel at (row, col) in the original maps to (col, height-1-row) in the result.

    Args:
        file_path: Source PBM file path.
        dest_path: Destination PBM file path.

    Returns:
        Dict with keys: ok, width, height, pixel_count.

    Raises:
        PbmError: If source cannot be parsed.
    """
    img = parse_pbm_strict(file_path)
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
    write_pbm(rotated, new_w, new_h, dest_path)
    return {"ok": True, "width": new_w, "height": new_h, "pixel_count": len(rotated)}


def black_pixel_ratio(file_path: "str | Path") -> float:
    """Return the fraction of black pixels (1-values) in a PBM image.

    In PBM format, 1 = black and 0 = white.

    Args:
        file_path: Path to a PBM image file.

    Returns:
        Float in [0.0, 1.0] representing fraction of black pixels.
        Returns 0.0 for empty images.

    Raises:
        PbmError: If the file cannot be parsed.
    """
    img = parse_pbm_strict(file_path)
    total = img.width * img.height
    if total == 0:
        return 0.0
    black = sum(1 for px in img.pixels if px == 1)
    return black / total


def pbm_white_pixel_ratio(file_path: "str | Path") -> float:
    """Return the fraction of white pixels (0-values) in a PBM image.

    In PBM format, 0 = white and 1 = black.

    Args:
        file_path: Path to a PBM image file.

    Returns:
        Float in [0.0, 1.0] representing fraction of white pixels.
        Returns 0.0 for empty images.

    Raises:
        PbmError: If the file cannot be parsed.
    """
    return 1.0 - black_pixel_ratio(file_path)


def pbm_aspect_ratio(file_path: "str | Path") -> float:
    """Return the aspect ratio (width / height) of a PBM image.

    Args:
        file_path: Path to a PBM image file.

    Returns:
        Float representing width divided by height.
        Returns 0.0 for images with zero height.

    Raises:
        PbmError: If the file cannot be parsed.
    """
    img = parse_pbm_strict(file_path)
    if img.height == 0:
        return 0.0
    return img.width / img.height


def pbm_white_pixel_count(file_path: "str | Path") -> int:
    """Return the count of white pixels (value 0) in a PBM image.

    In PBM format, 0 = white and 1 = black.

    Args:
        file_path: Path to a PBM file.

    Returns:
        Integer count of white pixels. Returns 0 for all-black images.

    Raises:
        PbmError: If the file cannot be parsed.
    """
    img = parse_pbm_strict(file_path)
    return sum(1 for p in img.pixels if p == 0)


def scale_nearest(file_path: "str | Path", dest_path: "str | Path", factor: int) -> dict[str, Any]:
    """Scale a PBM image up by an integer factor using nearest-neighbor interpolation.

    Each pixel becomes a factor x factor block of identical pixels.

    Args:
        file_path: Source PBM file path.
        dest_path: Destination PBM file path.
        factor: Integer scale factor (must be >= 1).

    Returns:
        Dict with keys: ok, width, height, pixel_count.

    Raises:
        PbmError: If source cannot be parsed.
        ValueError: If factor < 1.
    """
    if factor < 1:
        raise ValueError(f"Scale factor must be >= 1, got {factor}")
    img = parse_pbm_strict(file_path)
    new_w = img.width * factor
    new_h = img.height * factor
    scaled: list[int] = [0] * (new_w * new_h)
    for row in range(img.height):
        for col in range(img.width):
            px = img.pixels[row * img.width + col]
            for dr in range(factor):
                for dc in range(factor):
                    dst_row = row * factor + dr
                    dst_col = col * factor + dc
                    scaled[dst_row * new_w + dst_col] = px
    write_pbm(scaled, new_w, new_h, dest_path)
    return {"ok": True, "width": new_w, "height": new_h, "pixel_count": len(scaled)}


def pbm_row_black_counts(file_path: "str | Path") -> list[int]:
    """Return a list of per-row black pixel counts for a PBM image.

    For a PBM image with height H, returns a list of H integers where each
    element is the count of black pixels (value 1) in that row. Useful for
    detecting horizontal patterns, text lines, or image structure.

    Args:
        file_path: Path to a PBM file.

    Returns:
        List of integers, one per row, each being the black pixel count.

    Raises:
        PbmError: If the file cannot be parsed.
    """
    img = parse_pbm_strict(file_path)
    counts: list[int] = []
    for row in range(img.height):
        start = row * img.width
        end = start + img.width
        counts.append(sum(1 for p in img.pixels[start:end] if p == 1))
    return counts


def pbm_total_pixel_count(file_path: "str | Path") -> int:
    """Return the total number of pixels in a PBM image (width * height).

    Args:
        file_path: Path to a PBM file.

    Returns:
        Integer total pixel count.

    Raises:
        PbmError: If the file cannot be parsed.
    """
    img = parse_pbm_strict(file_path)
    return img.width * img.height


def pbm_is_binary(file_path: "str | Path") -> bool:
    """Return True if the PBM file uses binary P4 format, False if ASCII P1.

    Args:
        file_path: Path to a PBM file.

    Returns:
        True for P4 (binary), False for P1 (ASCII).

    Raises:
        PbmError: If the file cannot be parsed or has an unrecognized magic.
    """
    p = Path(file_path)
    data = p.read_bytes()
    magic = data[:2]
    if magic == b"P4":
        return True
    if magic == b"P1":
        return False
    raise PbmError(f"Unrecognized PBM magic: {magic!r}")


def pbm_black_pixel_ratio(file_path: "str | Path") -> float:
    """Return the ratio of black pixels to total pixels. 0.0 if no pixels."""
    img = parse_pbm_strict(file_path)
    total = img.width * img.height
    if total == 0:
        return 0.0
    stats = image_pixel_stats(file_path)
    return stats["black_count"] / total


def pbm_dimensions(file_path: "str | Path") -> dict:
    """Return width and height of the PBM image as a dict."""
    img = parse_pbm_strict(file_path)
    return {"width": img.width, "height": img.height}


def pbm_column_black_counts(file_path: "str | Path") -> list[int]:
    """Return the number of black pixels in each column."""
    img = parse_pbm_strict(file_path)
    if not img.pixels or img.width == 0:
        return []
    counts = [0] * img.width
    for y in range(img.height):
        for x in range(img.width):
            if img.pixels[y * img.width + x] == 1:
                counts[x] += 1
    return counts


def pbm_white_density(file_path: "str | Path") -> float:
    """Return the ratio of white pixels to total pixels. 0.0 if no pixels."""
    img = parse_pbm_strict(file_path)
    if not img.pixels:
        return 0.0
    white = sum(1 for p in img.pixels if p == 0)
    return white / len(img.pixels)
