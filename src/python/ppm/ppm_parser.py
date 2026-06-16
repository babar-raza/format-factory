"""
ppm_parser.py — PPM (Portable Pixmap) parser for format-factory-ppm.

Public API:
  parse_ppm(file_path)        — returns result dict (never raises)
  parse_ppm_strict(file_path) — raises PpmError on failure
  probe_ppm(file_path)        — returns header metadata without full parse

Implements Gate 4 prototype + Gate 5 neutral model.
Parses P3 (ASCII) and P6 (binary) PPM files.
Technology: Python stdlib only (open/read/split).

R55 Train F: P6 binary decode added (TC-BINARY-PPM-001).

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

# Magic number constants (Netpbm spec — FACT-PPM-001, FACT-PPM-002)
# FACT-PPM-001: "PPM ASCII format starts with magic 'P3' followed by whitespace"
# FACT-PPM-002: "PPM binary format starts with magic 'P6' followed by whitespace"
PPM_MAGIC_ASCII = "P3"   # FACT-PPM-001
PPM_MAGIC_BINARY = "P6"  # FACT-PPM-002


class PpmError(Exception):
    """Base exception for PPM parser errors."""


class PpmInvalidMagicError(PpmError):
    """Raised when file does not start with P3 or P6."""


class PpmInvalidHeaderError(PpmError):
    """Raised when header fields are invalid."""


class PpmSizeError(PpmError):
    """Raised when file or image dimensions exceed limits."""


class PpmDecodeError(PpmError):
    """Raised when pixel data is malformed."""


@dataclass
class PpmImage:
    width: int = 0
    height: int = 0
    maxval: int = 255
    magic: str = "P3"
    pixels: list[tuple[int, int, int]] = field(default_factory=list)
    path: str = ""


def _strip_comments(text: str) -> str:
    """Remove # comments from PPM text."""
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


def _parse_p6_binary(path: Path, data: bytes) -> "PpmImage":
    """Decode a P6 (binary) PPM file."""
    try:
        (width, height, maxval), data_offset = _parse_netpbm_header_bytes(data, 3)
    except (ValueError, IndexError) as exc:
        raise PpmInvalidHeaderError(f"Invalid P6 header: {exc}")

    if width <= 0 or height <= 0:
        raise PpmInvalidHeaderError(f"Invalid dimensions: {width}x{height}")
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        raise PpmSizeError(f"Dimensions {width}x{height} exceed limit of {MAX_DIMENSION}")
    if maxval <= 0 or maxval > MAX_MAXVAL:
        raise PpmInvalidHeaderError(f"Invalid maxval: {maxval}")

    bytes_per_sample = 2 if maxval > 255 else 1
    expected_pixels = width * height
    expected_bytes = expected_pixels * 3 * bytes_per_sample
    pixel_data = data[data_offset:]

    if len(pixel_data) < expected_bytes:
        raise PpmDecodeError(
            f"Not enough binary pixel data: expected {expected_bytes} bytes, "
            f"got {len(pixel_data)}"
        )

    pixels: list[tuple[int, int, int]] = []
    if bytes_per_sample == 1:
        for i in range(expected_pixels):
            base = i * 3
            r, g, b = pixel_data[base], pixel_data[base + 1], pixel_data[base + 2]
            if r > maxval or g > maxval or b > maxval:
                raise PpmDecodeError(
                    f"Pixel {i} value ({r},{g},{b}) out of range [0,{maxval}]"
                )
            pixels.append((r, g, b))
    else:
        for i in range(expected_pixels):
            base = i * 6
            r = (pixel_data[base] << 8) | pixel_data[base + 1]
            g = (pixel_data[base + 2] << 8) | pixel_data[base + 3]
            b = (pixel_data[base + 4] << 8) | pixel_data[base + 5]
            if r > maxval or g > maxval or b > maxval:
                raise PpmDecodeError(
                    f"Pixel {i} value ({r},{g},{b}) out of range [0,{maxval}]"
                )
            pixels.append((r, g, b))

    return PpmImage(
        width=width, height=height, maxval=maxval,
        magic="P6", pixels=pixels, path=str(path),
    )


