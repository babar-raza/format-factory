"""
PGM image analytics — file-path based image analytics.

Extends grayscale_image.py with additional analytics.
Uses parse_pgm_strict from pgm_parser.
"""
from __future__ import annotations

from pathlib import Path

from .pgm_parser import parse_pgm_strict

spec_qname = "pgm:image"
spec_fact_ref = "FACT-PGM-001"


def pgm_width(file_path: "str | Path") -> int:
    """Return the width (number of columns) of the PGM image.

    Spec: Netpbm PGM header width field (FACT-PGM-001)
    """
    img = parse_pgm_strict(file_path)
    return img.width


def pgm_height(file_path: "str | Path") -> int:
    """Return the height (number of rows) of the PGM image.

    Spec: Netpbm PGM header height field (FACT-PGM-001)
    """
    img = parse_pgm_strict(file_path)
    return img.height


def pgm_maxval(file_path: "str | Path") -> int:
    """Return the maximum gray value (maxval) declared in the PGM header.

    Spec: Netpbm PGM header maxval field (FACT-PGM-001)
    """
    img = parse_pgm_strict(file_path)
    return img.maxval


def pgm_magic(file_path: "str | Path") -> str:
    """Return the magic number of the PGM file ('P2' ASCII or 'P5' binary).

    Spec: Netpbm PGM magic number (FACT-PGM-001)
    """
    img = parse_pgm_strict(file_path)
    return img.magic


def pgm_is_single_pixel(file_path: "str | Path") -> bool:
    """Return True if the PGM image is exactly 1×1 pixels.

    Spec: Netpbm PGM width/height fields (FACT-PGM-001)
    """
    img = parse_pgm_strict(file_path)
    return img.width == 1 and img.height == 1


def pgm_is_full_range(file_path: "str | Path") -> bool:
    """Return True if the image uses the full 0–maxval dynamic range.

    True when min(pixels) == 0 and max(pixels) == maxval.

    Spec: Netpbm PGM pixel range (FACT-PGM-001)
    """
    img = parse_pgm_strict(file_path)
    if not img.pixels:
        return False
    return min(img.pixels) == 0 and max(img.pixels) == img.maxval


def pgm_total_pixels(file_path: "str | Path") -> int:
    """Return total pixel count (width * height).

    Spec: Netpbm PGM width/height fields (FACT-PGM-001)
    """
    img = parse_pgm_strict(file_path)
    return img.width * img.height


def pgm_is_square(file_path: "str | Path") -> bool:
    """Return True if image width equals height.

    Spec: Netpbm PGM width/height fields (FACT-PGM-001)
    """
    img = parse_pgm_strict(file_path)
    return img.width == img.height


def pgm_is_landscape(file_path: "str | Path") -> bool:
    """Return True if the image is wider than it is tall.

    Spec: Netpbm PGM width/height fields (FACT-PGM-001)
    """
    img = parse_pgm_strict(file_path)
    return img.width > img.height


def pgm_aspect_ratio(file_path: "str | Path") -> float:
    """Return width / height as a float. 0.0 if height is zero.

    Spec: Netpbm PGM width/height fields (FACT-PGM-001)
    """
    img = parse_pgm_strict(file_path)
    if img.height == 0:
        return 0.0
    return img.width / img.height


def pgm_min_pixel_value(file_path: "str | Path") -> int:
    """Return the minimum pixel value in the image. 0 if no pixels.

    Spec: Netpbm PGM pixel data (FACT-PGM-001)
    """
    img = parse_pgm_strict(file_path)
    return min(img.pixels) if img.pixels else 0


def pgm_max_pixel_value(file_path: "str | Path") -> int:
    """Return the maximum pixel value in the image. 0 if no pixels.

    Spec: Netpbm PGM pixel data (FACT-PGM-001)
    """
    img = parse_pgm_strict(file_path)
    return max(img.pixels) if img.pixels else 0
