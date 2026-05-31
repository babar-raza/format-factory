"""
format-factory-pbm — Python FOSS parser for PBM (Portable Bitmap) format.

Public API:
    parse_pbm(file_path)        — returns result dict (never raises)
    parse_pbm_strict(file_path) — raises PbmError subclasses on failure
    probe_pbm(file_path)        — returns header metadata without full decode
    get_capabilities()          — returns capability dict

License: Apache-2.0
Package: format-factory-pbm v0.1.0
Gate history: Gates 1-9 PASSED; Gate 10 R59
"""

from .pbm_parser import (
    parse_pbm,
    parse_pbm_strict,
    probe_pbm,
    get_capabilities,
    image_pixel_stats,
    write_pbm,
    PbmError,
    PbmInvalidMagicError,
    PbmInvalidHeaderError,
    PbmSizeError,
    PbmDecodeError,
    PbmImage,
)
from .pbm_to_pgm import (
    convert_pbm_to_pgm,
    pbm_pixels_to_pgm_pixels,
)

__version__ = "0.1.0"
__track__ = "python-foss"
__commercial_ready__ = False
__capability_level__ = "alpha-foss-preview"

__all__ = [
    "parse_pbm",
    "parse_pbm_strict",
    "probe_pbm",
    "get_capabilities",
    "image_pixel_stats",
    "write_pbm",
    "PbmError",
    "PbmInvalidMagicError",
    "PbmInvalidHeaderError",
    "PbmSizeError",
    "PbmDecodeError",
    "PbmImage",
    "convert_pbm_to_pgm",
    "pbm_pixels_to_pgm_pixels",
]