def parse_ppm_strict(file_path: str | Path) -> PpmImage:
    """Parse a PPM (P3 ASCII or P6 binary) file, raising PpmError on any problem."""
    path = Path(file_path)
    if not path.exists():
        raise PpmError(f"File not found: {path}")

    size = os.path.getsize(path)
    if size > MAX_FILE_SIZE:
        raise PpmSizeError(f"File size {size} exceeds limit of {MAX_FILE_SIZE}")

    data = path.read_bytes()
    header_probe = data[:16].decode("ascii", errors="replace").split()
    if not header_probe:
        raise PpmInvalidMagicError("Empty file")
    magic = header_probe[0]
    if magic not in ("P3", "P6"):
        raise PpmInvalidMagicError(f"Invalid magic: '{magic}', expected P3 or P6")

    if magic == "P6":
        return _parse_p6_binary(path, data)

    # P3 ASCII path
    raw = data.decode("ascii", errors="replace")
    cleaned = _strip_comments(raw)
    tokens = cleaned.split()

    if len(tokens) < 4:
        raise PpmInvalidHeaderError(
            f"Incomplete header: need magic, width, height, maxval; got {len(tokens)} tokens"
        )

    try:
        width = int(tokens[1])
        height = int(tokens[2])
        maxval = int(tokens[3])
    except ValueError as exc:
        raise PpmInvalidHeaderError(f"Invalid header values: {exc}")

    if width <= 0 or height <= 0:
        raise PpmInvalidHeaderError(f"Invalid dimensions: {width}x{height}")
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        raise PpmSizeError(
            f"Dimensions {width}x{height} exceed limit of {MAX_DIMENSION}"
        )
    if maxval <= 0 or maxval > MAX_MAXVAL:
        raise PpmInvalidHeaderError(f"Invalid maxval: {maxval}")

    expected_pixels = width * height
    pixel_tokens = tokens[4:]
    expected_values = expected_pixels * 3

    if len(pixel_tokens) < expected_values:
        raise PpmDecodeError(
            f"Not enough pixel data: expected {expected_values} values, got {len(pixel_tokens)}"
        )

    pixels: list[tuple[int, int, int]] = []
    for i in range(expected_pixels):
        base = i * 3
        try:
            r = int(pixel_tokens[base])
            g = int(pixel_tokens[base + 1])
            b = int(pixel_tokens[base + 2])
        except (ValueError, IndexError) as exc:
            raise PpmDecodeError(f"Invalid pixel data at pixel {i}: {exc}")
        if r < 0 or g < 0 or b < 0 or r > maxval or g > maxval or b > maxval:
            raise PpmDecodeError(
                f"Pixel {i} value ({r},{g},{b}) out of range [0,{maxval}]"
            )
        pixels.append((r, g, b))

    return PpmImage(
        width=width,
        height=height,
        maxval=maxval,
        magic=magic,
        pixels=pixels,
        path=str(path),
    )


def parse_ppm(file_path: str | Path) -> dict[str, Any]:
    """Parse a PPM file, returning a result dict (never raises)."""
    try:
        img = parse_ppm_strict(file_path)
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


def probe_ppm(file_path: str | Path) -> dict[str, Any]:
    """Probe a PPM file for header metadata without full parse."""
    path = Path(file_path)
    result: dict[str, Any] = {"path": str(path), "exists": path.exists()}
    if not path.exists():
        return result
    try:
        raw = path.read_bytes()[:1024].decode("ascii", errors="replace")
        cleaned = _strip_comments(raw)
        tokens = cleaned.split()
        if not tokens or tokens[0] not in ("P3", "P6"):
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
# Gate 5 — Neutral model: capability declaration
# ---------------------------------------------------------------------------

SUPPORTED_FEATURES: frozenset[str] = frozenset({
    "p3_ascii_parse",
    "p6_binary_parse",
    "rgb_pixel_decode",
    "comment_stripping",
    "probe",
    "dimension_extraction",
    "maxval_validation",
    "size_guard",
})

UNSUPPORTED_FEATURES: frozenset[str] = frozenset({
    "pgm_grayscale",
    "pbm_bitmap",
    "pam_arbitrary_map",
    "16bit_values",
    "color_profiles",
    "metadata_extraction",
    "streaming_decode",
})


def get_capabilities() -> dict[str, Any]:
    """Return a capability descriptor for the PPM parser (Gate 5 neutral model)."""
    return {
        "format": "ppm",
        "gate": 5,
        "supported": sorted(SUPPORTED_FEATURES),
        "unsupported": sorted(UNSUPPORTED_FEATURES),
        "commercial_product_ready": False,
    }


# ---------------------------------------------------------------------------
# write_ppm — PPM P3 ASCII writer (R86 Train K)
# ---------------------------------------------------------------------------

