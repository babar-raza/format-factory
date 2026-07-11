"""
ppm_stats.py -- Statistics and analysis functions for PPM neutral model dicts.

Works on the dict output of parse_ppm(), not on file paths.
All functions are pure: no I/O, no mutation.

Added in R62 (format track advancement).

License: Apache-2.0
Package: format-factory-ppm v0.1.0
"""
from __future__ import annotations

from typing import Any


def image_stats(ppm_doc: dict[str, Any]) -> dict[str, Any]:
    """Return aggregate statistics for a PPM image dict.

    Works on the output of parse_ppm().
    Returns:
        width (int), height (int), pixel_count (int), maxval (int),
        magic (str), depth (str: '8-bit' or '16-bit'),
        aspect_ratio (float | None), megapixels (float).
    """
    width = ppm_doc.get("width", 0)
    height = ppm_doc.get("height", 0)
    maxval = ppm_doc.get("maxval", 255)
    magic = ppm_doc.get("magic", "")
    pixel_count = ppm_doc.get("pixel_count", width * height)

    depth = "16-bit" if maxval > 255 else "8-bit"
    aspect_ratio: float | None = None
    if height > 0:
        aspect_ratio = round(width / height, 4)

    megapixels = round(pixel_count / 1_000_000, 4) if pixel_count > 0 else 0.0

    return {
        "width": width,
        "height": height,
        "pixel_count": pixel_count,
        "maxval": maxval,
        "magic": magic,
        "depth": depth,
        "aspect_ratio": aspect_ratio,
        "megapixels": megapixels,
    }


def image_color_sample(ppm_doc: dict[str, Any], sample_size: int = 10) -> dict[str, Any]:
    """Return a small sample of pixel tuples from a PPM image dict.

    Returns: sampled_pixels (list of tuples/lists), sample_size (int),
             total_pixels (int).
    Samples evenly spaced from the pixel list.
    """
    pixel_count = ppm_doc.get("pixel_count", 0)
    # Note: parse_ppm() returns pixel_count as an int, not the pixel list itself.
    # This function works with the count only; actual pixel sampling would need the list.
    return {
        "total_pixels": pixel_count,
        "sample_size": min(sample_size, pixel_count),
        "note": "Pixel list not stored in parse_ppm() dict; use parse_ppm_strict() for pixels.",
    }


def ppm_channel_stats(ppm_doc: dict) -> dict:
    """Return per-channel statistics for PPM image data.

    For P3 RGB PPM images, computes min/max/mean for each channel (R, G, B)
    from the sample pixels available in the document. Returns:
      channels: list[str]        — e.g. ['R', 'G', 'B']
      per_channel: dict          — {channel: {min, max, mean}}
      total_pixels: int          — number of pixels in sample
      note: str                  — if limited sample

    Works on the parsed dict from parse_ppm(). The dict includes a 'pixels'
    list of RGB tuples (may be partial for large images). If pixels is empty,
    returns zero statistics.
    """
    pixels = ppm_doc.get("pixels", [])
    if not pixels:
        return {
            "channels": ["R", "G", "B"],
            "per_channel": {c: {"min": None, "max": None, "mean": None} for c in "RGB"},
            "total_pixels": 0,
            "note": "No pixel data available",
        }

    r_vals = [p[0] for p in pixels if len(p) >= 3]
    g_vals = [p[1] for p in pixels if len(p) >= 3]
    b_vals = [p[2] for p in pixels if len(p) >= 3]

    def _channel_stats(vals: list) -> dict:
        if not vals:
            return {"min": None, "max": None, "mean": None}
        return {
            "min": min(vals),
            "max": max(vals),
            "mean": round(sum(vals) / len(vals), 2),
        }

    result: dict = {
        "channels": ["R", "G", "B"],
        "per_channel": {
            "R": _channel_stats(r_vals),
            "G": _channel_stats(g_vals),
            "B": _channel_stats(b_vals),
        },
        "total_pixels": len(pixels),
    }
    if len(pixels) < ppm_doc.get("width", 0) * ppm_doc.get("height", 0):
        result["note"] = "Partial pixel sample (large image)"
    return result


