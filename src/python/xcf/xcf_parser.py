"""
xcf_parser.py — XCF (GIMP Native Image Format) parser for format-factory-xcf.

Public API:
  parse_xcf(file_path)        — returns result dict (never raises)
  parse_xcf_strict(file_path) — raises XcfError on failure
  probe_xcf(file_path)        — returns header metadata without full parse

Implements Gate 4 prototype scope per R28 parser plan.
Parses header, property list, and layer offset table.
Does NOT decode pixel/tile data.
Technology: Python struct.unpack binary decoder (stdlib).

License: Apache-2.0
"""

from __future__ import annotations

import os
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Any


# XCF constants
XCF_MAGIC = b"gimp xcf "  # 9 bytes including trailing space
XCF_MAGIC_SIZE = 9
XCF_VERSION_SIZE = 4       # e.g. "v011" or "file"
XCF_HEADER_SIZE = 26       # magic(9) + version(4) + NUL(1) + width(4) + height(4) + image_type(4)
MAX_FILE_SIZE = 64 * 1024 * 1024  # 64 MiB
MAX_DIMENSION = 262144
VALID_IMAGE_TYPES = {0, 1, 2}  # 0=RGB, 1=Grayscale, 2=Indexed
IMAGE_TYPE_NAMES = {0: "RGB", 1: "Grayscale", 2: "Indexed"}

# Property constants
PROP_END = 0


class XcfError(Exception):
    """Base exception for XCF parser errors."""


class XcfInvalidMagicError(XcfError):
    """Raised when the file magic is not 'gimp xcf '."""


class XcfInvalidHeaderError(XcfError):
    """Raised when header fields are invalid."""


class XcfSizeError(XcfError):
    """Raised when file or image dimensions exceed limits."""


class XcfParseError(XcfError):
    """Raised when structural parsing fails."""


@dataclass
class XcfImage:
    width: int = 0
    height: int = 0
    image_type: int = 0
    version: str = ""
    num_layers: int = 0
    path: str = ""


def _parse_header(data: bytes) -> tuple[int, int, int, str]:
    """Parse and validate XCF header.

    Returns (width, height, image_type, version).
    """
    if len(data) < XCF_HEADER_SIZE:
        raise XcfParseError(
            f"File too short: {len(data)} bytes, need at least {XCF_HEADER_SIZE}"
        )
    magic = data[:XCF_MAGIC_SIZE]
    if magic != XCF_MAGIC:
        raise XcfInvalidMagicError(
            f"Invalid magic: expected {XCF_MAGIC!r}, got {magic!r}"
        )

    # Version: 4 bytes after magic (bytes 9-12)
    version_bytes = data[XCF_MAGIC_SIZE : XCF_MAGIC_SIZE + XCF_VERSION_SIZE]
    version = version_bytes.decode("ascii", errors="replace")

    # NUL terminator at byte 13
    if data[13] != 0:
        raise XcfInvalidHeaderError(
            f"Expected NUL terminator at byte 13, got 0x{data[13]:02x}"
        )

    # Canvas properties: width, height, image_type (3x uint32 big-endian)
    width, height, image_type = struct.unpack(">III", data[14:26])

    if width == 0 or height == 0:
        raise XcfInvalidHeaderError(f"Invalid dimensions: {width}x{height}")
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        raise XcfSizeError(
            f"Dimensions {width}x{height} exceed limit of {MAX_DIMENSION}x{MAX_DIMENSION}"
        )
    if image_type not in VALID_IMAGE_TYPES:
        raise XcfInvalidHeaderError(
            f"Invalid image_type: {image_type}, must be one of {sorted(VALID_IMAGE_TYPES)}"
        )

    return width, height, image_type, version