def write_ppm(
    pixels: list[tuple[int, int, int]],
    width: int,
    height: int,
    maxval: int,
    file_path: str | Path,
    *,
    comment: str = "",
) -> None:
    """Write a PPM P3 (ASCII portable pixmap) file.

    Pixels must be a flat list of (R, G, B) tuples in row-major order.
    The list length must equal width * height.
    Each channel value must be in range [0, maxval].

    Args:
        pixels: Flat row-major list of (R, G, B) tuples.
        width: Image width in pixels.
        height: Image height in pixels.
        maxval: Maximum channel value (1-65535).
        file_path: Destination file path.
        comment: Optional comment line to include in the header.

    Raises:
        ValueError: If pixel count mismatch, maxval out of range, or bad tuple.
        PpmSizeError: If dimensions exceed MAX_DIMENSION.

    Added in R86 Train K as Netpbm write/roundtrip product advancement.
    """
    if width < 1 or height < 1:
        raise ValueError(f"Dimensions must be positive: got {width}x{height}")
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        raise PpmSizeError(f"Dimension {width}x{height} exceeds limit {MAX_DIMENSION}")
    if not (1 <= maxval <= MAX_MAXVAL):
        raise ValueError(f"maxval {maxval} must be in range 1-{MAX_MAXVAL}")
    if len(pixels) != width * height:
        raise ValueError(
            f"pixels length {len(pixels)} does not match width*height {width * height}"
        )

    # Validate pixel channel values are within [0, maxval]
    for i, (r, g, b) in enumerate(pixels):
        if r < 0 or r > maxval or g < 0 or g > maxval or b < 0 or b > maxval:
            raise ValueError(
                f"Pixel {i} channel value out of range [0, {maxval}]: ({r}, {g}, {b})"
            )

    out_path = Path(file_path)
    lines = ["P3"]
    if comment:
        safe_comment = comment.replace("\n", " ").replace("\r", " ")
        lines.append(f"# {safe_comment}")
    lines.append(f"{width} {height}")
    lines.append(str(maxval))
    for row_idx in range(height):
        row_start = row_idx * width
        row_pixels = pixels[row_start : row_start + width]
        row_str = " ".join(f"{r} {g} {b}" for r, g, b in row_pixels)
        lines.append(row_str)

    out_path.write_text("\n".join(lines) + "\n", encoding="ascii")


def get_dimensions(file_path: str | Path) -> tuple[int, int]:
    """Return (width, height) of a PPM image without full pixel decode.

    Parses only the header. Useful for quick dimension checks.

    Args:
        file_path: Path to a P3 or P6 PPM file.

    Returns:
        Tuple (width, height).

    Raises:
        PpmError: If the file cannot be parsed or does not exist.
    """
    img = parse_ppm_strict(file_path)
    return (img.width, img.height)


def to_grayscale(file_path: str | Path, dest_path: str | Path) -> dict[str, Any]:
    """Convert a PPM color image to a PGM grayscale image.

    Uses luminance formula: gray = round(0.299*R + 0.587*G + 0.114*B).
    Writes a P2 ASCII PGM file to dest_path.

    Args:
        file_path: Source PPM file path.
        dest_path: Destination PGM file path.

    Returns:
        Dict with keys: ok, width, height, maxval, pixel_count.

    Raises:
        PpmError: If the source file cannot be parsed.
    """
    img = parse_ppm_strict(file_path)
    gray_pixels: list[int] = []
    for r, g, b in img.pixels:
        gray = round(0.299 * r + 0.587 * g + 0.114 * b)
        gray = min(gray, img.maxval)
        gray_pixels.append(gray)

    # Write as PGM
    out_path = Path(dest_path)
    lines = ["P2"]
    lines.append(f"{img.width} {img.height}")
    lines.append(str(img.maxval))
    for row_idx in range(img.height):
        row_start = row_idx * img.width
        row_pixels = gray_pixels[row_start: row_start + img.width]
        lines.append(" ".join(str(p) for p in row_pixels))
    out_path.write_text("\n".join(lines) + "\n", encoding="ascii")

    return {
        "ok": True,
        "width": img.width,
        "height": img.height,
        "maxval": img.maxval,
        "pixel_count": len(gray_pixels),
    }


def pixel_count(file_path: str | Path) -> int:
    """Return the total pixel count (width * height) of a PPM image."""
    img = parse_ppm_strict(file_path)
    return img.width * img.height


def average_color(file_path: str | Path) -> tuple[float, float, float]:
    """Return the average (R, G, B) color of a PPM image as floats."""
    img = parse_ppm_strict(file_path)
    if not img.pixels:
        return (0.0, 0.0, 0.0)
    n = len(img.pixels)
    r_sum = sum(p[0] for p in img.pixels)
    g_sum = sum(p[1] for p in img.pixels)
    b_sum = sum(p[2] for p in img.pixels)
    return (r_sum / n, g_sum / n, b_sum / n)


def brightness(file_path: str | Path, dest_path: str | Path,
               delta: int) -> dict[str, Any]:
    """Adjust brightness of a PPM image by adding delta to all channels.

    Values are clamped to [0, maxval].

    Args:
        file_path: Source PPM file path.
        dest_path: Destination PPM file path.
        delta: Brightness adjustment (-maxval to +maxval).

    Returns:
        Dict with keys: ok, width, height, delta, clamped_count.

    Raises:
        PpmError: If the source file cannot be parsed.
    """
    img = parse_ppm_strict(file_path)
    adjusted: list[tuple[int, int, int]] = []
    clamped = 0
    for r, g, b in img.pixels:
        nr = r + delta
        ng = g + delta
        nb = b + delta
        if nr < 0 or nr > img.maxval or ng < 0 or ng > img.maxval or nb < 0 or nb > img.maxval:
            clamped += 1
        nr = max(0, min(img.maxval, nr))
        ng = max(0, min(img.maxval, ng))
        nb = max(0, min(img.maxval, nb))
        adjusted.append((nr, ng, nb))
    write_ppm(adjusted, img.width, img.height, img.maxval, dest_path)
    return {
        "ok": True,
        "width": img.width,
        "height": img.height,
        "delta": delta,
        "clamped_count": clamped,
    }


