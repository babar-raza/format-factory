"""
pbm_to_pgm.py — Dogfood export: PBM (1-bit bitmap) to PGM (8-bit grayscale).

Public API:
    convert_pbm_to_pgm(pbm_path, pgm_output_path, maxval=255) — convert and save
    pbm_pixels_to_pgm_pixels(pbm_pixels, maxval=255) — convert pixel list only

Dogfooding: Uses Format Factory's own PBM parser (parse_pbm_strict) and PGM writer (write_pgm).
No external image library is used.

dogfood_status: IMPLEMENTED
target_ff_libraries: format-factory-pbm (parse_pbm_strict), format-factory-pgm (write_pgm)

Mapping convention:
    PBM 0 (white) → PGM maxval (white)
    PBM 1 (black) → PGM 0       (black)

License: Apache-2.0
Package: format-factory-pbm v0.1.0
R85 Train M: Netpbm family dogfood export added
"""
from __future__ import annotations

from pathlib import Path
from typing import Union

from .pbm_parser import parse_pbm_strict, PbmImage


def pbm_pixels_to_pgm_pixels(
    pbm_pixels: list[int],
    maxval: int = 255,
) -> list[int]:
    """Convert PBM pixel list to PGM pixel list.

    PBM convention:
      0 = white (background)
      1 = black (foreground)

    PGM convention (standard):
      maxval = white
      0 = black

    Args:
        pbm_pixels: Flat row-major list of PBM pixel values (0 or 1).
        maxval: Output grayscale maximum (1-255). Default: 255.

    Returns:
        Flat row-major list of PGM pixel values.
    """
    if not (1 <= maxval <= 255):
        raise ValueError(f"maxval must be in range 1-255, got {maxval}")
    return [0 if p == 1 else maxval for p in pbm_pixels]


def convert_pbm_to_pgm(
    pbm_path: Union[str, Path],
    pgm_output_path: Union[str, Path],
    maxval: int = 255,
) -> dict:
    """Convert a PBM file to PGM using Format Factory's own libraries.

    dogfood_status: IMPLEMENTED
    Uses: format-factory-pbm parse_pbm_strict + format-factory-pgm write_pgm

    Args:
        pbm_path: Input PBM file path (P1 or P4).
        pgm_output_path: Output PGM file path (P2 ASCII).
        maxval: Output grayscale maximum (1-255). Default: 255.

    Returns:
        dict with: width, height, maxval, pixel_count, dogfood_library

    Raises:
        PbmError: If PBM parsing fails.
        ValueError: If maxval is out of range.
    """
    # Import FF PGM writer — dogfood dependency
    from pgm.pgm_parser import write_pgm  # type: ignore[import]

    pbm_path = Path(pbm_path)
    pgm_output_path = Path(pgm_output_path)

    # Step 1: Parse PBM using Format Factory PBM library
    pbm_image: PbmImage = parse_pbm_strict(pbm_path)

    # Step 2: Convert pixel values
    pgm_pixels = pbm_pixels_to_pgm_pixels(pbm_image.pixels, maxval=maxval)

    # Step 3: Write PGM using Format Factory PGM library
    write_pgm(
        pixels=pgm_pixels,
        width=pbm_image.width,
        height=pbm_image.height,
        maxval=maxval,
        file_path=pgm_output_path,
        comment=f"Converted from PBM by format-factory-pbm dogfood export",
    )

    return {
        "width": pbm_image.width,
        "height": pbm_image.height,
        "maxval": maxval,
        "pixel_count": len(pgm_pixels),
        "dogfood_library": "format-factory-pgm write_pgm",
        "dogfood_status": "IMPLEMENTED",
    }