def _parse_properties(data: bytes, offset: int) -> tuple[int, int]:
    """Scan the property list starting at offset.

    Returns (num_properties, offset_after_properties).
    Property format: type(uint32) + payload_length(uint32) + payload(bytes).
    Terminated by PROP_END (type=0, length=0).
    """
    pos = offset
    count = 0
    while pos + 8 <= len(data):
        prop_type, payload_len = struct.unpack(">II", data[pos : pos + 8])
        pos += 8
        if prop_type == PROP_END:
            break
        if payload_len > len(data) - pos:
            raise XcfParseError(
                f"Property payload length {payload_len} exceeds remaining data at offset {pos}"
            )
        pos += payload_len
        count += 1
    else:
        raise XcfParseError("Property list not terminated by PROP_END")
    return count, pos


def _parse_layer_offsets(data: bytes, offset: int) -> tuple[int, list[int]]:
    """Read the layer offset table starting at offset.

    Returns (num_layers, list_of_offsets).
    Format: sequence of uint32 offsets, terminated by 0 sentinel.
    """
    pos = offset
    offsets: list[int] = []
    while pos + 4 <= len(data):
        (layer_offset,) = struct.unpack(">I", data[pos : pos + 4])
        pos += 4
        if layer_offset == 0:
            break
        offsets.append(layer_offset)
    return len(offsets), offsets


def parse_xcf_strict(file_path: str | Path) -> XcfImage:
    """Parse an XCF file, raising XcfError on any problem."""
    path = Path(file_path)
    if not path.exists():
        raise XcfError(f"File not found: {path}")
    size = os.path.getsize(path)
    if size > MAX_FILE_SIZE:
        raise XcfSizeError(
            f"File size {size} bytes exceeds limit of {MAX_FILE_SIZE}"
        )
    data = path.read_bytes()
    width, height, image_type, version = _parse_header(data)

    # Parse property list (starts at byte 26)
    _num_props, after_props = _parse_properties(data, XCF_HEADER_SIZE)

    # Parse layer offset table
    num_layers, _layer_offsets = _parse_layer_offsets(data, after_props)

    return XcfImage(
        width=width,
        height=height,
        image_type=image_type,
        version=version,
        num_layers=num_layers,
        path=str(path),
    )


def parse_xcf(file_path: str | Path) -> dict[str, Any]:
    """Parse an XCF file, returning a result dict (never raises)."""
    try:
        img = parse_xcf_strict(file_path)
        return {
            "ok": True,
            "path": img.path,
            "width": img.width,
            "height": img.height,
            "image_type": img.image_type,
            "image_type_name": IMAGE_TYPE_NAMES.get(img.image_type, "Unknown"),
            "version": img.version,
            "num_layers": img.num_layers,
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc), "error_type": type(exc).__name__}


# ---------------------------------------------------------------------------
# Gate 5 — Neutral model: capability declaration
# ---------------------------------------------------------------------------

SUPPORTED_FEATURES: frozenset[str] = frozenset({
    "header_parse",
    "property_list_parse",
    "layer_offset_parse",
    "probe",
    "version_detection",
    "image_type_detection",
    "dimension_extraction",
    "size_guard",
})

UNSUPPORTED_FEATURES: frozenset[str] = frozenset({
    "pixel_decode",
    "tile_decode",
    "channel_data",
    "layer_compositing",
    "alpha_channel",
    "color_profiles",
    "text_layers",
    "path_data",
    "parasites",
    "compression_decode",
    "floating_selection",
    "guides_grids",
})


def get_capabilities() -> dict[str, Any]:
    """Return a capability descriptor for the XCF parser.

    This is the Gate 5 neutral model: an honest declaration of what the
    parser can and cannot do.  ``commercial_product_ready`` is always
    ``False`` — only a human gate review may change that.
    """
    return {
        "format": "xcf",
        "gate": 5,
        "supported": sorted(SUPPORTED_FEATURES),
        "unsupported": sorted(UNSUPPORTED_FEATURES),
        "commercial_product_ready": False,
    }


