"""
XCF layer analytics — file-path based image layer statistics.

Extends xcf_image_metrics.py with additional analytics.
Uses parse_xcf_strict from xcf_parser.
"""
from __future__ import annotations

from pathlib import Path

from .xcf_parser import parse_xcf_strict

spec_qname = "xcf:image"
spec_fact_ref = "FACT-XCF-001"

# XCF image type constants (GIMP XCF spec)
_IMAGE_TYPE_RGB = 0
_IMAGE_TYPE_GRAY = 1
_IMAGE_TYPE_INDEXED = 2


def xcf_is_rgb(source: "str | Path") -> bool:
    """Return True if the XCF image is RGB type (image_type == 0)."""
    img = parse_xcf_strict(source)
    return img.image_type == _IMAGE_TYPE_RGB


def xcf_is_grayscale(source: "str | Path") -> bool:
    """Return True if the XCF image is grayscale type (image_type == 1)."""
    img = parse_xcf_strict(source)
    return img.image_type == _IMAGE_TYPE_GRAY


def xcf_is_square(source: "str | Path") -> bool:
    """Return True if the image width equals its height."""
    img = parse_xcf_strict(source)
    return img.width == img.height


def xcf_total_pixels(source: "str | Path") -> int:
    """Return total pixel count (width * height)."""
    img = parse_xcf_strict(source)
    return img.width * img.height


def xcf_has_single_layer(source: "str | Path") -> bool:
    """Return True if the image has exactly one layer."""
    img = parse_xcf_strict(source)
    return img.num_layers == 1


def xcf_layer_names(source: "str | Path") -> list:
    """Return list of layer names in the XCF image."""
    img = parse_xcf_strict(source)
    return list(img.layer_names)
