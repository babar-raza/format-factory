"""
ppm_to_pgm.py - Dogfood export: PPM (RGB color) to PGM (grayscale).

Uses Format Factory's own PPM parser and PGM writer.

dogfood_status: IMPLEMENTED
target_ff_library: pgm.pgm_parser.write_pgm
"""

from __future__ import annotations

from pathlib import Path

from .ppm_parser import parse_ppm_strict


def ppm_pixels_to_pgm_pixels(
    ppm_pixels: list[tuple[int, int, int]],
    maxval: int = 255,
) -> list[int]:
    """Convert RGB pixels to grayscale using the integer BT.601 approximation."""
    if not 1 <= maxval <= 65535:
        raise ValueError(f"maxval must be in range 1-65535, got {maxval}")
    grayscale: list[int] = []
    for index, pixel in enumerate(ppm_pixels):
        if len(pixel) != 3:
            raise ValueError(f"pixel {index} must contain exactly three channels")
        red, green, blue = pixel
        if any(channel < 0 or channel > maxval for channel in pixel):
            raise ValueError(f"pixel {index} channel out of range [0, {maxval}]: {pixel}")
        grayscale.append((299 * red + 587 * green + 114 * blue + 500) // 1000)
    return grayscale


def convert_ppm_to_pgm(
    ppm_path: str | Path,
    pgm_output_path: str | Path,
) -> dict[str, object]:
    """Convert PPM to PGM through Format Factory's PGM writer."""
    from pgm.pgm_parser import write_pgm

    ppm_image = parse_ppm_strict(ppm_path)
    pgm_pixels = ppm_pixels_to_pgm_pixels(ppm_image.pixels, maxval=ppm_image.maxval)
    write_pgm(
        pixels=pgm_pixels,
        width=ppm_image.width,
        height=ppm_image.height,
        maxval=ppm_image.maxval,
        file_path=pgm_output_path,
        comment="Converted from PPM by Format Factory dogfood export",
    )
    return {
        "status": "success",
        "dogfood": True,
        "source_format": "PPM",
        "target_format": "PGM",
        "width": ppm_image.width,
        "height": ppm_image.height,
        "ff_write_library": "pgm.pgm_parser.write_pgm",
    }
