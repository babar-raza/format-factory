"""
qoi_parser.py — QOI (Quite OK Image) decoder for format-factory-qoi.

Public API:
  parse_qoi(file_path)        — returns result dict (never raises)
  parse_qoi_strict(file_path) — raises QoiError on failure
  probe_qoi(file_path)        — returns header metadata without pixel decode

Implements Gate 4 prototype scope per R26 parser plan.
Full pixel decode of all 6 QOI chunk types.
Technology: Python struct.unpack binary decoder (stdlib).

License: Apache-2.0
"""

from __future__ import annotations

import os
import struct
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# QOI constants
QOI_MAGIC = b"qoif"
QOI_HEADER_SIZE = 14
QOI_END_MARKER = bytes([0, 0, 0, 0, 0, 0, 0, 1])
MAX_FILE_SIZE = 64 * 1024 * 1024  # 64 MiB
MAX_DIMENSION = 16384
MAX_PIXELS = MAX_DIMENSION * MAX_DIMENSION

# Chunk tag masks
QOI_OP_INDEX = 0x00  # 0b00xxxxxx
QOI_OP_DIFF = 0x40   # 0b01xxxxxx
QOI_OP_LUMA = 0x80   # 0b10xxxxxx
QOI_OP_RUN = 0xC0    # 0b11xxxxxx
QOI_OP_RGB = 0xFE
QOI_OP_RGBA = 0xFF


UNSUPPORTED_FEATURES = frozenset({
    "animation",
    "multi_frame",
    "metadata_embedding",
    "icc_profiles",
    "exif",
    "encoding",
    "streaming_decode",
    "partial_decode",
    "thumbnail_extraction",
    "color_management",
})

SUPPORTED_FEATURES = frozenset({
    "header_parse",
    "full_pixel_decode",
    "op_rgb",
    "op_rgba",
    "op_index",
    "op_diff",
    "op_luma",
    "op_run",
    "3_channel_mode",
    "4_channel_mode",
    "srgb_colorspace",
    "linear_colorspace",
    "end_marker_validation",
    "size_guard",
    "probe_without_decode",
})


def get_capabilities() -> dict[str, Any]:
    """Return supported/unsupported feature declarations for QOI parser."""
    return {
        "format": "qoi",
        "gate": 5,
        "supported": sorted(SUPPORTED_FEATURES),
        "unsupported": sorted(UNSUPPORTED_FEATURES),
        "commercial_product_ready": False,
        "max_file_size": MAX_FILE_SIZE,
        "max_dimension": MAX_DIMENSION,
        "max_pixels": MAX_PIXELS,
    }


class QoiError(Exception):
    """Base exception for QOI parser errors."""


class QoiInvalidMagicError(QoiError):
    """Raised when the file magic is not 'qoif'."""


class QoiInvalidHeaderError(QoiError):
    """Raised when header fields are invalid."""


class QoiSizeError(QoiError):
    """Raised when file or image dimensions exceed limits."""


class QoiDecodeError(QoiError):
    """Raised when pixel data cannot be decoded."""


@dataclass
class QoiImage:
    width: int = 0
    height: int = 0
    channels: int = 4
    colorspace: int = 0
    pixels: list[tuple[int, ...]] = field(default_factory=list)
    path: str = ""


def _color_hash(r: int, g: int, b: int, a: int) -> int:
    return (r * 3 + g * 5 + b * 7 + a * 11) % 64


def _parse_header(data: bytes) -> tuple[int, int, int, int]:
    """Parse and validate QOI header. Returns (width, height, channels, colorspace)."""
    if len(data) < QOI_HEADER_SIZE:
        raise QoiDecodeError(
            f"File too short: {len(data)} bytes, need at least {QOI_HEADER_SIZE}"
        )
    magic = data[:4]
    if magic != QOI_MAGIC:
        raise QoiInvalidMagicError(
            f"Invalid magic: expected {QOI_MAGIC!r}, got {magic!r}"
        )
    width, height = struct.unpack(">II", data[4:12])
    channels = data[12]
    colorspace = data[13]

    if channels not in (3, 4):
        raise QoiInvalidHeaderError(f"Invalid channels: {channels}, must be 3 or 4")
    if colorspace not in (0, 1):
        raise QoiInvalidHeaderError(
            f"Invalid colorspace: {colorspace}, must be 0 or 1"
        )
    if width == 0 or height == 0:
        raise QoiInvalidHeaderError(f"Invalid dimensions: {width}x{height}")
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        raise QoiSizeError(
            f"Dimensions {width}x{height} exceed limit of {MAX_DIMENSION}x{MAX_DIMENSION}"
        )
    if width * height > MAX_PIXELS:
        raise QoiSizeError(
            f"Pixel count {width * height} exceeds limit of {MAX_PIXELS}"
        )
    return width, height, channels, colorspace


