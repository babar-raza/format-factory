"""
format-factory-ppm — Python FOSS parser for PPM (Portable Pixmap) format.

Public API:
    parse_ppm(file_path)        — returns result dict (never raises)
    parse_ppm_strict(file_path) — raises PpmError subclasses on failure
    probe_ppm(file_path)        — returns header metadata without full decode
    get_capabilities()          — returns capability dict

License: Apache-2.0
Package: format-factory-ppm v0.1.0
Gate history: Gates 1-9 PASSED; Gate 10 R59
R84 Train M: PPM __init__.py promoted from stub to full package export
"""

from .ppm_parser import (
    parse_ppm,
    parse_ppm_strict,
    probe_ppm,
    get_capabilities,
    write_ppm,
    PpmError,
    PpmInvalidMagicError,
    PpmInvalidHeaderError,
    PpmSizeError,
    PpmDecodeError,
    PpmImage,
)
from .ppm_to_pgm import convert_ppm_to_pgm, ppm_pixels_to_pgm_pixels

__version__ = "0.1.0"
__track__ = "python-foss"
__commercial_ready__ = False
__capability_level__ = "alpha-foss-preview"

__all__ = [
    "parse_ppm",
    "parse_ppm_strict",
    "probe_ppm",
    "get_capabilities",
    "write_ppm",
    "PpmError",
    "PpmInvalidMagicError",
    "PpmInvalidHeaderError",
    "PpmSizeError",
    "PpmDecodeError",
    "PpmImage",
    "convert_ppm_to_pgm",
    "ppm_pixels_to_pgm_pixels",
]