def crop(file_path: str | Path, dest_path: str | Path,
         x: int, y: int, w: int, h: int) -> dict[str, Any]:
    """Crop a rectangular region from a PPM image and write it.

    Args:
        file_path: Source PPM file path.
        dest_path: Destination PPM file path.
        x: Left column of crop region (0-based).
        y: Top row of crop region (0-based).
        w: Width of crop region.
        h: Height of crop region.

    Returns:
        Dict with keys: ok, width, height, pixel_count.

    Raises:
        PpmError: If source cannot be parsed.
        ValueError: If crop region is out of bounds.
    """
    img = parse_ppm_strict(file_path)
    if x < 0 or y < 0 or w <= 0 or h <= 0:
        raise ValueError(f"Invalid crop region: x={x}, y={y}, w={w}, h={h}")
    if x + w > img.width or y + h > img.height:
        raise ValueError(
            f"Crop region ({x},{y},{w},{h}) exceeds image bounds ({img.width}x{img.height})"
        )
    cropped: list[tuple[int, int, int]] = []
    for row in range(y, y + h):
        for col in range(x, x + w):
            cropped.append(img.pixels[row * img.width + col])
    write_ppm(cropped, w, h, img.maxval, dest_path)
    return {"ok": True, "width": w, "height": h, "pixel_count": len(cropped)}


def flip_horizontal(file_path: str | Path, dest_path: str | Path) -> dict[str, Any]:
    """Flip a PPM image horizontally (mirror left-right) and write the result."""
    img = parse_ppm_strict(file_path)
    flipped: list[tuple[int, int, int]] = []
    for row in range(img.height):
        row_start = row * img.width
        row_pixels = img.pixels[row_start:row_start + img.width]
        flipped.extend(reversed(row_pixels))
    write_ppm(flipped, img.width, img.height, img.maxval, dest_path)
    return {"ok": True, "width": img.width, "height": img.height, "pixel_count": len(flipped)}


def invert(file_path: str | Path, dest_path: str | Path) -> dict[str, Any]:
    """Invert all pixel colors in a PPM image and write the result."""
    img = parse_ppm_strict(file_path)
    inverted = [(img.maxval - r, img.maxval - g, img.maxval - b) for r, g, b in img.pixels]
    write_ppm(inverted, img.width, img.height, img.maxval, dest_path)
    return {"ok": True, "width": img.width, "height": img.height, "pixel_count": len(inverted)}


def flip_vertical(file_path: str | Path, dest_path: str | Path) -> dict[str, Any]:
    """Flip a PPM image vertically (mirror top-bottom) and write the result."""
    img = parse_ppm_strict(file_path)
    flipped: list[tuple[int, int, int]] = []
    for row in range(img.height - 1, -1, -1):
        row_start = row * img.width
        flipped.extend(img.pixels[row_start:row_start + img.width])
    write_ppm(flipped, img.width, img.height, img.maxval, dest_path)
    return {"ok": True, "width": img.width, "height": img.height, "pixel_count": len(flipped)}


def rotate_90(file_path: str | Path, dest_path: str | Path) -> dict[str, Any]:
    """Rotate a PPM image 90 degrees clockwise and write the result.

    The output image has width=original_height and height=original_width.
    Pixel at (row, col) in the original maps to (col, height-1-row) in the result.

    Args:
        file_path: Source PPM file path.
        dest_path: Destination PPM file path.

    Returns:
        Dict with keys: ok, width, height, pixel_count.

    Raises:
        PpmError: If source cannot be parsed.
    """
    img = parse_ppm_strict(file_path)
    new_w = img.height
    new_h = img.width
    rotated: list[tuple[int, int, int]] = [(0, 0, 0)] * (new_w * new_h)
    for row in range(img.height):
        for col in range(img.width):
            src_idx = row * img.width + col
            dst_row = col
            dst_col = img.height - 1 - row
            dst_idx = dst_row * new_w + dst_col
            rotated[dst_idx] = img.pixels[src_idx]
    write_ppm(rotated, new_w, new_h, img.maxval, dest_path)
    return {"ok": True, "width": new_w, "height": new_h, "pixel_count": len(rotated)}


def is_grayscale(file_path: str | Path) -> bool:
    """Return True if all pixels in a PPM image are grayscale (R == G == B).

    Args:
        file_path: Path to a PPM file.

    Returns:
        True if every pixel has equal R, G, B channels. False otherwise.
        Returns True for empty images (vacuously).

    Raises:
        PpmError: If the file cannot be parsed.
    """
    img = parse_ppm_strict(file_path)
    return all(r == g == b for r, g, b in img.pixels)


