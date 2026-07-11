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


def qoi_channels(source: "str | Path") -> int:
    """Return the channel count from the QOI header (3=RGB, 4=RGBA).

    Spec: QOI header channels field (FACT-QOI-001)
    """
    img = parse_qoi_strict(source)
    return img.channels


def qoi_is_single_pixel(source: "str | Path") -> bool:
    """Return True if the image is exactly 1x1 pixel.

    Spec: QOI header width/height fields (FACT-QOI-001)
    """
    img = parse_qoi_strict(source)
    return img.width == 1 and img.height == 1


def qoi_aspect_ratio(source: "str | Path") -> float:
    """Return width / height as a float. 0.0 if height is 0.

    Spec: QOI header width/height fields (FACT-QOI-001)
    """
    img = parse_qoi_strict(source)
    if img.height == 0:
        return 0.0
    return img.width / img.height


def qoi_is_opaque(source: "str | Path") -> bool:
    """Return True if all alpha channel values are 255 (fully opaque).

    For RGB images (3 channels) this always returns True.

    Spec: QOI pixel data alpha channel (FACT-QOI-001)
    """
    img = parse_qoi_strict(source)
    if img.channels == 3:
        return True
    return all(p[3] == 255 for p in img.pixels)


def qoi_unique_pixel_count(source: "str | Path") -> int:
    """Return the count of distinct pixel tuples in the image.

    Spec: QOI pixel data (FACT-QOI-001)
    """
    img = parse_qoi_strict(source)
    return len(set(img.pixels))


def qoi_is_srgb(source: "str | Path") -> bool:
    """Return True if the image uses sRGB colorspace (colorspace == 0).

    Spec: QOI header colorspace field (FACT-QOI-001)
    """
    img = parse_qoi_strict(source)
    return img.colorspace == 0
