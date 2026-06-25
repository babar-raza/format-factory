"""
XCF analytics — pure functions extracted from primary codec/parser.
"""
from __future__ import annotations


spec_qname = "xcf:image"
spec_fact_ref = "FACT-XCF-001"
namespace_uri = "urn:gimp:xcf-native"

import os
from pathlib import Path
from typing import Any

from .xcf_parser import parse_xcf_strict, IMAGE_TYPE_NAMES, XcfError


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


def xcf_is_square(file_path: str | Path) -> bool:
    """Return True if width equals height."""
    img = parse_xcf_strict(file_path)
    return img.width == img.height


def xcf_layers_per_pixel(file_path: str | Path) -> float:
    """Return layers / (width * height). 0.0 if no pixels."""
    img = parse_xcf_strict(file_path)
    pixels = img.width * img.height
    return img.num_layers / pixels if pixels > 0 else 0.0


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
