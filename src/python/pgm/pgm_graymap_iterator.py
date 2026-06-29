"""
pgm_graymap_iterator.py — Spec-shaped graymap iteration for PGM documents.

Authority: Netpbm format — PGM (Portable Graymap) pixel data.
Spec QName: pgm:graymap (urn:format:netpbm:pgm:1.0)
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterator

from .pgm_parser import parse_pgm_strict
from .spec.graymap.graymap import Graymap


def pgm_iter_graymaps(source: "str | Path") -> Iterator[Graymap]:
    """Yield a spec-shaped Graymap object for the image in a PGM document.

    Each PGM file contains exactly one graymap (the full grayscale image).

    Args:
        source: Path to a .pgm Portable Graymap file.

    Yields:
        Graymap instances (spec class: pgm:graymap, FACT-PGM-002).
    """
    img = parse_pgm_strict(str(Path(source).resolve()))
    width = img.width
    height = img.height
    pixels = list(img.pixels)
    rows = [pixels[i * width:(i + 1) * width] for i in range(height)]
    yield Graymap({"width": width, "height": height, "rows": rows, "maxval": getattr(img, "maxval", 255)})
