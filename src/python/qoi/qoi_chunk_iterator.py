"""
qoi_chunk_iterator.py — Spec-shaped chunk iteration for QOI documents.

Authority: QOI specification — chunk types (QOI_OP_*).
Spec QName: qoi:chunk (urn:format:qoi:1.0)
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterator

from .qoi_parser import parse_qoi_strict
from .spec.chunk.chunk import Chunk


def qoi_iter_chunks(source: "str | Path") -> Iterator[Chunk]:
    """Yield spec-shaped Chunk objects for every pixel in a QOI document.

    Each decoded pixel is represented as a spec-shaped Chunk with its
    RGBA channel values and inferred chunk type.

    Args:
        source: Path to a .qoi Quite OK Image file.

    Yields:
        Chunk instances (spec class: qoi:chunk, SAL-QOI-00002).
    """
    img = parse_qoi_strict(str(Path(source).resolve()))
    channels = img.channels
    for pixel in img.pixels:
        if len(pixel) >= 4:
            chunk_type = "QOI_OP_RGBA"
            data = {"r": pixel[0], "g": pixel[1], "b": pixel[2], "a": pixel[3], "byte_length": 5}
        else:
            chunk_type = "QOI_OP_RGB"
            data = {"r": pixel[0], "g": pixel[1], "b": pixel[2], "byte_length": 4}
        yield Chunk(chunk_type, data)