def ppm_red_channel_average(file_path: str | Path) -> float:
    """Return the average value of the red channel across all pixels.

    Args:
        file_path: Path to a PPM file.

    Returns:
        Float average red channel value. Returns 0.0 for empty images.

    Raises:
        PpmError: If the file cannot be parsed.
    """
    img = parse_ppm_strict(file_path)
    if not img.pixels:
        return 0.0
    return sum(p[0] for p in img.pixels) / len(img.pixels)


def ppm_green_channel_average(file_path: str | Path) -> float:
    """Return the average value of the green channel across all pixels.

    Args:
        file_path: Path to a PPM file.

    Returns:
        Float average green channel value. Returns 0.0 for empty images.

    Raises:
        PpmError: If the file cannot be parsed.
    """
    img = parse_ppm_strict(file_path)
    if not img.pixels:
        return 0.0
    return sum(p[1] for p in img.pixels) / len(img.pixels)


def ppm_unique_color_count(file_path: str | Path) -> int:
    """Return the number of unique RGB color tuples in the image.

    Args:
        file_path: Path to a PPM file.

    Returns:
        Integer count of distinct (R, G, B) color tuples. Returns 0 for empty images.

    Raises:
        PpmError: If the file cannot be parsed.
    """
    img = parse_ppm_strict(file_path)
    return len(set(img.pixels))


def ppm_pixel_count(file_path: str | Path) -> int:
    """Return the total number of pixels in a PPM image (width * height).

    Args:
        file_path: Path to a PPM file.

    Returns:
        Integer pixel count. Returns 0 for empty images.

    Raises:
        PpmError: If the file cannot be parsed.
    """
    img = parse_ppm_strict(file_path)
    return len(img.pixels)


def ppm_brightness_variance(file_path: str | Path) -> float:
    """Return the variance of per-pixel brightness (mean of R, G, B) across the image.

    Args:
        file_path: Path to a PPM file.

    Returns:
        Float variance of brightness values. Returns 0.0 for single-pixel or empty images.

    Raises:
        PpmError: If the file cannot be parsed.
    """
    img = parse_ppm_strict(file_path)
    if not img.pixels:
        return 0.0
    brightnesses = [sum(p) / 3.0 for p in img.pixels]
    avg = sum(brightnesses) / len(brightnesses)
    return sum((b - avg) ** 2 for b in brightnesses) / len(brightnesses)


def ppm_is_binary(file_path: str | Path) -> bool:
    """Return True if the PPM file uses binary P6 format, False if ASCII P3.

    Args:
        file_path: Path to a PPM file.

    Returns:
        True for P6 (binary), False for P3 (ASCII).

    Raises:
        PpmError: If the file cannot be parsed or has an unrecognized magic.
    """
    p = Path(file_path)
    data = p.read_bytes()
    magic = data[:2]
    if magic == b"P6":
        return True
    if magic == b"P3":
        return False
    raise PpmError(f"Unrecognized PPM magic: {magic!r}")


def ppm_aspect_ratio(file_path: str | Path) -> float:
    """Return the aspect ratio (width / height) of a PPM image.

    Args:
        file_path: Path to a PPM file.

    Returns:
        Float aspect ratio. Returns 0.0 if height is 0.

    Raises:
        PpmError: If the file cannot be parsed.
    """
    img = parse_ppm_strict(file_path)
    if img.height == 0:
        return 0.0
    return img.width / img.height


def ppm_dominant_channel(file_path: str | Path) -> str:
    """Return the dominant color channel ('red', 'green', or 'blue') of a PPM image.

    The dominant channel is the one with the highest sum of pixel values.

    Args:
        file_path: Path to a PPM file.

    Returns:
        String 'red', 'green', or 'blue'. Returns 'red' for empty images (tie-break).

    Raises:
        PpmError: If the file cannot be parsed.
    """
    img = parse_ppm_strict(file_path)
    if not img.pixels:
        return "red"
    r_sum = sum(p[0] for p in img.pixels)
    g_sum = sum(p[1] for p in img.pixels)
    b_sum = sum(p[2] for p in img.pixels)
    if r_sum >= g_sum and r_sum >= b_sum:
        return "red"
    if g_sum >= b_sum:
        return "green"
    return "blue"


def ppm_min_max_brightness(file_path: str | Path) -> dict[str, float]:
    """Return the min and max pixel brightness of a PPM image.

    Brightness is computed as 0.299*R + 0.587*G + 0.114*B (ITU-R BT.601).

    Args:
        file_path: Path to a PPM file.

    Returns:
        Dict with 'min' and 'max' float values. Returns {'min': 0.0, 'max': 0.0}
        for empty images.

    Raises:
        PpmError: If the file cannot be parsed.
    """
    img = parse_ppm_strict(file_path)
    if not img.pixels:
        return {"min": 0.0, "max": 0.0}
    brightnesses = [0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2] for p in img.pixels]
    return {"min": min(brightnesses), "max": max(brightnesses)}