def _decode_pixels(
    data: bytes, width: int, height: int, channels: int
) -> list[tuple[int, ...]]:
    """Decode QOI pixel data from all 6 chunk types."""
    pixel_count = width * height
    pixels: list[tuple[int, ...]] = []

    # Running color hash array
    index = [(0, 0, 0, 0)] * 64
    r, g, b, a = 0, 0, 0, 255  # Previous pixel

    pos = QOI_HEADER_SIZE
    end = len(data) - 8  # Exclude end marker

    while len(pixels) < pixel_count and pos < end:
        byte = data[pos]

        if byte == QOI_OP_RGB:
            if pos + 3 >= end:
                raise QoiDecodeError("Truncated QOI_OP_RGB chunk")
            r = data[pos + 1]
            g = data[pos + 2]
            b = data[pos + 3]
            pos += 4
        elif byte == QOI_OP_RGBA:
            if pos + 4 >= end:
                raise QoiDecodeError("Truncated QOI_OP_RGBA chunk")
            r = data[pos + 1]
            g = data[pos + 2]
            b = data[pos + 3]
            a = data[pos + 4]
            pos += 5
        elif (byte & 0xC0) == QOI_OP_INDEX:
            idx = byte & 0x3F
            r, g, b, a = index[idx]
            pos += 1
        elif (byte & 0xC0) == QOI_OP_DIFF:
            dr = ((byte >> 4) & 0x03) - 2
            dg = ((byte >> 2) & 0x03) - 2
            db = (byte & 0x03) - 2
            r = (r + dr) & 0xFF
            g = (g + dg) & 0xFF
            b = (b + db) & 0xFF
            pos += 1
        elif (byte & 0xC0) == QOI_OP_LUMA:
            if pos + 1 >= end:
                raise QoiDecodeError("Truncated QOI_OP_LUMA chunk")
            byte2 = data[pos + 1]
            dg = (byte & 0x3F) - 32
            dr_dg = ((byte2 >> 4) & 0x0F) - 8
            db_dg = (byte2 & 0x0F) - 8
            r = (r + dg + dr_dg) & 0xFF
            g = (g + dg) & 0xFF
            b = (b + dg + db_dg) & 0xFF
            pos += 2
        elif (byte & 0xC0) == QOI_OP_RUN:
            run_length = (byte & 0x3F) + 1
            for _ in range(min(run_length, pixel_count - len(pixels))):
                if channels == 3:
                    pixels.append((r, g, b))
                else:
                    pixels.append((r, g, b, a))
            idx_hash = _color_hash(r, g, b, a)
            index[idx_hash] = (r, g, b, a)
            pos += 1
            continue  # Skip the append below — already added
        else:
            pos += 1
            continue

        idx_hash = _color_hash(r, g, b, a)
        index[idx_hash] = (r, g, b, a)
        if channels == 3:
            pixels.append((r, g, b))
        else:
            pixels.append((r, g, b, a))

    if len(pixels) < pixel_count:
        raise QoiDecodeError(
            f"Decoded {len(pixels)} pixels, expected {pixel_count}"
        )

    # Verify end marker
    marker = data[end : end + 8]
    if marker != QOI_END_MARKER:
        raise QoiDecodeError(
            f"Invalid end marker: expected {QOI_END_MARKER.hex()}, got {marker.hex()}"
        )

    return pixels


def parse_qoi_strict(file_path: str | Path) -> QoiImage:
    """Parse a QOI file, raising QoiError on any problem."""
    path = Path(file_path)
    size = os.path.getsize(path)
    if size > MAX_FILE_SIZE:
        raise QoiSizeError(
            f"File size {size} bytes exceeds limit of {MAX_FILE_SIZE}"
        )
    data = path.read_bytes()
    width, height, channels, colorspace = _parse_header(data)
    pixels = _decode_pixels(data, width, height, channels)
    return QoiImage(
        width=width,
        height=height,
        channels=channels,
        colorspace=colorspace,
        pixels=pixels,
        path=str(path),
    )


