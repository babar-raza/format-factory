"""
format-factory-pgm — Python FOSS parser for PGM (Portable Graymap) format.

Public API:
    parse_pgm(file_path)        — returns result dict (never raises)
    parse_pgm_strict(file_path) — raises PgmError subclasses on failure
    probe_pgm(file_path)        — returns header metadata without full decode
    get_capabilities()          — returns capability dict

License: Apache-2.0
Package: format-factory-pgm v0.1.0
Gate history: Gates 1-9 PASSED; Gate 10 R59
"""

from .pgm_parser import (
    parse_pgm,
    parse_pgm_strict,
    probe_pgm,
    get_capabilities,
    image_pixel_stats,
    write_pgm,
    get_dimensions,
    pixel_count,
    average_gray,
    count_above_threshold,
    min_max_gray,
    flip_horizontal,
    normalize,
    histogram,
    threshold,
    rotate_90,
    grayscale_variance,
    pgm_bright_pixel_ratio,
    pgm_dark_pixel_count,
    pgm_average_brightness,
    pgm_max_pixel_value,
    pgm_min_pixel_value,
    pgm_contrast_range,
    pgm_median_pixel_value,
    PgmError,
    PgmInvalidMagicError,
    PgmInvalidHeaderError,
    PgmSizeError,
    PgmDecodeError,
    PgmImage,
)

__version__ = "0.1.0"
__track__ = "python-foss"
__commercial_ready__ = False
__capability_level__ = "alpha-foss-preview"

__all__ = [
    "parse_pgm",
    "parse_pgm_strict",
    "probe_pgm",
    "get_capabilities",
    "image_pixel_stats",
    "write_pgm",
    "get_dimensions",
    "pixel_count",
    "average_gray",
    "count_above_threshold",
    "min_max_gray",
    "flip_horizontal",
    "normalize",
    "histogram",
    "threshold",
    "rotate_90",
    "grayscale_variance",
    "pgm_bright_pixel_ratio",
    "pgm_dark_pixel_count",
    "pgm_average_brightness",
    "pgm_max_pixel_value",
    "pgm_min_pixel_value",
    "pgm_contrast_range",
    "pgm_median_pixel_value",
    "PgmError",
    "PgmInvalidMagicError",
    "PgmInvalidHeaderError",
    "PgmSizeError",
    "PgmDecodeError",
    "PgmImage",
]
