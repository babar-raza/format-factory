"""
xcf_layer_iterator.py — Spec-shaped layer iteration for XCF documents.

Authority: GIMP XCF file format — layer record.
Spec QName: xcf:layer (urn:format:gimp:xcf:1.0)
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterator

from .xcf_parser import parse_xcf_strict
from .spec.layer.layer import Layer


def xcf_iter_layers(source: "str | Path") -> Iterator[Layer]:
    """Yield spec-shaped Layer objects for every layer in an XCF document.

    Args:
        source: Path to a .xcf GIMP drawing file.

    Yields:
        Layer instances (spec class: xcf:layer, SAL-XCF-00002).
    """
    img = parse_xcf_strict(str(Path(source).resolve()))
    layer_names = img.layer_names or []
    for name in layer_names:
        yield Layer({
            "name": name,
            "width": img.width,
            "height": img.height,
            "type": img.image_type,
            "visible": True,
        })
