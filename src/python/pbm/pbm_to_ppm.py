"""
pbm_to_ppm.py — Dogfood export: PBM (1-bit bitmap) to PPM (RGB color).

Public API:
    convert_pbm_to_ppm(pbm_path, ppm_output_path, maxval=255) — convert and save
    pbm_pixels_to_ppm_pixels(pbm_pixels, maxval=255) — convert pixel list only

Dogfooding: Uses Format Factory's own PBM parser (parse_pbm_strict) and PPM writer (write_ppm).
No external image library is used.

dogfood_status: IMPLEMENTED
target_ff_libraries: format-factory-pbm (parse_pbm_strict), format-factory-ppm (write_ppm)

Mapping convention:
    PBM 0 (white) → PPM (maxval, maxval, maxval) (white)
    PBM 1 (black) → PPM (0, 0, 0)                (black)

License: Apache-2.0
Package: format-factory-pbm v0.1.0
R86 Train M: Netpbm PBM→PPM dogfood export added
"""
from __future__ import annotations

from pathlib import Path
from typing import Union

from .pbm_parser import parse_pbm_strict, PbmImage


def pbm_pixels_to_ppm_pixels(
    pbm_pixels: list[int],
    maxval: int = 255,
) -> list[tuple[int, int, int]]:
    """Convert a flat PBM pixel list (0/1) to PPM RGB tuples.

    PBM 0 (white) → (maxval, maxval, maxval)
    PBM 1 (black) → (0, 0, 0)
    """
    if maxval < 1:
        raise ValueError(f"maxval must be >= 1, got {maxval}")
    result: list[tuple[int, int, int]] = []
    for p in pbm_pixels:
        if p == 0:
            result.append((maxval, maxval, maxval))
        else:
            result.append((0, 0, 0))
    return result


def convert_pbm_to_ppm(
    pbm_path: Union[str, Path],
    ppm_output_path: Union[str, Path],
    maxval: int = 255,
) -> dict:
    """Convert a PBM file to PPM using Format Factory libraries (dogfood).

    Returns a result dict with conversion metadata.
    """
    # Import FF PPM writer (dogfood dependency)
    from ppm.ppm_parser import write_ppm

    pbm_image: PbmImage = parse_pbm_strict(pbm_path)
    ppm_pixels = pbm_pixels_to_ppm_pixels(pbm_image.pixels, maxval=maxval)

    write_ppm(
        pixels=ppm_pixels,
        width=pbm_image.width,
        height=pbm_image.height,
        maxval=maxval,
        file_path=ppm_output_path,
        comment=f"Converted from PBM by format-factory (dogfood export)",
    )

    return {
        "status": "success",
        "source": str(pbm_path),
        "output": str(ppm_output_path),
        "width": pbm_image.width,
        "height": pbm_image.height,
        "maxval": maxval,
        "dogfood": True,
    }
