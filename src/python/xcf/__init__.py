"""
format-factory-xcf — XCF (GIMP Native Image Format) parser prototype.

Gate 4 prototype. FOSS track. No third-party dependencies.
Acquisition gates 1-3 passed. Implementation authorized: R28.
commercial_product_ready: false
"""

from .xcf_parser import (
    parse_xcf,
    parse_xcf_strict,
    probe_xcf,
    get_capabilities,
    xcf_layer_count,
    xcf_image_dimensions,
    xcf_version,
    xcf_image_type_name,
    xcf_pixel_count,
    xcf_file_size,
    xcf_is_rgb,
    xcf_is_grayscale,
    xcf_is_indexed,
    xcf_aspect_ratio,
    xcf_is_square,
    xcf_width,
    xcf_megapixels,
    xcf_has_alpha,
    xcf_canvas_size_bytes,
    xcf_height,
    xcf_layer_to_canvas_ratio,
    xcf_total_layers_area,
    xcf_average_layer_size,
    xcf_is_landscape,
    XcfError,
    XcfInvalidMagicError,
    XcfInvalidHeaderError,
    XcfSizeError,
    XcfParseError,
    XcfImage,
)

__version__ = "0.1.0.dev0"
__track__ = "python-foss"
__commercial_ready__ = False
__capability_level__ = "alpha-foss-preview"

__all__ = [
    "parse_xcf",
    "parse_xcf_strict",
    "probe_xcf",
    "get_capabilities",
    "xcf_layer_count",
    "xcf_image_dimensions",
    "xcf_version",
    "xcf_image_type_name",
    "xcf_pixel_count",
    "xcf_file_size",
    "xcf_is_rgb",
    "xcf_is_grayscale",
    "xcf_is_indexed",
    "xcf_aspect_ratio",
    "xcf_is_square",
    "xcf_width",
    "xcf_megapixels",
    "xcf_has_alpha",
    "xcf_canvas_size_bytes",
    "xcf_height",
    "xcf_layer_to_canvas_ratio",
    "xcf_total_layers_area",
    "xcf_average_layer_size",
    "xcf_is_landscape",
    "XcfError",
    "XcfInvalidMagicError",
    "XcfInvalidHeaderError",
    "XcfSizeError",
    "XcfParseError",
    "XcfImage",
]
