"""
ppm_image_analytics.py -- Additional file-path analytics for PPM (Portable Pixmap) images.

Extends color_image.py with 6 new predicates that do not overlap with existing
functions: single-pixel/row/column detection, bit-depth check, and all-white/all-black tests.

License: Apache-2.0
Package: format-factory-ppm v0.1.0
"""
from __future__ import annotations

from pathlib import Path


def _load_ppm(file_path: "str | Path"):
    """Return PpmImage from parse_ppm_strict."""
    from .ppm_parser import parse_ppm_strict
    return parse_ppm_strict(file_path)


def ppm_has_single_pixel(file_path: "str | Path") -> bool:
    """Return True if the image contains exactly one pixel (width == height == 1).

    Args:
        file_path: Path to the .ppm file.

    Returns:
        bool — True if width == 1 and height == 1.
    """
    img = _load_ppm(file_path)
    return img.width == 1 and img.height == 1


def ppm_has_single_row(file_path: "str | Path") -> bool:
    """Return True if the image has exactly one row (height == 1).

    Args:
        file_path: Path to the .ppm file.

    Returns:
        bool — True if height == 1.
    """
    img = _load_ppm(file_path)
    return img.height == 1


def ppm_has_single_column(file_path: "str | Path") -> bool:
    """Return True if the image has exactly one column (width == 1).

    Args:
        file_path: Path to the .ppm file.

    Returns:
        bool — True if width == 1.
    """
    img = _load_ppm(file_path)
    return img.width == 1


def ppm_is_high_depth(file_path: "str | Path") -> bool:
    """Return True if the image uses more than 8 bits per channel (maxval > 255).

    Standard 8-bit PPM uses maxval == 255. A maxval > 255 indicates a 16-bit
    (or higher) image, typically written with 2-byte samples.

    Args:
        file_path: Path to the .ppm file.

    Returns:
        bool — True if maxval > 255.
    """
    img = _load_ppm(file_path)
    return img.maxval > 255


def ppm_all_white(file_path: "str | Path") -> bool:
    """Return True if every pixel is pure white (all channels equal maxval).

    Differs from ppm_has_pure_white which returns True when ANY pixel is white.
    This function requires ALL pixels to be white.

    Args:
        file_path: Path to the .ppm file.

    Returns:
        bool — True if every pixel is (maxval, maxval, maxval).
    """
    img = _load_ppm(file_path)
    maxval = img.maxval
    return all(r == maxval and g == maxval and b == maxval for r, g, b in img.pixels)


def ppm_all_black(file_path: "str | Path") -> bool:
    """Return True if every pixel is pure black (all channels equal zero).

    Differs from ppm_has_pure_black which returns True when ANY pixel is black.
    This function requires ALL pixels to be (0, 0, 0).

    Args:
        file_path: Path to the .ppm file.

    Returns:
        bool — True if every pixel is (0, 0, 0).
    """
    img = _load_ppm(file_path)
    return all(r == 0 and g == 0 and b == 0 for r, g, b in img.pixels)