def ppm_blue_channel_average(file_path: str | Path) -> float:
    """Return the average blue channel value across all pixels."""
    img = parse_ppm_strict(file_path)
    if not img.pixels:
        return 0.0
    return sum(p[2] for p in img.pixels) / len(img.pixels)


def ppm_is_grayscale(file_path: str | Path) -> bool:
    """Return True if all pixels have equal R, G, B values."""
    img = parse_ppm_strict(file_path)
    if not img.pixels:
        return True
    return all(p[0] == p[1] == p[2] for p in img.pixels)


def ppm_channel_range(file_path: str | Path) -> dict[str, int]:
    """Return the range (max - min) for each RGB channel."""
    img = parse_ppm_strict(file_path)
    if not img.pixels:
        return {"red": 0, "green": 0, "blue": 0}
    reds = [p[0] for p in img.pixels]
    greens = [p[1] for p in img.pixels]
    blues = [p[2] for p in img.pixels]
    return {
        "red": max(reds) - min(reds),
        "green": max(greens) - min(greens),
        "blue": max(blues) - min(blues),
    }


def ppm_saturation_estimate(file_path: str | Path) -> float:
    """Return the average per-pixel saturation estimate (max_channel - min_channel)."""
    img = parse_ppm_strict(file_path)
    if not img.pixels:
        return 0.0
    total = sum(max(p[0], p[1], p[2]) - min(p[0], p[1], p[2]) for p in img.pixels)
    return total / len(img.pixels)


def ppm_is_dark(file_path: str | Path) -> bool:
    """Return True if the average pixel brightness is below 128.

    Args:
        file_path: Path to a PPM file.

    Returns:
        True if average brightness < 128, False otherwise or if no pixels.
    """
    img = parse_ppm_strict(file_path)
    if not img.pixels:
        return False
    avg = sum((p[0] + p[1] + p[2]) / 3.0 for p in img.pixels) / len(img.pixels)
    return avg < 128.0


def ppm_red_channel_sum(file_path: str | Path) -> int:
    """Return the sum of all red channel pixel values.

    Args:
        file_path: Path to a PPM file.

    Returns:
        Integer sum of all red channel values.
    """
    img = parse_ppm_strict(file_path)
    return sum(p[0] for p in img.pixels)


def ppm_luminance_average(file_path: str | Path) -> float:
    """Return the average luminance using ITU-R BT.601 formula.

    Y = 0.299*R + 0.587*G + 0.114*B

    Args:
        file_path: Path to a PPM file.

    Returns:
        Float average luminance in [0.0, maxval]. Returns 0.0 for empty images.
    """
    img = parse_ppm_strict(file_path)
    if not img.pixels:
        return 0.0
    total = sum(0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2] for p in img.pixels)
    return total / len(img.pixels)


def ppm_green_channel_sum(file_path: str | Path) -> int:
    """Return the sum of all green channel pixel values.

    Args:
        file_path: Path to a PPM file.

    Returns:
        Integer sum of all green channel values.
    """
    img = parse_ppm_strict(file_path)
    return sum(p[1] for p in img.pixels)


def ppm_row_count(file_path: str | Path) -> int:
    """Return the number of rows (height) in the PPM image."""
    img = parse_ppm_strict(file_path)
    return img.height


def ppm_blue_channel_sum(file_path: str | Path) -> int:
    """Return the sum of all blue channel pixel values."""
    img = parse_ppm_strict(file_path)
    return sum(p[2] for p in img.pixels)


def ppm_unique_color_count(file_path: str | Path) -> int:
    """Return the number of distinct colors (R,G,B tuples) in the image.

    Args:
        file_path: Path to a PPM file.

    Returns:
        Integer count of unique color tuples. 0 for empty images.
    """
    img = parse_ppm_strict(file_path)
    if not img.pixels:
        return 0
    return len(set(tuple(p) for p in img.pixels))


def ppm_perimeter(file_path: str | Path) -> int:
    """Return the image perimeter in pixels: 2 * (width + height).

    Args:
        file_path: Path to a PPM file.

    Returns:
        Integer perimeter.
    """
    img = parse_ppm_strict(file_path)
    return 2 * (img.width + img.height)


def ppm_dimension_ratio(file_path: str | Path) -> float:
    """Return width / height ratio. 0.0 if height is 0."""
    img = parse_ppm_strict(file_path)
    if img.height == 0:
        return 0.0
    return img.width / img.height


def ppm_is_square(file_path: str | Path) -> bool:
    """Return True if the PPM image width equals its height."""
    img = parse_ppm_strict(file_path)
    return img.width == img.height


