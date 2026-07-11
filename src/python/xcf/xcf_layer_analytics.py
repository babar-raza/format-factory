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


def xcf_num_layers(source: "str | Path") -> int:
    """Return the number of layers in the XCF image.

    Spec: XCF image layer count (FACT-XCF-001)
    """
    img = parse_xcf_strict(source)
    return img.num_layers


def xcf_local_name(source: "str | Path") -> str:
    """Return the local element name for the XCF image object.

    Spec: XCF image namespace (FACT-XCF-001)
    """
    img = parse_xcf_strict(source)
    return img.local_name


def xcf_namespace_uri(source: "str | Path") -> str:
    """Return the namespace URI for the XCF format.

    Spec: XCF image namespace (FACT-XCF-001)
    """
    img = parse_xcf_strict(source)
    return img.namespace_uri


def xcf_layer_names_sorted(source: "str | Path") -> list:
    """Return alphabetically sorted list of layer names.

    Spec: XCF image layer (FACT-XCF-001)
    """
    img = parse_xcf_strict(source)
    return sorted(img.layer_names)


def xcf_has_named_layers(source: "str | Path") -> bool:
    """Return True if the image has at least one layer with a non-empty name.

    Spec: XCF image layer (FACT-XCF-001)
    """
    img = parse_xcf_strict(source)
    return any(name.strip() for name in img.layer_names)


def xcf_all_layers_named(source: "str | Path") -> bool:
    """Return True if every layer has a non-empty, non-whitespace name.

    True vacuously when there are no layers.

    Spec: XCF image layer (FACT-XCF-001)
    """
    img = parse_xcf_strict(source)
    return all(name.strip() for name in img.layer_names)


def xcf_width(source: "str | Path") -> int:
    """Return image width in pixels.

    Spec: XCF image header width (FACT-XCF-001)
    """
    img = parse_xcf_strict(source)
    return img.width


def xcf_height(source: "str | Path") -> int:
    """Return image height in pixels.

    Spec: XCF image header height (FACT-XCF-001)
    """
    img = parse_xcf_strict(source)
    return img.height


def xcf_image_type(source: "str | Path") -> int:
    """Return image type integer (0=RGB, 1=Grayscale, 2=Indexed).

    Spec: XCF image header image_type (FACT-XCF-001)
    """
    img = parse_xcf_strict(source)
    return img.image_type


def xcf_is_landscape(source: "str | Path") -> bool:
    """Return True if the image is wider than it is tall.

    Spec: XCF image header width/height (FACT-XCF-001)
    """
    img = parse_xcf_strict(source)
    return img.width > img.height


def xcf_aspect_ratio(source: "str | Path") -> float:
    """Return width / height as a float. 0.0 if height is zero.

    Spec: XCF image header width/height (FACT-XCF-001)
    """
    img = parse_xcf_strict(source)
    if img.height == 0:
        return 0.0
    return img.width / img.height


def xcf_first_layer_name(source: "str | Path") -> str:
    """Return the name of the first layer. Empty string if no layers.

    Spec: XCF image layer (FACT-XCF-001)
    """
    img = parse_xcf_strict(source)
    names = list(img.layer_names)
    return names[0] if names else ""