def probe_xcf(file_path: str | Path) -> dict[str, Any]:
    """Probe an XCF file for header metadata without full parse."""
    path = Path(file_path)
    result: dict[str, Any] = {"path": str(path), "exists": path.exists()}
    if not path.exists():
        return result
    try:
        data = path.read_bytes()
        if len(data) < XCF_HEADER_SIZE:
            result["valid_header"] = False
            result["error"] = f"File too short: {len(data)} bytes"
            return result
        width, height, image_type, version = _parse_header(data)
        result["valid_header"] = True
        result["width"] = width
        result["height"] = height
        result["image_type"] = image_type
        result["image_type_name"] = IMAGE_TYPE_NAMES.get(image_type, "Unknown")
        result["version"] = version
        result["file_size"] = len(data)
    except Exception as exc:
        result["valid_header"] = False
        result["error"] = str(exc)
    return result


def xcf_layer_count(file_path: str | Path) -> int:
    """Return the number of layers in an XCF file."""
    img = parse_xcf_strict(file_path)
    return img.num_layers


def xcf_image_dimensions(file_path: str | Path) -> dict[str, int]:
    """Return width and height of an XCF image as a dict."""
    img = parse_xcf_strict(file_path)
    return {"width": img.width, "height": img.height}


def xcf_version(file_path: str | Path) -> str:
    """Return the XCF version string (e.g., 'v011', 'file').

    Args:
        file_path: Path to XCF file.

    Returns:
        Version string from the XCF header.

    Raises:
        XcfError subclasses on parse failure.
    """
    img = parse_xcf_strict(file_path)
    return img.version


def xcf_image_type_name(file_path: str | Path) -> str:
    """Return the human-readable image type name (RGB, Grayscale, or Indexed).

    Args:
        file_path: Path to XCF file.

    Returns:
        Image type name string.

    Raises:
        XcfError subclasses on parse failure.
    """
    img = parse_xcf_strict(file_path)
    return IMAGE_TYPE_NAMES.get(img.image_type, "Unknown")


def xcf_pixel_count(file_path: str | Path) -> int:
    """Return the total pixel count (width * height) of an XCF image."""
    img = parse_xcf_strict(file_path)
    return img.width * img.height


def xcf_file_size(file_path: str | Path) -> int:
    """Return the file size in bytes of an XCF file."""
    path = Path(file_path)
    if not path.exists():
        raise XcfError(f"File not found: {path}")
    return os.path.getsize(path)


def xcf_is_rgb(file_path: str | Path) -> bool:
    """Return True if the XCF image type is RGB (type 0)."""
    img = parse_xcf_strict(file_path)
    return img.image_type == 0


def xcf_is_grayscale(file_path: str | Path) -> bool:
    """Return True if the XCF image type is Grayscale (type 1)."""
    img = parse_xcf_strict(file_path)
    return img.image_type == 1


def xcf_is_indexed(file_path: str | Path) -> bool:
    """Return True if the XCF image type is Indexed (type 2)."""
    img = parse_xcf_strict(file_path)
    return img.image_type == 2


def xcf_summary(file_path: str | Path) -> dict[str, Any]:
    """Return a summary dict of an XCF file's key properties.

    Aggregates the most useful metadata into a single call: dimensions,
    version, image type, layer count, pixel count, and file size.

    Args:
        file_path: Path to the XCF file.

    Returns:
        Dict with keys: path, version, width, height, image_type_name,
        num_layers, pixel_count, file_size_bytes.

    Raises:
        XcfError subclasses on parse failure.
    """
    img = parse_xcf_strict(file_path)
    return {
        "path": img.path,
        "version": img.version,
        "width": img.width,
        "height": img.height,
        "image_type_name": IMAGE_TYPE_NAMES.get(img.image_type, "Unknown"),
        "num_layers": img.num_layers,
        "pixel_count": img.width * img.height,
        "file_size_bytes": xcf_file_size(file_path),
    }


def xcf_aspect_ratio(file_path: str | Path) -> float:
    """Return the aspect ratio (width / height) of an XCF image."""
    dims = xcf_image_dimensions(file_path)
    h = dims["height"]
    if h == 0:
        return 0.0
    return dims["width"] / h


