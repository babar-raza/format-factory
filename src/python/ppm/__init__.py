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
    get_dimensions,
    to_grayscale,
    brightness,
    pixel_count,
    average_color,
    crop,
    flip_horizontal,
    invert,
    flip_vertical,
    rotate_90,
    is_grayscale,
    ppm_red_channel_average,
    ppm_green_channel_average,
    ppm_unique_color_count,
    ppm_brightness_variance,
    ppm_pixel_count,
    ppm_is_binary,
    ppm_aspect_ratio,
    ppm_dominant_channel,
    ppm_min_max_brightness,
    ppm_blue_channel_average,
    ppm_is_grayscale,
    ppm_channel_range,
    ppm_saturation_estimate,
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
    "get_dimensions",
    "to_grayscale",
    "brightness",
    "pixel_count",
    "average_color",
    "crop",
    "flip_horizontal",
    "invert",
    "flip_vertical",
    "rotate_90",
    "is_grayscale",
    "ppm_red_channel_average",
    "ppm_green_channel_average",
    "ppm_unique_color_count",
    "ppm_brightness_variance",
    "ppm_pixel_count",
    "ppm_is_binary",
    "ppm_aspect_ratio",
    "ppm_dominant_channel",
    "ppm_min_max_brightness",
    "ppm_blue_channel_average",
    "ppm_is_grayscale",
    "ppm_channel_range",
    "ppm_saturation_estimate",
    "PpmError",
    "PpmInvalidMagicError",
    "PpmInvalidHeaderError",
    "PpmSizeError",
    "PpmDecodeError",
    "PpmImage",
    "convert_ppm_to_pgm",
    "ppm_pixels_to_pgm_pixels",
]
