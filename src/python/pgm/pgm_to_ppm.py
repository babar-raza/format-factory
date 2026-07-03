"""
pgm_to_ppm.py — Dogfood export: PGM to PPM using Format Factory write_ppm.

R87 : PGM to PPM dogfood export.
Uses Format Factory's own ppm.ppm_parser.write_ppm (not external libraries).

dogfood_status: IMPLEMENTED
target_ff_library: ppm.ppm_parser.write_ppm
"""

from pathlib import Path

from pgm.pgm_parser import parse_pgm_strict
from ppm.ppm_parser import write_ppm


def pgm_pixels_to_ppm_pixels(pgm_pixels: list[int], maxval: int = 255) -> list[tuple[int, int, int]]:
    """Convert PGM grayscale pixels to PPM RGB tuples.

    Each gray value maps to (gray, gray, gray).
    """
    if maxval < 1:
        raise ValueError("maxval must be >= 1")
    return [(p, p, p) for p in pgm_pixels]


def convert_pgm_to_ppm(pgm_path: str | Path, ppm_output_path: str | Path,
                        maxval: int = 255) -> dict:
    """Convert a PGM file to PPM using Format Factory libraries.

    Dogfood path:
      - Read: pgm.pgm_parser.parse_pgm_strict (FF library)
      - Convert: pgm_pixels_to_ppm_pixels (this module)
      - Write: ppm.ppm_parser.write_ppm (FF library)
    """
    pgm_img = parse_pgm_strict(pgm_path)
    ppm_pixels = pgm_pixels_to_ppm_pixels(pgm_img.pixels, maxval=maxval)

    write_ppm(
        pixels=ppm_pixels,
        width=pgm_img.width,
        height=pgm_img.height,
        maxval=maxval,
        file_path=ppm_output_path,
        comment="Converted from PGM by Format Factory dogfood export (pgm_to_ppm)",
    )

    return {
        "status": "success",
        "dogfood": True,
        "width": pgm_img.width,
        "height": pgm_img.height,
        "source_format": "PGM",
        "target_format": "PPM",
        "ff_read_library": "pgm.pgm_parser.parse_pgm_strict",
        "ff_write_library": "ppm.ppm_parser.write_ppm",
    }