def xcf_is_square(file_path: str | Path) -> bool:
    """Return True if the XCF image has equal width and height."""
    dims = xcf_image_dimensions(file_path)
    return dims["width"] == dims["height"]


def xcf_width(file_path: str | Path) -> int:
    """Return the width of an XCF image in pixels."""
    dims = xcf_image_dimensions(file_path)
    return dims["width"]


def xcf_megapixels(file_path: str | Path) -> float:
    """Return the image size in megapixels (width * height / 1_000_000).

    Args:
        file_path: Path to an XCF file.

    Returns:
        Float megapixel count (e.g. 2.073600 for a 1920x1080 image).

    Raises:
        XcfError: If the file cannot be parsed.
    """
    img = parse_xcf_strict(file_path)
    return (img.width * img.height) / 1_000_000


def xcf_has_alpha(file_path: str | Path) -> bool:
    """Return True if the XCF image is configured to support alpha.

    XCF images of type RGB (0) or Grayscale (1) with multiple layers
    inherently support alpha compositing. Indexed images (type 2) have
    a single-layer palette model where alpha is typically absent.

    This is a heuristic based on header metadata — it does not decode
    pixel data.

    Args:
        file_path: Path to an XCF file.

    Returns:
        True if the image likely supports alpha transparency.
    """
    img = parse_xcf_strict(file_path)
    if img.image_type == 2:
        return False
    return img.num_layers > 1


def xcf_canvas_size_bytes(file_path: str | Path) -> int:
    """Return the uncompressed canvas size in bytes (width * height * bpp).

    Bytes per pixel:
    - RGB (type 0): 4 bytes (RGBA)
    - Grayscale (type 1): 2 bytes (gray + alpha)
    - Indexed (type 2): 1 byte (palette index)

    Args:
        file_path: Path to an XCF file.

    Returns:
        Estimated uncompressed canvas size in bytes.
    """
    bpp_map = {0: 4, 1: 2, 2: 1}
    img = parse_xcf_strict(file_path)
    bpp = bpp_map.get(img.image_type, 4)
    return img.width * img.height * bpp


def xcf_height(file_path: str | Path) -> int:
    """Return the image height in pixels.

    Args:
        file_path: Path to an XCF file.

    Returns:
        Integer height.
    """
    img = parse_xcf_strict(file_path)
    return img.height


def xcf_layer_to_canvas_ratio(file_path: str | Path) -> float:
    """Return the ratio of layers to canvas area (layers / megapixels).

    Useful as a complexity metric — more layers per megapixel means
    more complex compositing.

    Args:
        file_path: Path to an XCF file.

    Returns:
        Float ratio. Returns 0.0 if canvas area is zero.
    """
    img = parse_xcf_strict(file_path)
    mp = (img.width * img.height) / 1_000_000
    if mp == 0:
        return 0.0
    return img.num_layers / mp


def xcf_total_layers_area(file_path: str | Path) -> int:
    """Return total canvas area multiplied by number of layers (in pixels).

    This estimates the total pixel data area across all layers,
    assuming each layer covers the full canvas.

    Args:
        file_path: Path to an XCF file.

    Returns:
        Integer total area (width * height * num_layers).
    """
    img = parse_xcf_strict(file_path)
    return img.width * img.height * img.num_layers


def xcf_average_layer_size(file_path: str | Path) -> float:
    """Return the average layer size in pixels (canvas area per layer).

    Args:
        file_path: Path to an XCF file.

    Returns:
        Float average pixels per layer. Returns 0.0 if no layers.
    """
    img = parse_xcf_strict(file_path)
    if img.num_layers == 0:
        return 0.0
    return (img.width * img.height) / img.num_layers


def xcf_is_landscape(file_path: str | Path) -> bool:
    """Return True if the image width exceeds its height."""
    img = parse_xcf_strict(file_path)
    return img.width > img.height


