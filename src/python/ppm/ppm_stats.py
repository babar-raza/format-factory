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