def parse_qoi(file_path: str | Path) -> dict[str, Any]:
    """Parse a QOI file, returning a result dict (never raises)."""
    try:
        img = parse_qoi_strict(file_path)
        return {
            "ok": True,
            "path": img.path,
            "width": img.width,
            "height": img.height,
            "channels": img.channels,
            "colorspace": img.colorspace,
            "pixel_count": len(img.pixels),
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc), "error_type": type(exc).__name__}


def probe_qoi(file_path: str | Path) -> dict[str, Any]:
    """Probe a QOI file for header metadata without decoding pixels."""
    path = Path(file_path)
    result: dict[str, Any] = {"path": str(path), "exists": path.exists()}
    if not path.exists():
        return result
    try:
        data = path.read_bytes()
        if len(data) < QOI_HEADER_SIZE:
            result["valid_header"] = False
            result["error"] = f"File too short: {len(data)} bytes"
            return result
        width, height, channels, colorspace = _parse_header(data)
        result["valid_header"] = True
        result["width"] = width
        result["height"] = height
        result["channels"] = channels
        result["colorspace"] = colorspace
        result["file_size"] = len(data)
    except Exception as exc:
        result["valid_header"] = False
        result["error"] = str(exc)
    return result


def qoi_dimensions(file_path: str | Path) -> dict[str, int]:
    """Return image dimensions and channel info from a QOI file header (no pixel decode)."""
    path = Path(file_path)
    data = path.read_bytes()
    width, height, channels, colorspace = _parse_header(data)
    return {"width": width, "height": height, "channels": channels, "colorspace": colorspace}


def qoi_pixel_count(file_path: str | Path) -> int:
    """Return the total pixel count (width * height) of a QOI image."""
    path = Path(file_path)
    data = path.read_bytes()
    width, height, _channels, _colorspace = _parse_header(data)
    return width * height


def qoi_unique_color_count(file_path: str | Path) -> int:
    """Return the number of unique pixel color tuples in a QOI image."""
    img = parse_qoi_strict(file_path)
    return len(set(img.pixels))


def qoi_channel_count(file_path: str | Path) -> int:
    """Return the number of color channels (3=RGB or 4=RGBA) in a QOI image."""
    path = Path(file_path)
    data = path.read_bytes()
    _width, _height, channels, _colorspace = _parse_header(data)
    return channels


def qoi_is_opaque(file_path: str | Path) -> bool:
    """Return True if every pixel in the QOI image has alpha == 255.

    For 3-channel (RGB) images this always returns True since there is
    no alpha channel.  For 4-channel (RGBA) images it decodes all pixels
    and checks that every alpha value equals 255.

    Args:
        file_path: Path to a QOI file.

    Returns:
        True if the image is fully opaque, False otherwise.
    """
    img = parse_qoi_strict(file_path)
    if img.channels == 3:
        return True
    return all(pixel[3] == 255 for pixel in img.pixels)


def qoi_has_alpha(file_path: str | Path) -> bool:
    """Return True if the QOI image has an alpha channel (4 channels).

    This is a header-only operation — no pixel decode required.

    Args:
        file_path: Path to a QOI file.

    Returns:
        True if channels == 4 (RGBA), False if channels == 3 (RGB).
    """
    path = Path(file_path)
    data = path.read_bytes()
    _width, _height, channels, _colorspace = _parse_header(data)
    return channels == 4


def qoi_average_brightness(file_path: str | Path) -> float:
    """Return the average pixel brightness of a QOI image.

    Brightness is computed as the mean of (0.299*R + 0.587*G + 0.114*B)
    across all pixels, using the ITU-R BT.601 luma formula.

    Args:
        file_path: Path to a QOI file.

    Returns:
        Average brightness as a float in range [0.0, 255.0].
    """
    img = parse_qoi_strict(file_path)
    if not img.pixels:
        return 0.0
    total = sum(0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2] for p in img.pixels)
    return total / len(img.pixels)


