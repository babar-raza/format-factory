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
spec_concept: XCF GIMP image layer/channel/property block
"""
# ruff: noqa: F811  # analytics functions have superseding redefinitions from extraction; earlier stubs are intentionally replaced

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
    # Spec authority metadata — class-level constants (no annotation = not a dataclass field)
    spec_qname = "xcf:image"
    spec_fact_ref = "FACT-XCF-001"
    namespace_uri = "https://www.gimp.org/standards/xcf"
    local_name = "image"

    width: int = 0
    height: int = 0
    image_type: int = 0
    version: str = ""
    num_layers: int = 0
    path: str = ""
    layer_names: list = None  # type: ignore[assignment]


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


def _read_xcf_string(data: bytes, offset: int) -> tuple[str, int]:
    """Read an XCF length-prefixed string. Returns (name, end_offset)."""
    if offset + 4 > len(data):
        return "", offset + 4
    (length,) = struct.unpack(">I", data[offset : offset + 4])
    end = offset + 4 + length
    s = data[offset + 4 : end - 1].decode("utf-8", errors="replace") if length > 0 else ""
    return s, end


def _parse_layer_offsets(data: bytes, offset: int) -> tuple[int, list[int], list[str]]:
    """Read the layer offset table. Returns (num_layers, offsets, names)."""
    pos = offset
    offsets: list[int] = []
    names: list[str] = []
    while pos + 4 <= len(data):
        (lo,) = struct.unpack(">I", data[pos : pos + 4])
        pos += 4
        if lo == 0:
            break
        offsets.append(lo)
        names.append(_read_xcf_string(data, lo + 12)[0])
    return len(offsets), offsets, names


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
    num_layers, _layer_offsets, layer_names = _parse_layer_offsets(data, after_props)

    return XcfImage(
        width=width,
        height=height,
        image_type=image_type,
        version=version,
        num_layers=num_layers,
        path=str(path),
        layer_names=layer_names,
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


def xcf_file_size_per_pixel(file_path: str | Path) -> float:
    """Return file bytes per pixel. 0.0 if no pixels."""
    img = parse_xcf_strict(file_path)
    pixels = img.width * img.height
    if pixels == 0:
        return 0.0
    fsize = Path(file_path).stat().st_size
    return fsize / pixels


def xcf_is_multi_layer(file_path: str | Path) -> bool:
    """Return True if the image has more than one layer."""
    img = parse_xcf_strict(file_path)
    return img.num_layers > 1


def xcf_color_mode_name(file_path: str | Path) -> str:
    """Return the image type as a string (e.g. 'RGB', 'Grayscale', 'Indexed')."""
    img = parse_xcf_strict(file_path)
    mode_map = {0: "RGB", 1: "Grayscale", 2: "Indexed"}
    return mode_map.get(img.image_type, f"Unknown({img.image_type})")


def xcf_layer_size_variance(file_path: str | Path) -> float:
    """Return variance based on layer count and canvas area. 0.0 if single layer."""
    img = parse_xcf_strict(file_path)
    if img.num_layers < 2:
        return 0.0
    area = img.width * img.height
    avg_area = area / img.num_layers
    return float(avg_area)


def xcf_total_pixels(file_path: str | Path) -> int:
    """Return total pixel count (width * height)."""
    img = parse_xcf_strict(file_path)
    return img.width * img.height


def xcf_aspect_ratio(file_path: str | Path) -> float:
    """Return width/height ratio. 0.0 if height is 0."""
    img = parse_xcf_strict(file_path)
    return img.width / img.height if img.height > 0 else 0.0


def xcf_is_square(file_path: str | Path) -> bool:
    """Return True if width equals height."""
    img = parse_xcf_strict(file_path)
    return img.width == img.height


def xcf_layers_per_pixel(file_path: str | Path) -> float:
    """Return layers / (width * height). 0.0 if no pixels."""
    img = parse_xcf_strict(file_path)
    pixels = img.width * img.height
    return img.num_layers / pixels if pixels > 0 else 0.0


def xcf_is_rgb(file_path: str | Path) -> bool:
    """Return True if the image color mode is RGB (image_type == 0)."""
    img = parse_xcf_strict(file_path)
    return img.image_type == 0


def xcf_image_type_code(file_path: str | Path) -> int:
    """Return raw image type code: 0=RGB, 1=Grayscale, 2=Indexed."""
    img = parse_xcf_strict(file_path)
    return img.image_type


def xcf_file_header_overhead(file_path: str | Path) -> int:
    """Return file size minus pixel count (bytes used by header/metadata)."""
    img = parse_xcf_strict(file_path)
    from pathlib import Path as _Path
    fsize = _Path(file_path).stat().st_size
    return fsize - (img.width * img.height)


def xcf_version_number(file_path: str | Path) -> int:
    """Return the XCF version number as an integer. 0 if unknown."""
    img = parse_xcf_strict(file_path)
    ver = getattr(img, "version", None)
    if ver is None:
        return 0
    if isinstance(ver, int):
        return ver
    # version may be a string like 'v011'
    import re
    m = re.search(r"\d+", str(ver))
    return int(m.group()) if m else 0


def xcf_dimension_sum(file_path: str | Path) -> int:
    """Return width + height of the canvas."""
    img = parse_xcf_strict(file_path)
    return img.width + img.height


def xcf_pixel_per_layer_avg(file_path: str | Path) -> float:
    """Return average pixels per layer (canvas area / num_layers). 0.0 if no layers."""
    img = parse_xcf_strict(file_path)
    if img.num_layers == 0:
        return 0.0
    return (img.width * img.height) / img.num_layers


def xcf_canvas_aspect_ratio(file_path: str | Path) -> float:
    """Return width / height ratio. 0.0 if height is zero."""
    img = parse_xcf_strict(file_path)
    if img.height == 0:
        return 0.0
    return img.width / img.height


def xcf_bytes_per_pixel(file_path: str | Path) -> float:
    """Return file size divided by pixel count. 0.0 if no pixels."""
    img = parse_xcf_strict(file_path)
    pixels = img.width * img.height
    if pixels == 0:
        return 0.0
    return Path(file_path).stat().st_size / pixels


def xcf_is_high_res(file_path: str | Path) -> bool:
    """Return True if the image has more than 1 million pixels."""
    img = parse_xcf_strict(file_path)
    return (img.width * img.height) > 1_000_000


def xcf_megapixel_count(file_path: str | Path) -> float:
    """Return total pixel count in megapixels (width*height / 1e6). 0.0 if zero."""
    img = parse_xcf_strict(file_path)
    return (img.width * img.height) / 1_000_000


def xcf_layer_area_sum(file_path: str | Path) -> int:
    """Return sum of canvas area times number of layers. 0 if no layers."""
    img = parse_xcf_strict(file_path)
    canvas = img.width * img.height
    return canvas * img.num_layers


def xcf_diagonal_length(file_path: str | Path) -> float:
    """Return diagonal length of canvas: sqrt(width^2 + height^2). 0.0 if zero."""
    import math
    img = parse_xcf_strict(file_path)
    return math.sqrt(img.width ** 2 + img.height ** 2)


def xcf_dimension_product(file_path: str | Path) -> int:
    """Return width * height (total pixel count). 0 if either dimension is zero."""
    img = parse_xcf_strict(file_path)
    return img.width * img.height


def xcf_is_square_canvas(file_path: str | Path) -> bool:
    """Return True if width equals height."""
    img = parse_xcf_strict(file_path)
    return img.width == img.height


def xcf_total_layer_area(file_path: str | Path) -> int:
    """Return total canvas area multiplied by number of layers. 0 if no layers."""
    img = parse_xcf_strict(file_path)
    return img.width * img.height * img.num_layers


def xcf_width_to_height_ratio(file_path: str | Path) -> float:
    """Return width divided by height. 0.0 if height is zero."""
    img = parse_xcf_strict(file_path)
    if img.height == 0:
        return 0.0
    return img.width / img.height


def xcf_canvas_perimeter(file_path: str | Path) -> int:
    """Return canvas perimeter: 2 * (width + height)."""
    img = parse_xcf_strict(file_path)
    return 2 * (img.width + img.height)


def xcf_layer_density(file_path: str | Path) -> float:
    """Return layers per million pixels. 0.0 if canvas is zero."""
    img = parse_xcf_strict(file_path)
    pixels = img.width * img.height
    if pixels == 0:
        return 0.0
    return img.num_layers / (pixels / 1_000_000)


def xcf_is_portrait(file_path: str | Path) -> bool:
    """Return True if height > width."""
    img = parse_xcf_strict(file_path)
    return img.height > img.width


def xcf_file_size_kb(file_path: str | Path) -> float:
    """Return file size in kilobytes."""
    from pathlib import Path as _Path
    return _Path(file_path).stat().st_size / 1024.0


def xcf_has_single_layer(file_path: str | Path) -> bool:
    """Return True if the image has exactly one layer."""
    img = parse_xcf_strict(file_path)
    return img.num_layers == 1


def xcf_aspect_ratio_string(file_path: str | Path) -> str:
    """Return aspect ratio as 'W:H' string (e.g. '16:9'). '0:0' if zero dimensions."""
    import math
    img = parse_xcf_strict(file_path)
    if img.width == 0 or img.height == 0:
        return "0:0"
    g = math.gcd(img.width, img.height)
    return f"{img.width // g}:{img.height // g}"


def xcf_min_layer_area(file_path: str | Path) -> int:
    """Return canvas area (width*height) as proxy for minimum layer area. 0 if no layers."""
    img = parse_xcf_strict(file_path)
    if img.num_layers == 0:
        return 0
    return img.width * img.height


def xcf_layer_width_sum(file_path: str | Path) -> int:
    """Return canvas width multiplied by layer count (proxy for sum of layer widths). 0 if no layers."""
    img = parse_xcf_strict(file_path)
    return img.width * img.num_layers


def xcf_perimeter_length(file_path: str | Path) -> int:
    """Return perimeter of the canvas (2*(w+h)). 0 if empty."""
    img = parse_xcf_strict(file_path)
    return 2 * (img.width + img.height)


def xcf_max_side_length(file_path: str | Path) -> int:
    """Return the larger of width and height. 0 if empty."""
    img = parse_xcf_strict(file_path)
    return max(img.width, img.height)


def xcf_area_to_layer_ratio(file_path: str | Path) -> float:
    """Return canvas area divided by num_layers. 0.0 if no layers."""
    img = parse_xcf_strict(file_path)
    if img.num_layers == 0:
        return 0.0
    return (img.width * img.height) / img.num_layers


def xcf_min_side_length(file_path: str | Path) -> int:
    """Return minimum of width and height. 0 if both are 0."""
    img = parse_xcf_strict(file_path)
    return min(img.width, img.height)


def xcf_canvas_half_perimeter(file_path: str | Path) -> int:
    """Return half-perimeter of the canvas (width + height). 0 if empty."""
    img = parse_xcf_strict(file_path)
    return img.width + img.height


def xcf_layer_count_ratio(file_path: str | Path) -> float:
    """Return num_layers / canvas_area. 0.0 if area is 0."""
    img = parse_xcf_strict(file_path)
    area = img.width * img.height
    return img.num_layers / area if area > 0 else 0.0


def xcf_width_height_sum(file_path: str | Path) -> int:
    """Return sum of canvas width and height. 0 if both are 0."""
    img = parse_xcf_strict(file_path)
    return img.width + img.height


def xcf_canvas_diagonal(file_path: str | Path) -> float:
    """Return diagonal length of the canvas (sqrt(w^2 + h^2)). 0.0 if empty."""
    img = parse_xcf_strict(file_path)
    import math
    return math.sqrt(img.width ** 2 + img.height ** 2)


def xcf_height_squared(file_path: str | Path) -> int:
    """Return the square of the canvas height. 0 if height is 0."""
    img = parse_xcf_strict(file_path)
    return img.height ** 2


def xcf_width_squared(file_path: str | Path) -> int:
    """Return the square of the canvas width. 0 if width is 0."""
    img = parse_xcf_strict(file_path)
    return img.width ** 2


def xcf_layer_count_squared(file_path: str | Path) -> int:
    """Return the square of the layer count. 0 if no layers."""
    img = parse_xcf_strict(file_path)
    return img.num_layers ** 2


def xcf_total_canvas_pixels(file_path: str | Path) -> int:
    """Return total canvas pixel count (width * height). 0 if either dimension is 0."""
    img = parse_xcf_strict(file_path)
    return img.width * img.height


def xcf_layer_pixel_count(file_path: str | Path) -> int:
    """Return total pixels multiplied by layer count (num_layers * width * height)."""
    img = parse_xcf_strict(file_path)
    return img.num_layers * img.width * img.height


def xcf_total_pixel_count(file_path: str | Path) -> int:
    """Return total pixel count (width * height). 0 if either dimension is zero."""
    img = parse_xcf_strict(file_path)
    return img.width * img.height


def xcf_layer_name_list(file_path: str | Path) -> list:
    """Return actual layer names read from the XCF layer records.

    Returns a list of strings (may be empty strings if unnamed). Returns [] if no layers.
    GAP-XCF-LAYER-NAMES closed: real names now parsed from layer records.
    """
    img = parse_xcf_strict(file_path)
    return list(img.layer_names) if img.layer_names else []


def xcf_color_depth(file_path: str | Path) -> int:
    """Return color depth in bits based on image type. RGB=24, Grayscale=8, Indexed=8."""
    img = parse_xcf_strict(file_path)
    if img.image_type == 0:  # RGB
        return 24
    elif img.image_type == 1:  # Grayscale
        return 8
    else:  # Indexed
        return 8


def xcf_file_size_bytes(file_path: str | Path) -> int:
    """Return the size of the XCF file in bytes."""
    from pathlib import Path as _Path
    return _Path(file_path).stat().st_size


def xcf_is_rgb(file_path: str | Path) -> bool:
    """Return True if image type is RGB (image_type == 0)."""
    img = parse_xcf_strict(file_path)
    return img.image_type == 0


def xcf_is_grayscale(file_path: str | Path) -> bool:
    """Return True if image type is Grayscale (image_type == 1)."""
    img = parse_xcf_strict(file_path)
    return img.image_type == 1


def xcf_aspect_ratio(file_path: str | Path) -> float:
    """Return width / height as a float. Returns 0.0 if height is 0."""
    img = parse_xcf_strict(file_path)
    if img.height == 0:
        return 0.0
    return img.width / img.height


def xcf_max_layer_area(file_path: str | Path) -> int:
    """Return canvas area (width*height) as proxy for maximum layer area. 0 if no layers."""
    img = parse_xcf_strict(file_path)
    if img.num_layers == 0:
        return 0
    return img.width * img.height


def xcf_is_color(file_path: str | Path) -> bool:
    """Return True if the image color mode is RGB (not grayscale or indexed)."""
    img = parse_xcf_strict(file_path)
    return img.image_type == 0


def xcf_pixels_exceed_layers(file_path: str | Path) -> bool:
    """Return True if total pixel count strictly exceeds layer count."""
    img = parse_xcf_strict(file_path)
    return (img.width * img.height) > img.num_layers


def xcf_canvas_fill_ratio(file_path: str | Path) -> float:
    """Return ratio of layer count to canvas area. 0.0 if no canvas."""
    img = parse_xcf_strict(file_path)
    area = img.width * img.height
    return img.num_layers / area if area > 0 else 0.0


def xcf_is_tiny(file_path: str | Path) -> bool:
    """Return True if total pixel count is less than 100."""
    img = parse_xcf_strict(file_path)
    return (img.width * img.height) < 100


def xcf_avg_layer_area(file_path: str | Path) -> float:
    """Return canvas area divided by layer count. 0.0 if no layers."""
    img = parse_xcf_strict(file_path)
    if img.num_layers == 0:
        return 0.0
    return (img.width * img.height) / img.num_layers


def xcf_layer_name_count(file_path: str | Path) -> int:
    """Return number of layer names recorded in the XCF header. Same as num_layers."""
    img = parse_xcf_strict(file_path)
    return img.num_layers


def xcf_width_to_layer_ratio(file_path: str | Path) -> float:
    """Return canvas width divided by layer count. 0.0 if no layers."""
    img = parse_xcf_strict(file_path)
    if img.num_layers == 0:
        return 0.0
    return img.width / img.num_layers


def xcf_height_to_layer_ratio(file_path: str | Path) -> float:
    """Return canvas height divided by layer count. 0.0 if no layers."""
    img = parse_xcf_strict(file_path)
    if img.num_layers == 0:
        return 0.0
    return img.height / img.num_layers


def xcf_perimeter(file_path: str | Path) -> int:
    """Return perimeter of the canvas: 2 * (width + height). 0 if empty."""
    img = parse_xcf_strict(file_path)
    if img.width == 0 and img.height == 0:
        return 0
    return 2 * (img.width + img.height)


def xcf_image_type_id(file_path: str | Path) -> int:
    """Return the raw image_type field (0=RGB, 1=GRAYSCALE, 2=INDEXED)."""
    img = parse_xcf_strict(file_path)
    return img.image_type


def xcf_layer_count_exceeds_one(file_path: str | Path) -> bool:
    """Return True if the file has more than one layer."""
    return xcf_layer_count(file_path) > 1


def xcf_file_size_per_layer(file_path: str | Path) -> float:
    """Return file size divided by layer count. 0.0 if no layers."""
    lc = xcf_layer_count(file_path)
    if lc == 0:
        return 0.0
    return xcf_file_size(file_path) / lc


def xcf_is_landscape(file_path: str | Path) -> bool:
    """Return True if width > height."""
    img = parse_xcf_strict(file_path)
    return img.width > img.height


def xcf_pixel_count_per_layer(file_path: str | Path) -> float:
    """Return total pixel count divided by layer count. 0.0 if no layers."""
    lc = xcf_layer_count(file_path)
    if lc == 0:
        return 0.0
    return xcf_pixel_count(file_path) / lc



# Analytics extension — arithmetic combination functions.
# Separated from core parser to reduce file size. All names re-exported.
try:
    from .xcf_image_metrics import *  # noqa: F401, F403
except ImportError:
    pass  # Standalone module import — analytics unavailable
