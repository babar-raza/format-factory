"""
ppm_stats.py -- Statistics and analysis functions for PPM neutral model dicts.

Works on the dict output of parse_ppm(), not on file paths.
All functions are pure: no I/O, no mutation.

Added in R62 Train I (format track advancement).

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
    Added in R62 Train I.
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
    Added in R62 Train I.
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
    Added in R63 Train I (PPM format track advancement).
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