def qoi_red_channel_average(file_path: str | Path) -> float:
    """Return the average red channel value across all pixels.

    Args:
        file_path: Path to a QOI file.

    Returns:
        Average red value as a float in range [0.0, 255.0].
        Returns 0.0 for empty images.
    """
    img = parse_qoi_strict(file_path)
    if not img.pixels:
        return 0.0
    return sum(p[0] for p in img.pixels) / len(img.pixels)


def qoi_dominant_channel(file_path: str | Path) -> str:
    """Return the name of the dominant color channel ('red', 'green', or 'blue').

    Dominant is defined as the channel with the highest total value sum
    across all pixels. Ties are broken in R > G > B order.

    Args:
        file_path: Path to a QOI file.

    Returns:
        One of 'red', 'green', 'blue'.
    """
    img = parse_qoi_strict(file_path)
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


def qoi_min_max_brightness(file_path: str | Path) -> dict[str, float]:
    """Return the min and max pixel brightness values.

    Brightness uses the ITU-R BT.601 luma formula:
    Y = 0.299*R + 0.587*G + 0.114*B

    Args:
        file_path: Path to a QOI file.

    Returns:
        Dict with keys 'min' and 'max' (float in range [0.0, 255.0]).
    """
    img = parse_qoi_strict(file_path)
    if not img.pixels:
        return {"min": 0.0, "max": 0.0}
    brightnesses = [0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2] for p in img.pixels]
    return {"min": min(brightnesses), "max": max(brightnesses)}


def qoi_green_channel_average(file_path: str | Path) -> float:
    """Return the average green channel value across all pixels.

    Args:
        file_path: Path to a QOI file.

    Returns:
        Float average in [0.0, 255.0]. Returns 0.0 for empty images.
    """
    img = parse_qoi_strict(file_path)
    if not img.pixels:
        return 0.0
    return sum(p[1] for p in img.pixels) / len(img.pixels)


def qoi_blue_channel_average(file_path: str | Path) -> float:
    """Return the average blue channel value across all pixels.

    Args:
        file_path: Path to a QOI file.

    Returns:
        Float average in [0.0, 255.0]. Returns 0.0 for empty images.
    """
    img = parse_qoi_strict(file_path)
    if not img.pixels:
        return 0.0
    return sum(p[2] for p in img.pixels) / len(img.pixels)


def qoi_is_grayscale(file_path: str | Path) -> bool:
    """Return True if all pixels have equal R, G, B channels.

    Args:
        file_path: Path to a QOI file.

    Returns:
        True if every pixel satisfies R == G == B.
    """
    img = parse_qoi_strict(file_path)
    if not img.pixels:
        return True
    return all(p[0] == p[1] == p[2] for p in img.pixels)


def qoi_brightness_variance(file_path: str | Path) -> float:
    """Return the variance of pixel brightness values.

    Brightness is computed as (R + G + B) / 3 per pixel.

    Args:
        file_path: Path to a QOI file.

    Returns:
        Float variance. Returns 0.0 for empty images.
    """
    img = parse_qoi_strict(file_path)
    if not img.pixels:
        return 0.0
    brightnesses = [(p[0] + p[1] + p[2]) / 3.0 for p in img.pixels]
    mean = sum(brightnesses) / len(brightnesses)
    return sum((b - mean) ** 2 for b in brightnesses) / len(brightnesses)


def qoi_total_brightness(file_path: str | Path) -> float:
    """Return the sum of all pixel brightness values (R+G+B)/3."""
    img = parse_qoi_strict(file_path)
    if not img.pixels:
        return 0.0
    return sum((p[0] + p[1] + p[2]) / 3.0 for p in img.pixels)


def qoi_avg_rgb_value(file_path: str | Path) -> float:
    """Return the average of all channel values across all pixels.

    Computes mean of R, G, B values across every pixel.

    Args:
        file_path: Path to a QOI file.

    Returns:
        Float average RGB value (0.0-255.0), or 0.0 if no pixels.
    """
    img = parse_qoi_strict(file_path)
    if not img.pixels:
        return 0.0
    total = sum(p[0] + p[1] + p[2] for p in img.pixels)
    return total / (len(img.pixels) * 3)


