"""
QOI image analytics — file-path based image statistics.

Extends image_document.py with additional analytics derived from pixel data.
Uses parse_qoi_strict from qoi_parser.
"""
from __future__ import annotations

from pathlib import Path

from .qoi_parser import parse_qoi_strict

spec_qname = "qoi:image"
spec_fact_ref = "FACT-QOI-001"


def qoi_is_landscape(source: "str | Path") -> bool:
    """Return True if the image is wider than it is tall (landscape orientation)."""
    img = parse_qoi_strict(source)
    return img.width > img.height


def qoi_is_portrait(source: "str | Path") -> bool:
    """Return True if the image is taller than it is wide (portrait orientation)."""
    img = parse_qoi_strict(source)
    return img.height > img.width


def qoi_is_square(source: "str | Path") -> bool:
    """Return True if width equals height."""
    img = parse_qoi_strict(source)
    return img.width == img.height


def qoi_has_alpha(source: "str | Path") -> bool:
    """Return True if the image has 4 channels (RGBA), indicating alpha support."""
    img = parse_qoi_strict(source)
    return img.channels == 4


def qoi_total_pixels(source: "str | Path") -> int:
    """Return total pixel count (width * height)."""
    img = parse_qoi_strict(source)
    return img.width * img.height


def qoi_is_monochrome(source: "str | Path") -> bool:
    """Return True if all pixels have equal R, G, B channel values (greyscale image)."""
    img = parse_qoi_strict(source)
    return all(p[0] == p[1] == p[2] for p in img.pixels)


def qoi_width(source: "str | Path") -> int:
    """Return image width in pixels.

    Spec: QOI header width field (FACT-QOI-001)
    """
    img = parse_qoi_strict(source)
    return img.width


def qoi_height(source: "str | Path") -> int:
    """Return image height in pixels.

    Spec: QOI header height field (FACT-QOI-001)
    """
    img = parse_qoi_strict(source)
    return img.height


def qoi_colorspace(source: "str | Path") -> int:
    """Return the colorspace tag from the QOI header.

    0 = sRGB with linear alpha, 1 = all channels linear.

    Spec: QOI header colorspace field (FACT-QOI-001)
    """
    img = parse_qoi_strict(source)
    return img.colorspace


def qoi_is_rgb(source: "str | Path") -> bool:
    """Return True if the image uses 3-channel RGB (no alpha channel).

    Spec: QOI header channels field (FACT-QOI-001)
    """
    img = parse_qoi_strict(source)
    return img.channels == 3


def qoi_min_channel_value(source: "str | Path") -> int:
    """Return the minimum individual channel value across all pixels. 0 if no pixels.

    Spec: QOI pixel data channels (FACT-QOI-001)
    """
    img = parse_qoi_strict(source)
    if not img.pixels:
        return 0
    return min(v for p in img.pixels for v in p)


def qoi_max_channel_value(source: "str | Path") -> int:
    """Return the maximum individual channel value across all pixels. 0 if no pixels.

    Spec: QOI pixel data channels (FACT-QOI-001)
    """
    img = parse_qoi_strict(source)
    if not img.pixels:
        return 0
    return max(v for p in img.pixels for v in p)