def ppm_is_landscape(file_path: str | Path) -> bool:
    """Return True if the PPM image is wider than it is tall."""
    img = parse_ppm_strict(file_path)
    return img.width > img.height


def ppm_max_dimension(file_path: str | Path) -> int:
    """Return the larger of width and height."""
    img = parse_ppm_strict(file_path)
    return max(img.width, img.height)


def ppm_has_pure_black(file_path: str | Path) -> bool:
    """Return True if any pixel is pure black (R=0, G=0, B=0)."""
    img = parse_ppm_strict(file_path)
    return any(r == 0 and g == 0 and b == 0 for r, g, b in img.pixels)


def ppm_max_channel_sum(file_path: str | Path) -> int:
    """Return the maximum R+G+B sum across all pixels."""
    img = parse_ppm_strict(file_path)
    if not img.pixels:
        return 0
    return max(r + g + b for r, g, b in img.pixels)


def ppm_min_channel_sum(file_path: str | Path) -> int:
    """Return the minimum R+G+B sum across all pixels."""
    img = parse_ppm_strict(file_path)
    if not img.pixels:
        return 0
    return min(r + g + b for r, g, b in img.pixels)


def ppm_has_pure_white(file_path: str | Path) -> bool:
    """Return True if any pixel has R=maxval, G=maxval, B=maxval."""
    img = parse_ppm_strict(file_path)
    mv = img.maxval
    return any(r == mv and g == mv and b == mv for r, g, b in img.pixels)


def ppm_megapixels(file_path: str | Path) -> float:
    """Return image size in megapixels."""
    img = parse_ppm_strict(file_path)
    return (img.width * img.height) / 1_000_000


def ppm_channel_balance(file_path: str | Path) -> float:
    """Return 1.0 - (max_avg - min_avg)/maxval. Higher = more balanced."""
    img = parse_ppm_strict(file_path)
    if not img.pixels or img.maxval == 0:
        return 1.0
    r_avg = sum(p[0] for p in img.pixels) / len(img.pixels)
    g_avg = sum(p[1] for p in img.pixels) / len(img.pixels)
    b_avg = sum(p[2] for p in img.pixels) / len(img.pixels)
    spread = max(r_avg, g_avg, b_avg) - min(r_avg, g_avg, b_avg)
    return 1.0 - (spread / img.maxval)


def ppm_column_count(file_path: str | Path) -> int:
    """Return the number of columns (width) in the image."""
    img = parse_ppm_strict(file_path)
    return img.width


def ppm_min_dimension(file_path: str | Path) -> int:
    """Return the minimum of width and height."""
    img = parse_ppm_strict(file_path)
    return min(img.width, img.height)


def ppm_is_tall(file_path: str | Path) -> bool:
    """Return True if height > 2 * width."""
    img = parse_ppm_strict(file_path)
    return img.height > 2 * img.width


def ppm_pixel_density(file_path: str | Path) -> float:
    """Return pixels per byte of file size. 0.0 if file_size is 0."""
    img = parse_ppm_strict(file_path)
    fsize = Path(file_path).stat().st_size
    if fsize == 0:
        return 0.0
    return (img.width * img.height) / fsize


def ppm_is_portrait(file_path: str | Path) -> bool:
    """Return True if height > width."""
    img = parse_ppm_strict(file_path)
    return img.height > img.width


def ppm_diagonal(file_path: str | Path) -> float:
    """Return diagonal length: sqrt(width^2 + height^2)."""
    import math
    img = parse_ppm_strict(file_path)
    return math.sqrt(img.width ** 2 + img.height ** 2)


def ppm_is_monochrome(file_path: str | Path) -> bool:
    """Return True if all pixels share the same RGB values."""
    img = parse_ppm_strict(file_path)
    if not img.pixels:
        return True
    first = (img.pixels[0][0], img.pixels[0][1], img.pixels[0][2])
    return all((p[0], p[1], p[2]) == first for p in img.pixels)


def ppm_total_channel_sum(file_path: str | Path) -> int:
    """Return the sum of all R+G+B values across all pixels."""
    img = parse_ppm_strict(file_path)
    return sum(p[0] + p[1] + p[2] for p in img.pixels)


def ppm_avg_brightness(file_path: str | Path) -> float:
    """Return average brightness (mean of R+G+B / 3) across all pixels. 0.0 if none."""
    img = parse_ppm_strict(file_path)
    if not img.pixels:
        return 0.0
    total = sum((p[0] + p[1] + p[2]) / 3.0 for p in img.pixels)
    return total / len(img.pixels)


def ppm_color_variance(file_path: str | Path) -> float:
    """Return variance of pixel brightness values. 0.0 if fewer than 2 pixels."""
    img = parse_ppm_strict(file_path)
    if len(img.pixels) < 2:
        return 0.0
    brightnesses = [(p[0] + p[1] + p[2]) / 3.0 for p in img.pixels]
    mean = sum(brightnesses) / len(brightnesses)
    return sum((b - mean) ** 2 for b in brightnesses) / len(brightnesses)