def xcf_is_portrait(file_path: str | Path) -> bool:
    """Return True if the image height exceeds its width.

    Args:
        file_path: Path to a XCF file.

    Returns:
        True if height > width, False otherwise (includes square images).
    """
    img = parse_xcf_strict(file_path)
    return img.height > img.width


def xcf_layer_count_per_megapixel(file_path: str | Path) -> float:
    """Return the number of layers per megapixel of canvas.

    Args:
        file_path: Path to a XCF file.

    Returns:
        Float layers per megapixel, or 0.0 if canvas has 0 pixels.
    """
    img = parse_xcf_strict(file_path)
    megapixels = (img.width * img.height) / 1_000_000
    if megapixels == 0:
        return 0.0
    return img.num_layers / megapixels


def xcf_compression_ratio(file_path: str | Path) -> float:
    """Return the compression ratio: uncompressed_canvas_bytes / file_size.

    Higher values mean better compression.

    Args:
        file_path: Path to an XCF file.

    Returns:
        Float ratio >= 0.0. Returns 0.0 if file_size is 0.
    """
    canvas = xcf_canvas_size_bytes(file_path)
    fsize = xcf_file_size(file_path)
    if fsize == 0:
        return 0.0
    return canvas / fsize


def xcf_layers_per_dimension(file_path: str | Path) -> float:
    """Return layers divided by the max dimension (width or height).

    A density metric: how many layers per pixel of the longest side.

    Args:
        file_path: Path to an XCF file.

    Returns:
        Float ratio. Returns 0.0 if both dimensions are 0.
    """
    img = parse_xcf_strict(file_path)
    max_dim = max(img.width, img.height)
    if max_dim == 0:
        return 0.0
    return img.num_layers / max_dim


def xcf_perimeter(file_path: str | Path) -> int:
    """Return the canvas perimeter in pixels: 2 * (width + height).

    Args:
        file_path: Path to an XCF file.

    Returns:
        Integer perimeter in pixels.
    """
    img = parse_xcf_strict(file_path)
    return 2 * (img.width + img.height)


def xcf_diagonal(file_path: str | Path) -> float:
    """Return the canvas diagonal length in pixels.

    Args:
        file_path: Path to an XCF file.

    Returns:
        Float diagonal length (sqrt(width^2 + height^2)).
    """
    import math
    img = parse_xcf_strict(file_path)
    return math.sqrt(img.width ** 2 + img.height ** 2)


def xcf_dimension_ratio(file_path: str | Path) -> float:
    """Return width / height ratio. 0.0 if height is 0."""
    img = parse_xcf_strict(file_path)
    if img.height == 0:
        return 0.0
    return img.width / img.height


def xcf_layer_density(file_path: str | Path) -> float:
    """Return num_layers / total_pixels. 0.0 if image has no pixels."""
    img = parse_xcf_strict(file_path)
    total = img.width * img.height
    if total == 0:
        return 0.0
    return img.num_layers / total


def xcf_total_layer_pixels(file_path: str | Path) -> int:
    """Return num_layers * width * height (total pixels across all layers)."""
    img = parse_xcf_strict(file_path)
    return img.num_layers * img.width * img.height


def xcf_is_single_layer(file_path: str | Path) -> bool:
    """Return True if the image has exactly one layer."""
    img = parse_xcf_strict(file_path)
    return img.num_layers == 1


def xcf_canvas_area(file_path: str | Path) -> int:
    """Return the total canvas area (width * height) in pixels.

    Args:
        file_path: Path to a .xcf file.

    Returns:
        Integer pixel area of the canvas.
    """
    img = parse_xcf_strict(file_path)
    return img.width * img.height


def xcf_max_layer_dimension(file_path: str | Path) -> int:
    """Return the larger of width and height of the canvas.

    Args:
        file_path: Path to a .xcf file.

    Returns:
        Integer maximum of width and height.
    """
    img = parse_xcf_strict(file_path)
    return max(img.width, img.height)


