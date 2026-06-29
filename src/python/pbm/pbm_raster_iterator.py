"""
pbm_raster_iterator.py — Spec-shaped raster iteration for PBM documents.

Authority: Netpbm format — PBM (Portable Bitmap) raster data.
Spec QName: pbm:raster (urn:format:netpbm:pbm:1.0)
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterator

from .pbm_parser import parse_pbm_strict
from .spec.bitmap.raster import Raster


def pbm_iter_rasters(source: "str | Path") -> Iterator[Raster]:
    """Yield a spec-shaped Raster object for the image in a PBM document.

    Each PBM file contains exactly one raster (the full bitmap image).

    Args:
        source: Path to a .pbm Portable Bitmap file.

    Yields:
        Raster instances (spec class: pbm:raster, FACT-PBM-002).
    """
    img = parse_pbm_strict(str(Path(source).resolve()))
    width = img.width
    height = img.height
    pixels = list(img.pixels)
    rows = [pixels[i * width:(i + 1) * width] for i in range(height)]
    yield Raster({"width": width, "height": height, "rows": rows})