def qoi_red_dominance_ratio(file_path: str | Path) -> float:
    """Return the ratio of red channel sum to total RGB sum.

    Args:
        file_path: Path to a QOI file.

    Returns:
        Float ratio 0.0-1.0, or 0.0 if no pixels.
    """
    img = parse_qoi_strict(file_path)
    if not img.pixels:
        return 0.0
    red_sum = sum(p[0] for p in img.pixels)
    total = sum(p[0] + p[1] + p[2] for p in img.pixels)
    if total == 0:
        return 0.0
    return red_sum / total


def qoi_aspect_ratio(file_path: str | Path) -> float:
    """Return the aspect ratio (width / height) of a QOI image.

    Args:
        file_path: Path to a QOI file.

    Returns:
        Float ratio. Returns 0.0 for zero-height images.
    """
    path = Path(file_path)
    data = path.read_bytes()
    width, height, _channels, _colorspace = _parse_header(data)
    if height == 0:
        return 0.0
    return width / height


def qoi_color_concentration(file_path: str | Path) -> float:
    """Return color concentration: unique_colors / total_pixels.

    Lower values mean fewer unique colors relative to pixel count
    (more repeated colors). A value of 1.0 means every pixel is unique.

    Args:
        file_path: Path to a QOI file.

    Returns:
        Float ratio in (0.0, 1.0], or 0.0 for empty images.
    """
    img = parse_qoi_strict(file_path)
    if not img.pixels:
        return 0.0
    unique = len(set(img.pixels))
    return unique / len(img.pixels)


def qoi_avg_rgb(file_path: str | Path) -> tuple:
    """Return the average (R, G, B) values across all pixels.

    Args:
        file_path: Path to a QOI file.

    Returns:
        Tuple of three floats (avg_r, avg_g, avg_b). Returns (0.0, 0.0, 0.0) for empty images.
    """
    img = parse_qoi_strict(file_path)
    if not img.pixels:
        return (0.0, 0.0, 0.0)
    n = len(img.pixels)
    r = sum(p[0] for p in img.pixels) / n
    g = sum(p[1] for p in img.pixels) / n
    b = sum(p[2] for p in img.pixels) / n
    return (r, g, b)


def qoi_red_dominant(file_path: str | Path) -> bool:
    """Return True if the red channel has the highest average across all pixels.

    Args:
        file_path: Path to a QOI file.

    Returns:
        True if avg red > avg green and avg red > avg blue. False otherwise.
    """
    avg_r, avg_g, avg_b = qoi_avg_rgb(file_path)
    return avg_r > avg_g and avg_r > avg_b


def qoi_blue_dominant(file_path: str | Path) -> bool:
    """Return True if the blue channel has the highest average across all pixels.

    Args:
        file_path: Path to a QOI file.

    Returns:
        True if avg blue > avg red and avg blue > avg green. False otherwise.
    """
    avg_r, avg_g, avg_b = qoi_avg_rgb(file_path)
    return avg_b > avg_r and avg_b > avg_g


def qoi_green_dominant(file_path: str | Path) -> bool:
    """Return True if the green channel has the highest average across all pixels.

    Args:
        file_path: Path to a QOI file.

    Returns:
        True if avg green > avg red and avg green > avg blue. False otherwise.
    """
    avg_r, avg_g, avg_b = qoi_avg_rgb(file_path)
    return avg_g > avg_r and avg_g > avg_b


def qoi_row_count(file_path: str | Path) -> int:
    """Return the number of rows (height) in the QOI image."""
    img = parse_qoi_strict(file_path)
    return img.height


def qoi_is_square(file_path: str | Path) -> bool:
    """Return True if the QOI image width equals its height."""
    img = parse_qoi_strict(file_path)
    return img.width == img.height


def qoi_perimeter(file_path: str | Path) -> int:
    """Return the image perimeter in pixels: 2 * (width + height)."""
    img = parse_qoi_strict(file_path)
    return 2 * (img.width + img.height)


def qoi_color_variance(file_path: str | Path) -> float:
    """Return the variance of average RGB values across all pixels."""
    avg_r, avg_g, avg_b = qoi_avg_rgb(file_path)
    mean = (avg_r + avg_g + avg_b) / 3
    return ((avg_r - mean) ** 2 + (avg_g - mean) ** 2 + (avg_b - mean) ** 2) / 3


