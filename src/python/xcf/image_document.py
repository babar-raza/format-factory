"""
XCF Image Document — spec-level domain module.

Implements image-level predicates and metrics for the XCF (GIMP Native Image) format.

Spec authority : GIMP XCF 2.10 File Format Specification
QName         : xcf:image
Namespace URI : urn:format:xcf:2.10
Spec fact ref : FACT-XCF-001

Functions in this module derive directly from the XCF image-level structure:
- xcf:image root element (width, height, image type, layer count, pixel data)
- Behavioral predicates derived from parsed image header fields

This is a behavioral implementation module, NOT an architecture_only spec stub.
The corresponding spec stubs are under src/python/xcf/spec/.
"""
from __future__ import annotations

from pathlib import Path

from .xcf_parser import parse_xcf_strict

spec_qname = "xcf:image"
spec_fact_ref = "FACT-XCF-001"
namespace_uri = "urn:format:xcf:2.10"


class XcfImageSpec:
    """Spec authority class for xcf:image.

    spec_qname: xcf:image
    Spec fact ref: FACT-XCF-001
    Namespace URI: urn:format:xcf:2.10
    Source layer: Spec
    """

    spec_qname = "xcf:image"
    spec_fact_ref = "FACT-XCF-001"
    namespace_uri = "urn:format:xcf:2.10"


def xcf_is_landscape(file_path: "str | Path") -> bool:
    """Return True if the image width is strictly greater than its height.

    Spec: XCF image header — width and height fields (FACT-XCF-001).
    Orientation is derived from the xcf:image root-level width/height values.
    """
    img = parse_xcf_strict(file_path)
    return img.width > img.height
