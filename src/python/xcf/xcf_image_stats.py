"""xcf_image_stats.py — Extracted XCF image metric functions.

Split out of xcf_image_metrics.py (TC-PA-017 monolith healing) to keep each source
module under the 800-LOC architecture cap. Pure analytics functions over parsed XCF
images; behavior is unchanged from the original definitions. Base parser names and any
sibling metrics that remain in xcf_image_metrics.py are brought in via the star-import
below. Re-exported from xcf_image_metrics.py so every public name stays importable from
its original path.
"""
from __future__ import annotations

from .xcf_image_metrics import *  # noqa: F401,F403 - base parser/metrics reused at call time


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