def qoi_dimension_ratio(file_path: str | Path) -> float:
    """Return width / height ratio. 0.0 if height is 0."""
    img = parse_qoi_strict(file_path)
    if img.height == 0:
        return 0.0
    return img.width / img.height


def qoi_is_landscape(file_path: str | Path) -> bool:
    """Return True if the image is wider than it is tall."""
    img = parse_qoi_strict(file_path)
    return img.width > img.height


def qoi_is_portrait(file_path: str | Path) -> bool:
    """Return True if the image is taller than it is wide."""
    img = parse_qoi_strict(file_path)
    return img.height > img.width


def qoi_max_dimension(file_path: str | Path) -> int:
    """Return the larger of width and height."""
    img = parse_qoi_strict(file_path)
    return max(img.width, img.height)


def qoi_has_any_black(file_path: str | Path) -> bool:
    """Return True if any pixel has R=0, G=0, B=0."""
    img = parse_qoi_strict(file_path)
    return any(p[0] == 0 and p[1] == 0 and p[2] == 0 for p in img.pixels)


def qoi_max_channel_average(file_path: str | Path) -> float:
    """Return the maximum of the per-channel averages (R, G, B)."""
    img = parse_qoi_strict(file_path)
    if not img.pixels:
        return 0.0
    n = len(img.pixels)
    avg_r = sum(p[0] for p in img.pixels) / n
    avg_g = sum(p[1] for p in img.pixels) / n
    avg_b = sum(p[2] for p in img.pixels) / n
    return max(avg_r, avg_g, avg_b)


def qoi_min_channel_average(file_path: str | Path) -> float:
    """Return the minimum of the per-channel averages (R, G, B)."""
    img = parse_qoi_strict(file_path)
    if not img.pixels:
        return 0.0
    n = len(img.pixels)
    avg_r = sum(p[0] for p in img.pixels) / n
    avg_g = sum(p[1] for p in img.pixels) / n
    avg_b = sum(p[2] for p in img.pixels) / n
    return min(avg_r, avg_g, avg_b)


def qoi_has_any_white(file_path: str | Path) -> bool:
    """Return True if any pixel has R=255, G=255, B=255."""
    img = parse_qoi_strict(file_path)
    return any(p[0] == 255 and p[1] == 255 and p[2] == 255 for p in img.pixels)


def qoi_channel_range(file_path: str | Path) -> float:
    """Return the range between the max and min per-channel averages."""
    return qoi_max_channel_average(file_path) - qoi_min_channel_average(file_path)


def qoi_diagonal(file_path: str | Path) -> float:
    """Return the diagonal length of the image: sqrt(width^2 + height^2)."""
    import math
    img = parse_qoi_strict(file_path)
    return math.sqrt(img.width ** 2 + img.height ** 2)


def qoi_min_dimension(file_path: str | Path) -> int:
    """Return the smaller of width and height."""
    img = parse_qoi_strict(file_path)
    return min(img.width, img.height)


def qoi_area(file_path: str | Path) -> int:
    """Return the area of the image: width * height."""
    img = parse_qoi_strict(file_path)
    return img.width * img.height