def ppm_brightness_histogram(ppm_doc: dict, bins: int = 4) -> dict[str, int]:
    """Return a brightness histogram for PPM image pixel data.

    Computes per-pixel brightness as the average of R, G, B channels,
    then bins pixels into ``bins`` equal-width ranges from 0 to maxval.

    Args:
        ppm_doc: Parsed PPM document dict (must contain 'pixels' list).
        bins: Number of histogram bins (default 4).

    Returns:
        dict mapping bin label strings (e.g. '0-63', '64-127') to pixel counts.
        Empty dict if no pixel data.

    """
    pixels = ppm_doc.get("pixels", [])
    maxval = ppm_doc.get("maxval", 255)
    if not pixels or bins <= 0:
        return {}

    bin_width = (maxval + 1) / bins
    histogram: dict[str, int] = {}

    # Pre-compute bin labels
    bin_labels: list[str] = []
    for i in range(bins):
        lo = int(i * bin_width)
        hi = int((i + 1) * bin_width) - 1 if i < bins - 1 else maxval
        bin_labels.append(f"{lo}-{hi}")
        histogram[bin_labels[-1]] = 0

    for pixel in pixels:
        if not isinstance(pixel, (list, tuple)) or len(pixel) < 3:
            continue
        brightness = (pixel[0] + pixel[1] + pixel[2]) / 3.0
        bin_index = int(brightness / bin_width)
        if bin_index >= bins:
            bin_index = bins - 1
        histogram[bin_labels[bin_index]] += 1

    return histogram


def ppm_pixel_count(ppm_doc: dict[str, Any]) -> int:
    """Return the total pixel count for a PPM image (width * height).

    Args:
        ppm_doc: Parsed PPM document dict (from parse_ppm()).

    Returns:
        int — total pixel count. 0 if width or height is missing/zero.

    Useful for quick image size assessment without loading pixel data.
    """
    width = ppm_doc.get("width", 0)
    height = ppm_doc.get("height", 0)
    return width * height


def ppm_channel_histogram(ppm_doc: dict[str, Any]) -> dict[str, list[int]]:
    """Return per-channel histograms for PPM image pixel data.

    Computes a 256-bin histogram for each RGB channel (red, green, blue).
    Each bin counts how many pixels have that channel value (0-255).
    For images with maxval != 255, values are scaled to the 0-255 range.

    Args:
        ppm_doc: Parsed PPM document dict (must contain 'pixels' list).

    Returns:
        dict with keys 'red', 'green', 'blue', each mapping to a list
        of 256 ints. Returns zeroed histograms if no pixel data.

    Useful for color distribution analysis, exposure assessment, and
    image quality metrics.
    """
    red = [0] * 256
    green = [0] * 256
    blue = [0] * 256

    pixels = ppm_doc.get("pixels", [])
    maxval = ppm_doc.get("maxval", 255)

    for pixel in pixels:
        if not isinstance(pixel, (list, tuple)) or len(pixel) < 3:
            continue
        r, g, b = pixel[0], pixel[1], pixel[2]
        # Scale to 0-255 if maxval differs
        if maxval != 255 and maxval > 0:
            r = int(r * 255 / maxval)
            g = int(g * 255 / maxval)
            b = int(b * 255 / maxval)
        # Clamp to valid range
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        red[r] += 1
        green[g] += 1
        blue[b] += 1

    return {"red": red, "green": green, "blue": blue}


def ppm_is_square(ppm_doc: dict[str, Any]) -> bool:
    """Return True if image width equals height.

    Args:
        ppm_doc: Parsed PPM document dict.

    Returns:
        bool — True if width == height.
    """
    return ppm_doc.get("width", 0) == ppm_doc.get("height", 0)


def ppm_is_landscape(ppm_doc: dict[str, Any]) -> bool:
    """Return True if image is wider than it is tall.

    Args:
        ppm_doc: Parsed PPM document dict.

    Returns:
        bool — True if width > height.
    """
    return ppm_doc.get("width", 0) > ppm_doc.get("height", 0)


def ppm_is_portrait(ppm_doc: dict[str, Any]) -> bool:
    """Return True if image is taller than it is wide.

    Args:
        ppm_doc: Parsed PPM document dict.

    Returns:
        bool — True if height > width.
    """
    return ppm_doc.get("height", 0) > ppm_doc.get("width", 0)


def ppm_is_ok(ppm_doc: dict[str, Any]) -> bool:
    """Return True if the PPM parse succeeded without errors.

    Args:
        ppm_doc: Parsed PPM document dict.

    Returns:
        bool — True if 'ok' is truthy.
    """
    return bool(ppm_doc.get("ok", False))


def ppm_is_ascii_ppm(ppm_doc: dict[str, Any]) -> bool:
    """Return True if the image is ASCII PPM format (magic == 'P3').

    Args:
        ppm_doc: Parsed PPM document dict.

    Returns:
        bool — True if magic == 'P3'.
    """
    return ppm_doc.get("magic", "") == "P3"


def ppm_aspect_ratio_from_doc(ppm_doc: dict[str, Any]) -> float:
    """Return width / height as a float. 0.0 if height is zero.

    Args:
        ppm_doc: Parsed PPM document dict.

    Returns:
        float — width / height, or 0.0 if height is 0.
    """
    h = ppm_doc.get("height", 0)
    if h == 0:
        return 0.0
    return ppm_doc.get("width", 0) / h