def ppm_distinct_pixel_count(file_path: str | Path) -> int:
    """Return the count of distinct (R, G, B) pixel tuples."""
    img = parse_ppm_strict(file_path)
    return len(set(img.pixels))


def ppm_is_grayscale(file_path: str | Path) -> bool:
    """Return True if all pixels have equal R, G, and B channel values."""
    img = parse_ppm_strict(file_path)
    if not img.pixels:
        return True
    return all(p[0] == p[1] == p[2] for p in img.pixels)


def ppm_red_ratio(file_path: str | Path) -> float:
    """Return ratio of red channel sum to total channel sum. 0.0 if no pixels."""
    img = parse_ppm_strict(file_path)
    if not img.pixels:
        return 0.0
    red = sum(p[0] for p in img.pixels)
    total = sum(p[0] + p[1] + p[2] for p in img.pixels)
    if total == 0:
        return 0.0
    return red / total


def ppm_border_brightness(file_path: str | Path) -> float:
    """Return average brightness of border pixels. 0.0 if no pixels."""
    img = parse_ppm_strict(file_path)
    if img.width == 0 or img.height == 0:
        return 0.0
    border = []
    for i, p in enumerate(img.pixels):
        r = i // img.width
        c = i % img.width
        if r == 0 or r == img.height - 1 or c == 0 or c == img.width - 1:
            border.append((p[0] + p[1] + p[2]) / 3.0)
    if not border:
        return 0.0
    return sum(border) / len(border)


def ppm_green_ratio(file_path: str | Path) -> float:
    """Return ratio of green channel sum to total channel sum. 0.0 if no pixels."""
    img = parse_ppm_strict(file_path)
    if not img.pixels:
        return 0.0
    green = sum(p[1] for p in img.pixels)
    total = sum(p[0] + p[1] + p[2] for p in img.pixels)
    if total == 0:
        return 0.0
    return green / total


def ppm_pixel_brightness_range(file_path: str | Path) -> float:
    """Return brightness range (max - min) as ratio of maxval. 0.0 if no pixels."""
    img = parse_ppm_strict(file_path)
    if not img.pixels:
        return 0.0
    brightnesses = [(p[0] + p[1] + p[2]) / 3.0 for p in img.pixels]
    return (max(brightnesses) - min(brightnesses)) / max(img.maxval, 1)


def ppm_blue_ratio(file_path: str | Path) -> float:
    """Return blue channel sum as ratio of total channel sum. 0.0 if no pixels."""
    img = parse_ppm_strict(file_path)
    if not img.pixels:
        return 0.0
    total = sum(p[0] + p[1] + p[2] for p in img.pixels)
    if total == 0:
        return 0.0
    blue = sum(p[2] for p in img.pixels)
    return blue / total


def ppm_is_bright(file_path: str | Path) -> bool:
    """Return True if mean brightness exceeds 66% of maxval."""
    img = parse_ppm_strict(file_path)
    if not img.pixels or img.maxval == 0:
        return False
    mean = sum((p[0] + p[1] + p[2]) / 3.0 for p in img.pixels) / len(img.pixels)
    return mean > (img.maxval * 0.66)


def ppm_maxval(file_path: str | Path) -> int:
    """Return the maxval field from the PPM header."""
    img = parse_ppm_strict(file_path)
    return img.maxval


def ppm_normalized_brightness(file_path: str | Path) -> float:
    """Return mean brightness normalized to [0.0, 1.0] by maxval. 0.0 if no pixels."""
    img = parse_ppm_strict(file_path)
    if not img.pixels or img.maxval == 0:
        return 0.0
    mean = sum((p[0] + p[1] + p[2]) / 3.0 for p in img.pixels) / len(img.pixels)
    return mean / img.maxval


def ppm_area(file_path: str | Path) -> int:
    """Return image area in pixels: width * height."""
    img = parse_ppm_strict(file_path)
    return img.width * img.height


def ppm_min_channel_avg(file_path: str | Path) -> float:
    """Return the minimum of the average R, G, B channel values. 0.0 if no pixels."""
    img = parse_ppm_strict(file_path)
    if not img.pixels:
        return 0.0
    n = len(img.pixels)
    avg_r = sum(p[0] for p in img.pixels) / n
    avg_g = sum(p[1] for p in img.pixels) / n
    avg_b = sum(p[2] for p in img.pixels) / n
    return min(avg_r, avg_g, avg_b)


def ppm_max_pixel_brightness(file_path: str | Path) -> float:
    """Return the maximum per-pixel brightness ((R+G+B)/3). 0.0 if no pixels."""
    img = parse_ppm_strict(file_path)
    if not img.pixels:
        return 0.0
    return max((p[0] + p[1] + p[2]) / 3.0 for p in img.pixels)
