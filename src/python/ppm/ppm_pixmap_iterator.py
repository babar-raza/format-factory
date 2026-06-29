"""
ppm_pixmap_iterator.py — Spec-shaped pixmap iteration for PPM documents.

Authority: Netpbm format — PPM (Portable Pixmap) RGB pixel data.
Spec QName: ppm:pixmap (urn:format:netpbm:ppm:1.0)
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterator

from .ppm_parser import parse_ppm_strict
from .spec.pixmap.pixmap import Pixmap


def ppm_iter_pixmaps(source: "str | Path") -> Iterator[Pixmap]:
    """Yield a spec-shaped Pixmap object for the image in a PPM document.

    Each PPM file contains exactly one pixmap (the full RGB color image).

    Args:
        source: Path to a .ppm Portable Pixmap file.

    Yields:
        Pixmap instances (spec class: ppm:pixmap, FACT-PPM-002).
    """
    img = parse_ppm_strict(str(Path(source).resolve()))
    width = img.width
    height = img.height
    pixels = list(img.pixels)
    rows = [pixels[i * width:(i + 1) * width] for i in range(height)]
    yield Pixmap({"width": width, "height": height, "rows": rows, "maxval": getattr(img, "maxval", 255)})