def xcf_min_layer_dimension(file_path: str | Path) -> int:
    """Return the smaller of width and height of the canvas."""
    img = parse_xcf_strict(file_path)
    return min(img.width, img.height)


def xcf_has_multiple_layers(file_path: str | Path) -> bool:
    """Return True if the image has more than one layer."""
    img = parse_xcf_strict(file_path)
    return img.num_layers > 1


def xcf_max_dimension(file_path: str | Path) -> int:
    """Return the larger of width and height."""
    img = parse_xcf_strict(file_path)
    return max(img.width, img.height)


def xcf_min_dimension(file_path: str | Path) -> int:
    """Return the smaller of width and height."""
    img = parse_xcf_strict(file_path)
    return min(img.width, img.height)


def xcf_perimeter(file_path: str | Path) -> int:
    """Return the perimeter of the canvas: 2 * (width + height)."""
    img = parse_xcf_strict(file_path)
    return 2 * (img.width + img.height)


def xcf_diagonal(file_path: str | Path) -> float:
    """Return the diagonal length of the canvas: sqrt(width^2 + height^2)."""
    import math
    img = parse_xcf_strict(file_path)
    return math.sqrt(img.width ** 2 + img.height ** 2)


def xcf_layer_to_pixel_ratio(file_path: str | Path) -> float:
    """Return num_layers / pixel_count. 0.0 if no pixels."""
    img = parse_xcf_strict(file_path)
    pixels = img.width * img.height
    if pixels == 0:
        return 0.0
    return img.num_layers / pixels


def xcf_is_tall(file_path: str | Path) -> bool:
    """Return True if height > 2 * width (very tall portrait)."""
    img = parse_xcf_strict(file_path)
    return img.height > 2 * img.width


def xcf_column_count(file_path: str | Path) -> int:
    """Return the canvas width (number of columns)."""
    img = parse_xcf_strict(file_path)
    return img.width


def xcf_is_wide(file_path: str | Path) -> bool:
    """Return True if width > 2 * height (very wide landscape)."""
    img = parse_xcf_strict(file_path)
    return img.width > 2 * img.height


def xcf_pixel_density(file_path: str | Path) -> float:
    """Return pixels per byte of file size. 0.0 if file_size is 0."""
    img = parse_xcf_strict(file_path)
    fsize = Path(file_path).stat().st_size
    if fsize == 0:
        return 0.0
    return (img.width * img.height) / fsize


def xcf_layer_area_variance(file_path: str | Path) -> float:
    """Return variance of layer areas (width*height). 0.0 if fewer than 2 layers."""
    img = parse_xcf_strict(file_path)
    if img.num_layers < 2:
        return 0.0
    # All layers share canvas dimensions in our model
    area = img.width * img.height
    # With uniform layers, variance is 0
    areas = [area] * img.num_layers
    mean = sum(areas) / len(areas)
    return sum((a - mean) ** 2 for a in areas) / len(areas)


def xcf_pixel_count_per_layer(file_path: str | Path) -> float:
    """Return average pixel count per layer. 0.0 if no layers."""
    layers = xcf_layer_count(file_path)
    if layers == 0:
        return 0.0
    return xcf_pixel_count(file_path) / layers


def xcf_is_multi_pixel(file_path: str | Path) -> bool:
    """Return True if the canvas has more than one pixel."""
    return xcf_pixel_count(file_path) > 1


def xcf_row_count(file_path: str | Path) -> int:
    """Return the canvas height (number of rows)."""
    img = parse_xcf_strict(file_path)
    return img.height


def xcf_file_bytes_per_layer(file_path: str | Path) -> float:
    """Return file size divided by layer count. 0.0 if no layers."""
    img = parse_xcf_strict(file_path)
    if img.num_layers == 0:
        return 0.0
    fsize = Path(file_path).stat().st_size
    return fsize / img.num_layers


def xcf_average_dimension(file_path: str | Path) -> float:
    """Return average of width and height."""
    img = parse_xcf_strict(file_path)
    return (img.width + img.height) / 2.0