def qoi_brightness_range(file_path: str | Path) -> int:
    """Return the difference between max and min average brightness per pixel."""
    img = parse_qoi_strict(file_path)
    if not img.pixels:
        return 0
    brightness = [(p[0] + p[1] + p[2]) // 3 for p in img.pixels]
    return max(brightness) - min(brightness)


def qoi_is_small(file_path: str | Path) -> bool:
    """Return True if the image area is less than 1024 pixels."""
    img = parse_qoi_strict(file_path)
    return img.width * img.height < 1024


def qoi_megapixels(file_path: str | Path) -> float:
    """Return the image size in megapixels."""
    img = parse_qoi_strict(file_path)
    return (img.width * img.height) / 1_000_000


def qoi_channel_balance(file_path: str | Path) -> float:
    """Return 1.0 - (max_avg - min_avg)/255. Higher = more balanced channels."""
    img = parse_qoi_strict(file_path)
    if not img.pixels:
        return 1.0
    r_avg = sum(p[0] for p in img.pixels) / len(img.pixels)
    g_avg = sum(p[1] for p in img.pixels) / len(img.pixels)
    b_avg = sum(p[2] for p in img.pixels) / len(img.pixels)
    spread = max(r_avg, g_avg, b_avg) - min(r_avg, g_avg, b_avg)
    return 1.0 - (spread / 255.0)


def qoi_is_tall(file_path: str | Path) -> bool:
    """Return True if height > 2 * width (very tall portrait)."""
    img = parse_qoi_strict(file_path)
    return img.height > 2 * img.width


def qoi_channel_entropy(file_path: str | Path) -> float:
    """Return simple channel diversity: unique RGB tuples / total pixels. 0.0 if no pixels."""
    img = parse_qoi_strict(file_path)
    if not img.pixels:
        return 0.0
    unique = len(set((p[0], p[1], p[2]) for p in img.pixels))
    return unique / len(img.pixels)


def qoi_is_monochrome(file_path: str | Path) -> bool:
    """Return True if all pixels share the same RGB values (single color image)."""
    img = parse_qoi_strict(file_path)
    if not img.pixels:
        return True
    first = (img.pixels[0][0], img.pixels[0][1], img.pixels[0][2])
    return all((p[0], p[1], p[2]) == first for p in img.pixels)


def qoi_red_ratio(file_path: str | Path) -> float:
    """Return ratio of average red channel to total average (R+G+B). 0.0 if all channels zero."""
    img = parse_qoi_strict(file_path)
    if not img.pixels:
        return 0.0
    r_avg = sum(p[0] for p in img.pixels) / len(img.pixels)
    g_avg = sum(p[1] for p in img.pixels) / len(img.pixels)
    b_avg = sum(p[2] for p in img.pixels) / len(img.pixels)
    total = r_avg + g_avg + b_avg
    if total == 0:
        return 0.0
    return r_avg / total


def qoi_green_ratio(file_path: str | Path) -> float:
    """Return ratio of average green channel to total average (R+G+B). 0.0 if all channels zero."""
    img = parse_qoi_strict(file_path)
    if not img.pixels:
        return 0.0
    r_avg = sum(p[0] for p in img.pixels) / len(img.pixels)
    g_avg = sum(p[1] for p in img.pixels) / len(img.pixels)
    b_avg = sum(p[2] for p in img.pixels) / len(img.pixels)
    total = r_avg + g_avg + b_avg
    if total == 0:
        return 0.0
    return g_avg / total


def qoi_blue_ratio(file_path: str | Path) -> float:
    """Return ratio of average blue channel to total average (R+G+B). 0.0 if all channels zero."""
    img = parse_qoi_strict(file_path)
    if not img.pixels:
        return 0.0
    r_avg = sum(p[0] for p in img.pixels) / len(img.pixels)
    g_avg = sum(p[1] for p in img.pixels) / len(img.pixels)
    b_avg = sum(p[2] for p in img.pixels) / len(img.pixels)
    total = r_avg + g_avg + b_avg
    if total == 0:
        return 0.0
    return b_avg / total


def qoi_pixel_density(file_path: str | Path) -> float:
    """Return pixels per byte of file size. 0.0 if file_size is 0."""
    img = parse_qoi_strict(file_path)
    fsize = Path(file_path).stat().st_size
    if fsize == 0:
        return 0.0
    return (img.width * img.height) / fsize


def qoi_is_dark(file_path: str | Path) -> bool:
    """Return True if average brightness is below 50% of max (128 for 8-bit)."""
    img = parse_qoi_strict(file_path)
    if not img.pixels:
        return False
    avg = sum(p[0] + p[1] + p[2] for p in img.pixels) / (len(img.pixels) * 3)
    return avg < 128


def qoi_color_depth_estimate(file_path: str | Path) -> float:
    """Return log2 of unique color count (approx bits of color depth). 0.0 if no pixels."""
    import math
    img = parse_qoi_strict(file_path)
    if not img.pixels:
        return 0.0
    unique = len(set(img.pixels))
    if unique <= 1:
        return 0.0
    return math.log2(unique)


def qoi_is_bright(file_path: str | Path) -> bool:
    """Return True if average brightness is above 50% of max (128 for 8-bit)."""
    img = parse_qoi_strict(file_path)
    if not img.pixels:
        return False
    avg = sum(p[0] + p[1] + p[2] for p in img.pixels) / (len(img.pixels) * 3)
    return avg >= 128


def qoi_saturation_estimate(file_path: str | Path) -> float:
    """Return average saturation estimate (max_channel - min_channel) / 255. 0.0 if no pixels."""
    img = parse_qoi_strict(file_path)
    if not img.pixels:
        return 0.0
    total = 0.0
    for p in img.pixels:
        channels = p[:3]
        total += (max(channels) - min(channels)) / 255.0
    return total / len(img.pixels)


def qoi_pixel_contrast(file_path: str | Path) -> float:
    """Return brightness range (max - min) as a ratio of 255. 0.0 if no pixels."""
    img = parse_qoi_strict(file_path)
    if not img.pixels:
        return 0.0
    brightnesses = [(p[0] + p[1] + p[2]) / 3.0 for p in img.pixels]
    return (max(brightnesses) - min(brightnesses)) / 255.0


def qoi_max_brightness(file_path: str | Path) -> float:
    """Return maximum pixel brightness ((R+G+B)/3) across all pixels. 0.0 if no pixels."""
    img = parse_qoi_strict(file_path)
    if not img.pixels:
        return 0.0
    return max((p[0] + p[1] + p[2]) / 3.0 for p in img.pixels)


def qoi_total_rgb_sum(file_path: str | Path) -> int:
    """Return sum of all R+G+B channel values across all pixels. 0 if no pixels."""
    img = parse_qoi_strict(file_path)
    return sum(p[0] + p[1] + p[2] for p in img.pixels)


def qoi_channel_variance(file_path: str | Path) -> float:
    """Return variance of average R, G, B channel values. 0.0 if no pixels."""
    img = parse_qoi_strict(file_path)
    if not img.pixels:
        return 0.0
    n = len(img.pixels)
    avg_r = sum(p[0] for p in img.pixels) / n
    avg_g = sum(p[1] for p in img.pixels) / n
    avg_b = sum(p[2] for p in img.pixels) / n
    mean = (avg_r + avg_g + avg_b) / 3.0
    return ((avg_r - mean) ** 2 + (avg_g - mean) ** 2 + (avg_b - mean) ** 2) / 3.0


def qoi_red_blue_ratio(file_path: str | Path) -> float:
    """Return ratio of red channel sum to blue channel sum. 0.0 if blue is zero."""
    img = parse_qoi_strict(file_path)
    if not img.pixels:
        return 0.0
    red = sum(p[0] for p in img.pixels)
    blue = sum(p[2] for p in img.pixels)
    if blue == 0:
        return 0.0
    return red / blue


def qoi_normalized_brightness(file_path: str | Path) -> float:
    """Return mean brightness normalized to [0.0, 1.0] (divides by 255). 0.0 if no pixels."""
    img = parse_qoi_strict(file_path)
    if not img.pixels:
        return 0.0
    mean = sum((p[0] + p[1] + p[2]) / 3.0 for p in img.pixels) / len(img.pixels)
    return mean / 255.0


def qoi_min_brightness(file_path: str | Path) -> float:
    """Return minimum per-pixel brightness (mean of R, G, B channels). 0.0 if no pixels."""
    img = parse_qoi_strict(file_path)
    if not img.pixels:
        return 0.0
    return min((p[0] + p[1] + p[2]) / 3.0 for p in img.pixels)


def qoi_above_mean_ratio(file_path: str | Path) -> float:
    """Return ratio of pixels with brightness strictly above the mean. 0.0 if no pixels."""
    img = parse_qoi_strict(file_path)
    if not img.pixels:
        return 0.0
    brightnesses = [(p[0] + p[1] + p[2]) / 3.0 for p in img.pixels]
    mean = sum(brightnesses) / len(brightnesses)
    above = sum(1 for b in brightnesses if b > mean)
    return above / len(brightnesses)


def qoi_green_blue_ratio(file_path: str | Path) -> float:
    """Return ratio of green channel sum to blue channel sum. 0.0 if blue is zero."""
    img = parse_qoi_strict(file_path)
    if not img.pixels:
        return 0.0
    green = sum(p[1] for p in img.pixels)
    blue = sum(p[2] for p in img.pixels)
    if blue == 0:
        return 0.0
    return green / blue


def qoi_is_wide(file_path: str | Path) -> bool:
    """Return True if image width is more than twice its height."""
    img = parse_qoi_strict(file_path)
    return img.width > 2 * img.height
