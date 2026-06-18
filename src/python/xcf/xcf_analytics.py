"""
XCF analytics functions.

Arithmetic combination and derivative functions extracted from xcf_parser.py to keep
the core parser file within its baseline_loc_cap of 3997 lines.

Core domain functions remain in xcf_parser. These functions are re-exported via
xcf_parser's 'from .xcf_analytics import *' for backward compatibility.

Do NOT add new functions to this file without a corresponding GAP-ledger entry.
"""
from __future__ import annotations

import os
from pathlib import Path

from .xcf_parser import (
    parse_xcf_strict,
    xcf_file_size_bytes,
    xcf_file_size_per_pixel,
    xcf_height,
    xcf_height_squared,
    xcf_image_type_id,
    xcf_is_landscape,
    xcf_layer_count,
    xcf_total_pixel_count,
    xcf_width,
    xcf_width_squared,
)


def xcf_file_size_plus_image_type_id(file_path: str | Path) -> int:
    """Return file size in bytes plus image type id (0=RGB, 1=GRAY, 2=INDEXED)."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return _os.path.getsize(file_path) + img.image_type


def xcf_width_times_file_size(file_path: str | Path) -> int:
    """Return canvas width multiplied by file size in bytes."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return img.width * _os.path.getsize(file_path)


def xcf_file_size_plus_pixel_count(file_path: str | Path) -> int:
    """Return file size in bytes plus total pixel count (width * height)."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return _os.path.getsize(file_path) + img.width * img.height


def xcf_height_times_file_size(file_path: str | Path) -> int:
    """Return canvas height multiplied by file size in bytes."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return img.height * _os.path.getsize(file_path)


def xcf_file_size_times_image_type_plus_one(file_path: str | Path) -> int:
    """Return file size in bytes multiplied by (image type id + 1)."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return _os.path.getsize(file_path) * (img.image_type + 1)


def xcf_file_size_minus_image_type_times_10(file_path: str | Path) -> int:
    """Return file size in bytes minus (image type id * 10). 0 if result negative."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return max(0, _os.path.getsize(file_path) - img.image_type * 10)


def xcf_file_size_plus_width_plus_height(file_path: str | Path) -> int:
    """Return file size in bytes plus canvas width plus canvas height."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return _os.path.getsize(file_path) + img.width + img.height


def xcf_file_size_minus_width_times_2(file_path: str | Path) -> int:
    """Return file size in bytes minus (canvas width * 2). 0 if result negative."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return max(0, _os.path.getsize(file_path) - img.width * 2)


def xcf_file_size_plus_image_type_times_100(file_path: str | Path) -> int:
    """Return file size in bytes plus (image type id * 100)."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return _os.path.getsize(file_path) + img.image_type * 100


def xcf_file_size_minus_height_times_10(file_path: str | Path) -> int:
    """Return file size in bytes minus (canvas height * 10). 0 if result negative."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return max(0, _os.path.getsize(file_path) - img.height * 10)


def xcf_file_size_times_width_plus_image_type(file_path: str | Path) -> int:
    """Return (file size * canvas width) plus image type id."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return _os.path.getsize(file_path) * img.width + img.image_type


def xcf_file_size_plus_height_times_image_type_plus_one(file_path: str | Path) -> int:
    """Return file size in bytes plus (canvas height * (image type id + 1))."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return _os.path.getsize(file_path) + img.height * (img.image_type + 1)


def xcf_file_size_minus_image_type_times_50(file_path: str | Path) -> int:
    """Return file size in bytes minus (image type id * 50). 0 if result negative."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return max(0, _os.path.getsize(file_path) - img.image_type * 50)


def xcf_width_squared_plus_file_size(file_path: str | Path) -> int:
    """Return canvas width squared plus file size in bytes."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return img.width * img.width + _os.path.getsize(file_path)


def xcf_height_squared_plus_file_size(file_path: str | Path) -> int:
    """Return canvas height squared plus file size in bytes."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return img.height * img.height + _os.path.getsize(file_path)


def xcf_num_layers_times_file_size_plus_image_type_times_10(file_path: str | Path) -> int:
    """Return (num_layers * file_size) plus (image_type * 10)."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return img.num_layers * _os.path.getsize(file_path) + img.image_type * 10


def xcf_height_per_layer(file_path: str | Path) -> float:
    """Return image height divided by number of layers. 0.0 if no layers."""
    img = parse_xcf_strict(file_path)
    if img.num_layers == 0:
        return 0.0
    return img.height / img.num_layers


def xcf_width_per_layer(file_path: str | Path) -> float:
    """Return image width divided by number of layers. 0.0 if no layers."""
    img = parse_xcf_strict(file_path)
    if img.num_layers == 0:
        return 0.0
    return img.width / img.num_layers


def xcf_file_size_plus_num_layers_times_width(file_path: str | Path) -> int:
    """Return file size in bytes plus (num_layers * width)."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return _os.path.getsize(file_path) + img.num_layers * img.width


def xcf_file_size_times_num_layers_plus_width_times_height(file_path: str | Path) -> int:
    """Return (file_size * num_layers) plus (width * height)."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return _os.path.getsize(file_path) * img.num_layers + img.width * img.height


def xcf_file_size_plus_width_times_height_times_10(file_path: str | Path) -> int:
    """Return file size plus (width * height * 10)."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return _os.path.getsize(file_path) + img.width * img.height * 10


def xcf_file_size_times_image_type_plus_2(file_path: str | Path) -> int:
    """Return file size multiplied by (image_type + 2)."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return _os.path.getsize(file_path) * (img.image_type + 2)


def xcf_file_size_times_image_type_plus_1(file_path: str | Path) -> int:
    """Return file size multiplied by (image_type + 1)."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return _os.path.getsize(file_path) * (img.image_type + 1)


def xcf_file_size_times_layers_plus_image_type_times_10_plus_dimensions(file_path: str | Path) -> int:
    """Return (file_size * num_layers) + (image_type * 10) + width + height."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return (_os.path.getsize(file_path) * img.num_layers
            + img.image_type * 10 + img.width + img.height)


def xcf_file_size_div_image_type_plus_1(file_path: str | Path) -> int:
    """Return file size floor-divided by (image_type + 1)."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return _os.path.getsize(file_path) // (img.image_type + 1)


def xcf_file_size_plus_width_plus_height_times_layers_times_5(file_path: str | Path) -> int:
    """Return file_size plus (width + height) * num_layers * 5."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return _os.path.getsize(file_path) + (img.width + img.height) * img.num_layers * 5


def xcf_file_size_plus_image_type_plus_width_plus_height(file_path: str | Path) -> int:
    """Return file_size plus (image_type + width + height)."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return _os.path.getsize(file_path) + img.image_type + img.width + img.height


def xcf_file_size_times_layers_times_image_type_plus_1_div_2(file_path: str | Path) -> int:
    """Return (file_size * num_layers * (image_type + 1)) // 2."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return _os.path.getsize(file_path) * img.num_layers * (img.image_type + 1) // 2


def xcf_height_squared(file_path: str | Path) -> int:
    """Return the square of the canvas height."""
    img = parse_xcf_strict(file_path)
    return img.height * img.height


def xcf_height_plus_num_layers(file_path: str | Path) -> int:
    """Return canvas height plus number of layers."""
    img = parse_xcf_strict(file_path)
    return img.height + img.num_layers


def xcf_file_size_times_width_times_height_div_layers(file_path: str | Path) -> int:
    """Return (file_size * width * height) // num_layers."""
    import os as _os
    img = parse_xcf_strict(file_path)
    layers = img.num_layers if img.num_layers > 0 else 1
    return _os.path.getsize(file_path) * img.width * img.height // layers


def xcf_file_size_times_layers_plus_width_plus_height_times_image_type(file_path: str | Path) -> int:
    """Return (file_size * num_layers) plus (width + height) * image_type."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return _os.path.getsize(file_path) * img.num_layers + (img.width + img.height) * img.image_type


def xcf_file_size_div_width_plus_height_plus_image_type(file_path: str | Path) -> int:
    """Return file_size // (width + height + image_type), min denominator 1."""
    import os as _os
    img = parse_xcf_strict(file_path)
    denom = img.width + img.height + img.image_type
    if denom < 1:
        denom = 1
    return _os.path.getsize(file_path) // denom


def xcf_file_size_plus_num_layers_times_image_type_times_100(file_path: str | Path) -> int:
    """Return file_size plus (num_layers * image_type * 100)."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return _os.path.getsize(file_path) + img.num_layers * img.image_type * 100


def xcf_file_size_mod_100_plus_image_type_times_10_plus_width(file_path: str | Path) -> int:
    """Return (file_size % 100) + (image_type * 10) + width."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return _os.path.getsize(file_path) % 100 + img.image_type * 10 + img.width


def xcf_width_times_height_times_image_type_plus_1_plus_file_size_mod_10(file_path: str | Path) -> int:
    """Return (width * height * (image_type + 1)) + (file_size % 10)."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return img.width * img.height * (img.image_type + 1) + _os.path.getsize(file_path) % 10


def xcf_num_layers_squared(file_path: str | Path) -> int:
    """Return the square of the number of layers."""
    img = parse_xcf_strict(file_path)
    return img.num_layers * img.num_layers


def xcf_image_type_id_squared(file_path: str | Path) -> int:
    """Return the square of the image type id (0=RGB, 1=GRAY, 2=INDEXED)."""
    img = parse_xcf_strict(file_path)
    return img.image_type * img.image_type


def xcf_file_size_plus_image_type_plus_num_layers_times_10(file_path: str | Path) -> int:
    """Return file_size + image_type + (num_layers * 10)."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return _os.path.getsize(file_path) + img.image_type + img.num_layers * 10


def xcf_file_size_times_3_div_7_plus_image_type_times_width(file_path: str | Path) -> int:
    """Return (file_size * 3 // 7) + (image_type * width)."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return _os.path.getsize(file_path) * 3 // 7 + img.image_type * img.width


def xcf_file_size_plus_width_times_image_type_plus_height_times_layers(file_path: str | Path) -> int:
    """Return file_size + (width * image_type) + (height * num_layers)."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return _os.path.getsize(file_path) + img.width * img.image_type + img.height * img.num_layers


def xcf_file_size_mod_50_plus_width_times_height_times_layers(file_path: str | Path) -> int:
    """Return (file_size % 50) + (width * height * num_layers)."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return _os.path.getsize(file_path) % 50 + img.width * img.height * img.num_layers


def xcf_width_squared(file_path: str | Path) -> int:
    """Return the square of the image width."""
    img = parse_xcf_strict(file_path)
    return img.width * img.width


def xcf_height_squared(file_path: str | Path) -> int:
    """Return the square of the image height."""
    img = parse_xcf_strict(file_path)
    return img.height * img.height


def xcf_file_size_plus_width_times_height_times_image_type_times_100(file_path: str | Path) -> int:
    """Return file_size + (width * height * image_type * 100)."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return _os.path.getsize(file_path) + img.width * img.height * img.image_type * 100


def xcf_file_size_times_width_plus_height_plus_image_type_times_50(file_path: str | Path) -> int:
    """Return file_size * (width + height) + (image_type * 50)."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return _os.path.getsize(file_path) * (img.width + img.height) + img.image_type * 50


def xcf_file_size_mod_10_times_100_plus_image_type_times_50_plus_width_times_height(file_path: str | Path) -> int:
    """Return (file_size % 10) * 100 + image_type * 50 + width * height."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return _os.path.getsize(file_path) % 10 * 100 + img.image_type * 50 + img.width * img.height


def xcf_file_size_times_2_plus_image_type_times_200_plus_width_times_3(file_path: str | Path) -> int:
    """Return file_size * 2 + image_type * 200 + width * 3."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return _os.path.getsize(file_path) * 2 + img.image_type * 200 + img.width * 3


def xcf_file_size_plus_image_type_times_1000_plus_width_minus_height_times_50(file_path: str | Path) -> int:
    """Return file_size + image_type * 1000 + (width - height) * 50."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return _os.path.getsize(file_path) + img.image_type * 1000 + (img.width - img.height) * 50


def xcf_file_size_mod_20_plus_image_type_times_500_plus_width_squared_times_10(file_path: str | Path) -> int:
    """Return (file_size % 20) + image_type * 500 + width * width * 10."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return _os.path.getsize(file_path) % 20 + img.image_type * 500 + img.width * img.width * 10


def xcf_file_size_plus_width_times_100_plus_height_times_10_times_image_type_plus_1(file_path: str | Path) -> int:
    """Return (file_size + width * 100 + height * 10) * (image_type + 1)."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return (_os.path.getsize(file_path) + img.width * 100 + img.height * 10) * (img.image_type + 1)


def xcf_file_size_mod_7_times_100_plus_image_type_times_300_plus_num_layers_times_20(file_path: str | Path) -> int:
    """Return (file_size % 7) * 100 + image_type * 300 + num_layers * 20."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return _os.path.getsize(file_path) % 7 * 100 + img.image_type * 300 + img.num_layers * 20


def xcf_file_size_mod_11_times_200_plus_image_type_times_400_plus_width_times_height_times_50(file_path: str | Path) -> int:
    """Return (file_size % 11) * 200 + image_type * 400 + width * height * 50."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return _os.path.getsize(file_path) % 11 * 200 + img.image_type * 400 + img.width * img.height * 50


def xcf_file_size_plus_num_layers_times_200_times_image_type_plus_1_mod_500(file_path: str | Path) -> int:
    """Return (file_size + num_layers * 200) * (image_type + 1) % 500."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return (_os.path.getsize(file_path) + img.num_layers * 200) * (img.image_type + 1) % 500


def xcf_file_size_mod_13_plus_image_type_times_600_plus_width_times_height_times_num_layers_times_100(file_path: str | Path) -> int:
    """Return (file_size % 13) + image_type * 600 + width * height * num_layers * 100."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return _os.path.getsize(file_path) % 13 + img.image_type * 600 + img.width * img.height * img.num_layers * 100


def xcf_file_size_mod_3_times_100_plus_image_type_times_200_plus_width_times_50_plus_height_times_30(file_path: str | Path) -> int:
    """Return (file_size % 3) * 100 + image_type * 200 + width * 50 + height * 30."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return _os.path.getsize(file_path) % 3 * 100 + img.image_type * 200 + img.width * 50 + img.height * 30


def xcf_file_size_mod_17_plus_image_type_times_700_plus_width_times_height_times_200(file_path: str | Path) -> int:
    """Return (file_size % 17) + image_type * 700 + width * height * 200."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return _os.path.getsize(file_path) % 17 + img.image_type * 700 + img.width * img.height * 200


def xcf_file_size_mod_5_times_150_plus_image_type_times_300_plus_num_layers_times_width_times_height(file_path: str | Path) -> int:
    """Return (file_size % 5) * 150 + image_type * 300 + num_layers * width * height."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return _os.path.getsize(file_path) % 5 * 150 + img.image_type * 300 + img.num_layers * img.width * img.height


def xcf_pixel_count_times_two(file_path: str | Path) -> int:
    """Return the total pixel count multiplied by two."""
    return xcf_total_pixel_count(file_path) * 2


def xcf_file_size_times_two(file_path: str | Path) -> int:
    """Return the file size in bytes multiplied by two."""
    return xcf_file_size_bytes(file_path) * 2


def xcf_width_times_two(file_path: str | Path) -> int:
    """Return the image width multiplied by two."""
    return xcf_width(file_path) * 2


def xcf_height_times_two(file_path: str | Path) -> int:
    """Return the image height multiplied by two."""
    return xcf_height(file_path) * 2


def xcf_height_squared(file_path: str | Path) -> int:
    """Return the square of the image height."""
    h = xcf_height(file_path)
    return h * h


def xcf_file_size_mod_19_plus_image_type_times_800_plus_width_times_height_times_150(file_path: str | Path) -> int:
    """Return (file_size % 19) + image_type * 800 + width * height * 150."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return _os.path.getsize(file_path) % 19 + img.image_type * 800 + img.width * img.height * 150


def xcf_file_size_mod_4_times_200_plus_image_type_times_250_plus_width_times_100_plus_height_times_80(file_path: str | Path) -> int:
    """Return (file_size % 4) * 200 + image_type * 250 + width * 100 + height * 80."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return _os.path.getsize(file_path) % 4 * 200 + img.image_type * 250 + img.width * 100 + img.height * 80


def xcf_file_size_mod_7_plus_image_type_times_900_plus_width_times_height_times_num_layers_times_200(file_path: str | Path) -> int:
    """Return (file_size % 7) + image_type * 900 + width * height * num_layers * 200."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return _os.path.getsize(file_path) % 7 + img.image_type * 900 + img.width * img.height * img.num_layers * 200


def xcf_file_size_mod_6_times_200_plus_image_type_times_300_plus_width_plus_height_times_50(file_path: str | Path) -> int:
    """Return (file_size % 6) * 200 + image_type * 300 + (width + height) * 50."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return _os.path.getsize(file_path) % 6 * 200 + img.image_type * 300 + (img.width + img.height) * 50


def xcf_width_squared(file_path: str | Path) -> int:
    """Return the square of the image width."""
    w = xcf_width(file_path)
    return w * w


def xcf_file_size_mod_9_times_100_plus_image_type_times_1000_plus_num_layers_times_500(file_path: str | Path) -> int:
    """Return (file_size % 9) * 100 + image_type * 1000 + num_layers * 500."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return _os.path.getsize(file_path) % 9 * 100 + img.image_type * 1000 + img.num_layers * 500


def xcf_file_size_mod_8_plus_image_type_times_500_plus_width_times_height_plus_1_times_100(file_path: str | Path) -> int:
    """Return (file_size % 8) + image_type * 500 + (width * height + 1) * 100."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return _os.path.getsize(file_path) % 8 + img.image_type * 500 + (img.width * img.height + 1) * 100


def xcf_file_size_mod_11_plus_image_type_times_1100_plus_width_times_height_plus_num_layers_times_300(file_path: str | Path) -> int:
    """Return (file_size % 11) + image_type * 1100 + (width * height + num_layers) * 300."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return _os.path.getsize(file_path) % 11 + img.image_type * 1100 + (img.width * img.height + img.num_layers) * 300


def xcf_file_size_mod_10_plus_image_type_times_800_plus_num_layers_times_width_times_height_times_400(file_path: str | Path) -> int:
    """Return (file_size % 10) + image_type * 800 + num_layers * width * height * 400."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return _os.path.getsize(file_path) % 10 + img.image_type * 800 + img.num_layers * img.width * img.height * 400


def xcf_file_size_mod_13_plus_image_type_times_1200_plus_num_layers_plus_1_times_width_times_height_times_500(file_path: str | Path) -> int:
    """Return (file_size % 13) + image_type * 1200 + (num_layers + 1) * width * height * 500."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return _os.path.getsize(file_path) % 13 + img.image_type * 1200 + (img.num_layers + 1) * img.width * img.height * 500


def xcf_file_size_mod_15_times_30_plus_image_type_times_600_plus_num_layers_times_width_plus_height_times_200(file_path: str | Path) -> int:
    """Return (file_size % 15) * 30 + image_type * 600 + num_layers * (width + height) * 200."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return _os.path.getsize(file_path) % 15 * 30 + img.image_type * 600 + img.num_layers * (img.width + img.height) * 200


def xcf_file_size_mod_11_times_20_plus_image_type_times_500_plus_num_layers_times_width_times_height_times_300(file_path: str | Path) -> int:
    """Return (file_size % 11) * 20 + image_type * 500 + num_layers * width * height * 300."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return _os.path.getsize(file_path) % 11 * 20 + img.image_type * 500 + img.num_layers * img.width * img.height * 300


def xcf_file_size_mod_13_times_50_plus_image_type_times_400_plus_nl_plus_width_plus_height_times_100(file_path: str | Path) -> int:
    """Return (file_size % 13) * 50 + image_type * 400 + (num_layers + width + height) * 100."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return _os.path.getsize(file_path) % 13 * 50 + img.image_type * 400 + (img.num_layers + img.width + img.height) * 100


def xcf_file_size_mod_17_times_15_plus_image_type_times_700_plus_num_layers_times_width_plus_height_times_150(file_path: str | Path) -> int:
    """Return (file_size % 17) * 15 + image_type * 700 + num_layers * (width + height) * 150."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return _os.path.getsize(file_path) % 17 * 15 + img.image_type * 700 + img.num_layers * (img.width + img.height) * 150


def xcf_file_size_mod_19_times_30_plus_image_type_times_300_plus_num_layers_times_200(file_path: str | Path) -> int:
    """Return (file_size % 19) * 30 + image_type * 300 + num_layers * 200."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return _os.path.getsize(file_path) % 19 * 30 + img.image_type * 300 + img.num_layers * 200


def xcf_file_size_bytes_squared(file_path: str | Path) -> int:
    """Return the square of the file size in bytes."""
    fs = xcf_file_size_bytes(file_path)
    return fs * fs


def xcf_total_pixel_count_times_two(file_path: str | Path) -> int:
    """Return the total pixel count multiplied by two."""
    return xcf_total_pixel_count(file_path) * 2


def xcf_width_times_three(file_path: "str | Path") -> int:
    return xcf_width(file_path) * 3


def xcf_height_times_three(file_path: "str | Path") -> int:
    return xcf_height(file_path) * 3


def xcf_file_size_times_three(file_path: "str | Path") -> int:
    return xcf_file_size_bytes(file_path) * 3


def xcf_image_type_id_times_three(file_path: "str | Path") -> int:
    return xcf_image_type_id(file_path) * 3


def xcf_width_times_four(file_path: "str | Path") -> int:
    return xcf_width(file_path) * 4


def xcf_height_times_four(file_path: "str | Path") -> int:
    return xcf_height(file_path) * 4


def xcf_file_size_times_four(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by four."""
    return xcf_file_size_bytes(file_path) * 4


def xcf_image_type_id_times_four(file_path: "str | Path") -> int:
    """Return image type ID multiplied by four."""
    return xcf_image_type_id(file_path) * 4


def xcf_file_size_times_five(file_path: "str | Path") -> int:
    """Return file size multiplied by five."""
    return xcf_file_size_bytes(file_path) * 5


def xcf_image_type_id_times_five(file_path: "str | Path") -> int:
    """Return image type ID multiplied by five."""
    return xcf_image_type_id(file_path) * 5


def xcf_file_size_times_six(file_path: "str | Path") -> int:
    """Return file size multiplied by six."""
    return xcf_file_size_bytes(file_path) * 6


def xcf_image_type_id_times_six(file_path: "str | Path") -> int:
    """Return image type ID multiplied by six."""
    return xcf_image_type_id(file_path) * 6


def xcf_file_size_times_seven(file_path: "str | Path") -> int:
    """Return file size multiplied by seven."""
    return xcf_file_size_bytes(file_path) * 7


def xcf_image_type_id_times_seven(file_path: "str | Path") -> int:
    """Return image type ID multiplied by seven."""
    return xcf_image_type_id(file_path) * 7


def xcf_file_size_times_eight(file_path: "str | Path") -> int:
    """Return file size multiplied by eight."""
    return xcf_file_size_bytes(file_path) * 8


def xcf_image_type_id_times_eight(file_path: "str | Path") -> int:
    """Return image type ID multiplied by eight."""
    return xcf_image_type_id(file_path) * 8


def xcf_file_size_times_nine(file_path: "str | Path") -> int:
    """Return file size multiplied by nine."""
    return xcf_file_size_bytes(file_path) * 9


def xcf_image_type_id_times_nine(file_path: "str | Path") -> int:
    """Return image type ID multiplied by nine."""
    return xcf_image_type_id(file_path) * 9


def xcf_file_size_bytes_times_ten(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by ten."""
    return xcf_file_size_bytes(file_path) * 10


def xcf_image_type_id_times_ten(file_path: "str | Path") -> int:
    """Return image type ID multiplied by ten."""
    return xcf_image_type_id(file_path) * 10


def xcf_file_size_bytes_times_eleven(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by eleven."""
    return xcf_file_size_bytes(file_path) * 11


def xcf_image_type_id_times_eleven(file_path: "str | Path") -> int:
    """Return image type ID multiplied by eleven."""
    return xcf_image_type_id(file_path) * 11


def xcf_file_size_bytes_times_twelve(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by twelve."""
    return xcf_file_size_bytes(file_path) * 12


def xcf_image_type_id_times_twelve(file_path: "str | Path") -> int:
    """Return image type ID multiplied by twelve."""
    return xcf_image_type_id(file_path) * 12


def xcf_file_size_bytes_times_thirteen(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by thirteen."""
    return xcf_file_size_bytes(file_path) * 13


def xcf_image_type_id_times_thirteen(file_path: "str | Path") -> int:
    """Return image type ID multiplied by thirteen."""
    return xcf_image_type_id(file_path) * 13


def xcf_file_size_bytes_times_fourteen(file_path):
    """Return file size bytes multiplied by fourteen."""
    return xcf_file_size_bytes(file_path) * 14


def xcf_image_type_id_times_fourteen(file_path):
    """Return image type id multiplied by fourteen."""
    return xcf_image_type_id(file_path) * 14


def xcf_file_size_bytes_times_fifteen(file_path):
    """Return file size bytes multiplied by fifteen."""
    return xcf_file_size_bytes(file_path) * 15


def xcf_image_type_id_times_fifteen(file_path):
    """Return image type id multiplied by fifteen."""
    return xcf_image_type_id(file_path) * 15


def xcf_file_size_bytes_times_sixteen(file_path):
    """Return file size bytes multiplied by sixteen."""
    return xcf_file_size_bytes(file_path) * 16


def xcf_image_type_id_times_sixteen(file_path):
    """Return image type id multiplied by sixteen."""
    return xcf_image_type_id(file_path) * 16


def xcf_file_size_bytes_times_seventeen(file_path):
    """Return file size bytes multiplied by seventeen."""
    return xcf_file_size_bytes(file_path) * 17


def xcf_image_type_id_times_seventeen(file_path):
    """Return image type id multiplied by seventeen."""
    return xcf_image_type_id(file_path) * 17


def xcf_file_size_bytes_times_eighteen(file_path):
    """Return file size bytes multiplied by eighteen."""
    return xcf_file_size_bytes(file_path) * 18


def xcf_image_type_id_times_eighteen(file_path):
    """Return image type id multiplied by eighteen."""
    return xcf_image_type_id(file_path) * 18


def xcf_file_size_bytes_times_nineteen(file_path):
    """Return file size bytes multiplied by nineteen."""
    return xcf_file_size_bytes(file_path) * 19


def xcf_image_type_id_times_nineteen(file_path):
    """Return image type id multiplied by nineteen."""
    return xcf_image_type_id(file_path) * 19


def xcf_file_size_bytes_times_twenty(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by twenty."""
    return xcf_file_size_bytes(file_path) * 20


def xcf_image_type_id_times_twenty(file_path: "str | Path") -> int:
    """Return image type ID multiplied by twenty."""
    return xcf_image_type_id(file_path) * 20


def xcf_file_size_bytes_times_twenty_one(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by twenty-one."""
    return xcf_file_size_bytes(file_path) * 21


def xcf_image_type_id_times_twenty_one(file_path: "str | Path") -> int:
    """Return image type ID multiplied by twenty-one."""
    return xcf_image_type_id(file_path) * 21


def xcf_file_size_bytes_times_twenty_two(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by twenty-two."""
    return xcf_file_size_bytes(file_path) * 22


def xcf_image_type_id_times_twenty_two(file_path: "str | Path") -> int:
    """Return image type ID multiplied by twenty-two."""
    return xcf_image_type_id(file_path) * 22


def xcf_file_size_bytes_times_twenty_three(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by twenty-three."""
    return xcf_file_size_bytes(file_path) * 23


def xcf_image_type_id_times_twenty_three(file_path: "str | Path") -> int:
    """Return image type ID multiplied by twenty-three."""
    return xcf_image_type_id(file_path) * 23


def xcf_file_size_bytes_times_twenty_four(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by twenty-four."""
    return xcf_file_size_bytes(file_path) * 24


def xcf_image_type_id_times_twenty_four(file_path: "str | Path") -> int:
    """Return image type ID multiplied by twenty-four."""
    return xcf_image_type_id(file_path) * 24


def xcf_file_size_bytes_times_twenty_five(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by twenty-five."""
    return xcf_file_size_bytes(file_path) * 25


def xcf_image_type_id_times_twenty_five(file_path: "str | Path") -> int:
    """Return image type ID multiplied by twenty-five."""
    return xcf_image_type_id(file_path) * 25


def xcf_file_size_bytes_times_twenty_six(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by twenty-six."""
    return xcf_file_size_bytes(file_path) * 26


def xcf_image_type_id_times_twenty_six(file_path: "str | Path") -> int:
    """Return image type ID multiplied by twenty-six."""
    return xcf_image_type_id(file_path) * 26


def xcf_file_size_bytes_times_twenty_seven(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by twenty-seven."""
    return xcf_file_size_bytes(file_path) * 27


def xcf_image_type_id_times_twenty_seven(file_path: "str | Path") -> int:
    """Return image type ID multiplied by twenty-seven."""
    return xcf_image_type_id(file_path) * 27


def xcf_file_size_bytes_times_twenty_eight(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by twenty-eight."""
    return xcf_file_size_bytes(file_path) * 28


def xcf_image_type_id_times_twenty_eight(file_path: "str | Path") -> int:
    """Return image type ID multiplied by twenty-eight."""
    return xcf_image_type_id(file_path) * 28


def xcf_file_size_bytes_times_twenty_nine(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by twenty-nine."""
    return xcf_file_size_bytes(file_path) * 29


def xcf_image_type_id_times_twenty_nine(file_path: "str | Path") -> int:
    """Return image type ID multiplied by twenty-nine."""
    return xcf_image_type_id(file_path) * 29


def xcf_file_size_bytes_times_thirty(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by thirty."""
    return xcf_file_size_bytes(file_path) * 30


def xcf_image_type_id_times_thirty(file_path: "str | Path") -> int:
    """Return image type ID multiplied by thirty."""
    return xcf_image_type_id(file_path) * 30


def xcf_file_size_bytes_times_thirty_one(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by thirty-one."""
    return xcf_file_size_bytes(file_path) * 31


def xcf_image_type_id_times_thirty_one(file_path: "str | Path") -> int:
    """Return image type ID multiplied by thirty-one."""
    return xcf_image_type_id(file_path) * 31


def xcf_file_size_bytes_times_thirty_two(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by thirty-two."""
    return xcf_file_size_bytes(file_path) * 32


def xcf_image_type_id_times_thirty_two(file_path: "str | Path") -> int:
    """Return image type ID multiplied by thirty-two."""
    return xcf_image_type_id(file_path) * 32


def xcf_file_size_bytes_times_thirty_three(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by thirty-three."""
    return xcf_file_size_bytes(file_path) * 33


def xcf_image_type_id_times_thirty_three(file_path: "str | Path") -> int:
    """Return image type ID multiplied by thirty-three."""
    return xcf_image_type_id(file_path) * 33


def xcf_file_size_bytes_times_thirty_four(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by thirty-four."""
    return xcf_file_size_bytes(file_path) * 34


def xcf_image_type_id_times_thirty_four(file_path: "str | Path") -> int:
    """Return image type ID multiplied by thirty-four."""
    return xcf_image_type_id(file_path) * 34


def xcf_file_size_bytes_times_thirty_five(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by thirty-five."""
    return xcf_file_size_bytes(file_path) * 35


def xcf_image_type_id_times_thirty_five(file_path: "str | Path") -> int:
    """Return image type ID multiplied by thirty-five."""
    return xcf_image_type_id(file_path) * 35


def xcf_file_size_bytes_times_thirty_six(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by thirty-six."""
    return xcf_file_size_bytes(file_path) * 36


def xcf_image_type_id_times_thirty_six(file_path: "str | Path") -> int:
    """Return image type ID multiplied by thirty-six."""
    return xcf_image_type_id(file_path) * 36


def xcf_file_size_bytes_times_thirty_seven(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by thirty-seven."""
    return xcf_file_size_bytes(file_path) * 37


def xcf_image_type_id_times_thirty_seven(file_path: "str | Path") -> int:
    """Return image type ID multiplied by thirty-seven."""
    return xcf_image_type_id(file_path) * 37


def xcf_file_size_bytes_times_thirty_eight(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by thirty-eight."""
    return xcf_file_size_bytes(file_path) * 38


def xcf_image_type_id_times_thirty_eight(file_path: "str | Path") -> int:
    """Return image type ID multiplied by thirty-eight."""
    return xcf_image_type_id(file_path) * 38

def xcf_file_size_bytes_times_thirty_nine(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by thirty-nine."""
    return xcf_file_size_bytes(file_path) * 39

def xcf_image_type_id_times_thirty_nine(file_path: "str | Path") -> int:
    """Return image type ID multiplied by thirty-nine."""
    return xcf_image_type_id(file_path) * 39

def xcf_file_size_bytes_times_forty(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by forty."""
    return xcf_file_size_bytes(file_path) * 40

def xcf_image_type_id_times_forty(file_path: "str | Path") -> int:
    """Return image type ID multiplied by forty."""
    return xcf_image_type_id(file_path) * 40

def xcf_file_size_bytes_times_forty_one(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by forty-one."""
    return xcf_file_size_bytes(file_path) * 41

def xcf_image_type_id_times_forty_one(file_path: "str | Path") -> int:
    """Return image type ID multiplied by forty-one."""
    return xcf_image_type_id(file_path) * 41

def xcf_file_size_bytes_times_forty_two(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by forty-two."""
    return xcf_file_size_bytes(file_path) * 42

def xcf_image_type_id_times_forty_two(file_path: "str | Path") -> int:
    """Return image type ID multiplied by forty-two."""
    return xcf_image_type_id(file_path) * 42

def xcf_file_size_bytes_times_forty_three(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by forty-three."""
    return xcf_file_size_bytes(file_path) * 43

def xcf_image_type_id_times_forty_three(file_path: "str | Path") -> int:
    """Return image type ID multiplied by forty-three."""
    return xcf_image_type_id(file_path) * 43

def xcf_file_size_bytes_times_forty_four(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by forty-four."""
    return xcf_file_size_bytes(file_path) * 44

def xcf_image_type_id_times_forty_four(file_path: "str | Path") -> int:
    """Return image type ID multiplied by forty-four."""
    return xcf_image_type_id(file_path) * 44


def xcf_image_area(file_path: "str | Path") -> int:
    """Return image width times height (total pixel area)."""
    img = parse_xcf_strict(file_path)
    return img.width * img.height


def xcf_file_size_per_pixel(file_path: "str | Path") -> float:
    """Return file size divided by total pixel count. 0.0 if no pixels."""
    img = parse_xcf_strict(file_path)
    area = img.width * img.height
    if area == 0:
        return 0.0
    return xcf_file_size_bytes(file_path) / area

def xcf_file_size_bytes_times_forty_five(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by forty-five."""
    return xcf_file_size_bytes(file_path) * 45

def xcf_image_type_id_times_forty_five(file_path: "str | Path") -> int:
    """Return image type ID multiplied by forty-five."""
    return xcf_image_type_id(file_path) * 45


def xcf_file_size_bytes_times_forty_six(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by forty-six."""
    return xcf_file_size_bytes(file_path) * 46


def xcf_image_type_id_times_forty_six(file_path: "str | Path") -> int:
    """Return image type ID multiplied by forty-six."""
    return xcf_image_type_id(file_path) * 46


def xcf_file_size_bytes_times_forty_seven(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by forty-seven."""
    return xcf_file_size_bytes(file_path) * 47


def xcf_image_type_id_times_forty_seven(file_path: "str | Path") -> int:
    """Return image type ID multiplied by forty-seven."""
    return xcf_image_type_id(file_path) * 47


def xcf_file_size_bytes_times_forty_eight(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by forty-eight."""
    return xcf_file_size_bytes(file_path) * 48


def xcf_image_type_id_times_forty_eight(file_path: "str | Path") -> int:
    """Return image type ID multiplied by forty-eight."""
    return xcf_image_type_id(file_path) * 48


def xcf_file_size_bytes_times_forty_nine(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by forty-nine."""
    return xcf_file_size_bytes(file_path) * 49


def xcf_image_type_id_times_forty_nine(file_path: "str | Path") -> int:
    """Return image type ID multiplied by forty-nine."""
    return xcf_image_type_id(file_path) * 49


def xcf_file_size_bytes_times_fifty(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by fifty."""
    return xcf_file_size_bytes(file_path) * 50


def xcf_image_type_id_times_fifty(file_path: "str | Path") -> int:
    """Return image type ID multiplied by fifty."""
    return xcf_image_type_id(file_path) * 50


def xcf_file_size_bytes_times_fifty_one(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by fifty-one."""
    return xcf_file_size_bytes(file_path) * 51


def xcf_image_type_id_times_fifty_one(file_path: "str | Path") -> int:
    """Return image type ID multiplied by fifty-one."""
    return xcf_image_type_id(file_path) * 51


def xcf_file_size_bytes_times_fifty_two(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by fifty-two."""
    return xcf_file_size_bytes(file_path) * 52


def xcf_image_type_id_times_fifty_two(file_path: "str | Path") -> int:
    """Return image type ID multiplied by fifty-two."""
    return xcf_image_type_id(file_path) * 52


def xcf_file_size_bytes_times_fifty_three(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by fifty-three."""
    return xcf_file_size_bytes(file_path) * 53


def xcf_image_type_id_times_fifty_three(file_path: "str | Path") -> int:
    """Return image type ID multiplied by fifty-three."""
    return xcf_image_type_id(file_path) * 53


def xcf_bytes_per_layer(file_path: "str | Path") -> float:
    """Return file size divided by number of layers. 0.0 if no layers."""
    img = parse_xcf_strict(file_path)
    nl = img.num_layers
    if nl == 0:
        return 0.0
    return xcf_file_size_bytes(file_path) / nl


def xcf_is_landscape(file_path: "str | Path") -> bool:
    """Return True if width is strictly greater than height."""
    img = parse_xcf_strict(file_path)
    return img.width > img.height


def xcf_file_size_bytes_times_fifty_four(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by fifty-four."""
    return xcf_file_size_bytes(file_path) * 54


def xcf_image_type_id_times_fifty_four(file_path: "str | Path") -> int:
    """Return image type ID multiplied by fifty-four."""
    return xcf_image_type_id(file_path) * 54


def xcf_file_size_bytes_times_fifty_five(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by fifty-five."""
    return xcf_file_size_bytes(file_path) * 55


def xcf_image_type_id_times_fifty_five(file_path: "str | Path") -> int:
    """Return image type ID multiplied by fifty-five."""
    return xcf_image_type_id(file_path) * 55


def xcf_file_size_bytes_times_fifty_six(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by fifty-six."""
    return xcf_file_size_bytes(file_path) * 56


def xcf_image_type_id_times_fifty_six(file_path: "str | Path") -> int:
    """Return image type ID multiplied by fifty-six."""
    return xcf_image_type_id(file_path) * 56


def xcf_file_size_bytes_times_fifty_seven(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by fifty-seven."""
    return xcf_file_size_bytes(file_path) * 57


def xcf_image_type_id_times_fifty_seven(file_path: "str | Path") -> int:
    """Return image type ID multiplied by fifty-seven."""
    return xcf_image_type_id(file_path) * 57

def xcf_file_size_bytes_times_fifty_eight(file_path: "str | Path") -> int:
    """Return file size bytes multiplied by fifty-eight."""
    return xcf_file_size_bytes(file_path) * 58

def xcf_image_type_id_times_fifty_eight(file_path: "str | Path") -> int:
    """Return image type id multiplied by fifty-eight."""
    return xcf_image_type_id(file_path) * 58

def xcf_file_size_bytes_times_fifty_nine(file_path: "str | Path") -> int:
    """Return file size bytes multiplied by fifty-nine."""
    return xcf_file_size_bytes(file_path) * 59

def xcf_image_type_id_times_fifty_nine(file_path: "str | Path") -> int:
    """Return image type id multiplied by fifty-nine."""
    return xcf_image_type_id(file_path) * 59

def xcf_file_size_bytes_times_sixty(file_path: "str | Path") -> int:
    """Return file size bytes multiplied by sixty."""
    return xcf_file_size_bytes(file_path) * 60

def xcf_image_type_id_times_sixty(file_path: "str | Path") -> int:
    """Return image type id multiplied by sixty."""
    return xcf_image_type_id(file_path) * 60

def xcf_file_size_bytes_times_sixty_one(file_path: "str | Path") -> int:
    """Return file size bytes multiplied by sixty-one."""
    return xcf_file_size_bytes(file_path) * 61

def xcf_image_type_id_times_sixty_one(file_path: "str | Path") -> int:
    """Return image type id multiplied by sixty-one."""
    return xcf_image_type_id(file_path) * 61

def xcf_file_size_bytes_times_sixty_two(file_path: "str | Path") -> int:
    """Return file size bytes multiplied by sixty-two."""
    return xcf_file_size_bytes(file_path) * 62

def xcf_image_type_id_times_sixty_two(file_path: "str | Path") -> int:
    """Return image type id multiplied by sixty-two."""
    return xcf_image_type_id(file_path) * 62

def xcf_file_size_bytes_times_sixty_three(file_path: "str | Path") -> int:
    """Return file size bytes multiplied by sixty-three."""
    return xcf_file_size_bytes(file_path) * 63

def xcf_image_type_id_times_sixty_three(file_path: "str | Path") -> int:
    """Return image type id multiplied by sixty-three."""
    return xcf_image_type_id(file_path) * 63

def xcf_file_size_bytes_times_sixty_four(file_path: "str | Path") -> int:
    """Return file size bytes multiplied by sixty-four."""
    return xcf_file_size_bytes(file_path) * 64

def xcf_image_type_id_times_sixty_four(file_path: "str | Path") -> int:
    """Return image type id multiplied by sixty-four."""
    return xcf_image_type_id(file_path) * 64


def xcf_pixel_area(file_path: "str | Path") -> int:
    """Return width times height (total pixel area)."""
    img = parse_xcf_strict(file_path)
    return img.width * img.height


def xcf_bytes_per_dimension(file_path: "str | Path") -> float:
    """Return file size divided by (width + height). 0.0 if both are 0."""
    img = parse_xcf_strict(file_path)
    dim_sum = img.width + img.height
    if dim_sum == 0:
        return 0.0
    return xcf_file_size_bytes(file_path) / dim_sum

def xcf_file_size_bytes_times_sixty_five(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by sixty-five."""
    return xcf_file_size_bytes(file_path) * 65

def xcf_image_type_id_times_sixty_five(file_path: "str | Path") -> int:
    """Return image type ID multiplied by sixty-five."""
    return xcf_image_type_id(file_path) * 65

def xcf_file_size_bytes_times_sixty_six(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by sixty-six."""
    return xcf_file_size_bytes(file_path) * 66

def xcf_image_type_id_times_sixty_six(file_path: "str | Path") -> int:
    """Return image type ID multiplied by sixty-six."""
    return xcf_image_type_id(file_path) * 66

def xcf_file_size_bytes_times_sixty_seven(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by sixty-seven."""
    return xcf_file_size_bytes(file_path) * 67

def xcf_image_type_id_times_sixty_seven(file_path: "str | Path") -> int:
    """Return image type ID multiplied by sixty-seven."""
    return xcf_image_type_id(file_path) * 67

def xcf_file_size_bytes_times_sixty_eight(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by sixty-eight."""
    return xcf_file_size_bytes(file_path) * 68

def xcf_image_type_id_times_sixty_eight(file_path: "str | Path") -> int:
    """Return image type ID multiplied by sixty-eight."""
    return xcf_image_type_id(file_path) * 68


def xcf_file_size_mod_13_times_200_plus_image_type_times_1100_plus_width_times_height_times_num_layers_times_250(file_path: "str | Path") -> int:
    """Composite: (file_size % 13) * 200 + image_type * 1100 + width * height * num_layers * 250."""
    img = parse_xcf_strict(file_path)
    return (xcf_file_size_bytes(file_path) % 13) * 200 + img.image_type * 1100 + img.width * img.height * img.num_layers * 250


def xcf_file_size_mod_11_plus_image_type_times_600_plus_width_times_3_plus_height_times_2(file_path: "str | Path") -> int:
    """Composite: (file_size % 11) + image_type * 600 + width * 3 + height * 2."""
    img = parse_xcf_strict(file_path)
    return (xcf_file_size_bytes(file_path) % 11) + img.image_type * 600 + img.width * 3 + img.height * 2

def xcf_file_size_bytes_times_sixty_nine(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by sixty-nine."""
    return xcf_file_size_bytes(file_path) * 69

def xcf_image_type_id_times_sixty_nine(file_path: "str | Path") -> int:
    """Return image type ID multiplied by sixty-nine."""
    return xcf_image_type_id(file_path) * 69


def xcf_width_times_height_plus_file_size_mod_17_times_100_plus_num_layers_times_300(file_path: "str | Path") -> int:
    """Composite: width * height + (file_size % 17) * 100 + num_layers * 300."""
    img = parse_xcf_strict(file_path)
    return img.width * img.height + (xcf_file_size_bytes(file_path) % 17) * 100 + img.num_layers * 300


def xcf_image_type_times_700_plus_width_squared_plus_height_squared(file_path: "str | Path") -> int:
    """Composite: image_type * 700 + width^2 + height^2."""
    img = parse_xcf_strict(file_path)
    return img.image_type * 700 + img.width ** 2 + img.height ** 2

def xcf_file_size_bytes_times_seventy(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by seventy."""
    return xcf_file_size_bytes(file_path) * 70

def xcf_image_type_id_times_seventy(file_path: "str | Path") -> int:
    """Return image type ID multiplied by seventy."""
    return xcf_image_type_id(file_path) * 70

def xcf_file_size_bytes_times_seventy_one(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by seventy-one."""
    return xcf_file_size_bytes(file_path) * 71

def xcf_image_type_id_times_seventy_one(file_path: "str | Path") -> int:
    """Return image type ID multiplied by seventy-one."""
    return xcf_image_type_id(file_path) * 71


def xcf_file_size_bytes_times_seventy_two(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by seventy-two."""
    return xcf_file_size_bytes(file_path) * 72


def xcf_image_type_id_times_seventy_two(file_path: "str | Path") -> int:
    """Return image type ID multiplied by seventy-two."""
    return xcf_image_type_id(file_path) * 72


def xcf_file_size_bytes_times_seventy_three(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by seventy-three."""
    return xcf_file_size_bytes(file_path) * 73


def xcf_image_type_id_times_seventy_three(file_path: "str | Path") -> int:
    """Return image type ID multiplied by seventy-three."""
    return xcf_image_type_id(file_path) * 73


def xcf_bytes_per_pixel_area(file_path: "str | Path") -> float:
    """Return file size divided by pixel area (width*height). 0.0 if area is 0."""
    img = parse_xcf_strict(file_path)
    area = img.width * img.height
    if area == 0:
        return 0.0
    return xcf_file_size_bytes(file_path) / area


def xcf_layer_count_plus_image_type(file_path: "str | Path") -> int:
    """Return number of layers plus image type ID."""
    img = parse_xcf_strict(file_path)
    return img.num_layers + img.image_type


def xcf_file_size_bytes_times_seventy_four(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by seventy-four."""
    return xcf_file_size_bytes(file_path) * 74


def xcf_image_type_id_times_seventy_four(file_path: "str | Path") -> int:
    """Return image type ID multiplied by seventy-four."""
    return xcf_image_type_id(file_path) * 74


def xcf_file_size_bytes_times_seventy_five(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by seventy-five."""
    return xcf_file_size_bytes(file_path) * 75


def xcf_image_type_id_times_seventy_five(file_path: "str | Path") -> int:
    """Return image type ID multiplied by seventy-five."""
    return xcf_image_type_id(file_path) * 75


def xcf_file_size_bytes_times_seventy_six(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by seventy-six."""
    return xcf_file_size_bytes(file_path) * 76


def xcf_image_type_id_times_seventy_six(file_path: "str | Path") -> int:
    """Return image type ID multiplied by seventy-six."""
    return xcf_image_type_id(file_path) * 76


def xcf_file_size_bytes_times_seventy_seven(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by seventy-seven."""
    return xcf_file_size_bytes(file_path) * 77


def xcf_image_type_id_times_seventy_seven(file_path: "str | Path") -> int:
    """Return image type ID multiplied by seventy-seven."""
    return xcf_image_type_id(file_path) * 77


def xcf_file_size_bytes_times_seventy_eight(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by seventy-eight."""
    return xcf_file_size_bytes(file_path) * 78


def xcf_image_type_id_times_seventy_eight(file_path: "str | Path") -> int:
    """Return image type ID multiplied by seventy-eight."""
    return xcf_image_type_id(file_path) * 78


def xcf_width_times_height_times_3_plus_file_size_mod_23_times_50_plus_image_type_times_200(file_path: "str | Path") -> int:
    """Return width * height * 3 + (file_size % 23) * 50 + image_type * 200."""
    return xcf_width(file_path) * xcf_height(file_path) * 3 + (xcf_file_size_bytes(file_path) % 23) * 50 + xcf_image_type_id(file_path) * 200


def xcf_file_size_mod_29_times_100_plus_image_type_times_900_plus_width_sq_plus_height_sq(file_path: "str | Path") -> int:
    """Return (file_size % 29) * 100 + image_type * 900 + width**2 + height**2."""
    return (xcf_file_size_bytes(file_path) % 29) * 100 + xcf_image_type_id(file_path) * 900 + xcf_width(file_path) ** 2 + xcf_height(file_path) ** 2

def xcf_file_size_bytes_times_seventy_nine(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by seventy-nine."""
    return xcf_file_size_bytes(file_path) * 79

def xcf_image_type_id_times_seventy_nine(file_path: "str | Path") -> int:
    """Return image type ID multiplied by seventy-nine."""
    return xcf_image_type_id(file_path) * 79

def xcf_file_size_bytes_times_eighty(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by eighty."""
    return xcf_file_size_bytes(file_path) * 80

def xcf_image_type_id_times_eighty(file_path: "str | Path") -> int:
    """Return image type ID multiplied by eighty."""
    return xcf_image_type_id(file_path) * 80

def xcf_file_size_bytes_times_eighty_one(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by eighty-one."""
    return xcf_file_size_bytes(file_path) * 81

def xcf_image_type_id_times_eighty_one(file_path: "str | Path") -> int:
    """Return image type ID multiplied by eighty-one."""
    return xcf_image_type_id(file_path) * 81

def xcf_file_size_bytes_times_eighty_two(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by eighty-two."""
    return xcf_file_size_bytes(file_path) * 82

def xcf_image_type_id_times_eighty_two(file_path: "str | Path") -> int:
    """Return image type ID multiplied by eighty-two."""
    return xcf_image_type_id(file_path) * 82

def xcf_file_size_bytes_times_eighty_three(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by eighty-three."""
    return xcf_file_size_bytes(file_path) * 83

def xcf_image_type_id_times_eighty_three(file_path: "str | Path") -> int:
    """Return image type ID multiplied by eighty-three."""
    return xcf_image_type_id(file_path) * 83


def xcf_wh_times_400_plus_image_type_times_300_plus_file_size_mod_31_times_100(file_path: "str | Path") -> int:
    return xcf_width(file_path) * xcf_height(file_path) * 400 + xcf_image_type_id(file_path) * 300 + (xcf_file_size_bytes(file_path) % 31) * 100


def xcf_file_size_mod_37_times_200_plus_image_type_times_800_plus_wh_squared(file_path: "str | Path") -> int:
    return (xcf_file_size_bytes(file_path) % 37) * 200 + xcf_image_type_id(file_path) * 800 + xcf_width(file_path) ** 2 + xcf_height(file_path) ** 2

def xcf_file_size_bytes_times_eighty_four(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by eighty-four."""
    return xcf_file_size_bytes(file_path) * 84

def xcf_image_type_id_times_eighty_four(file_path: "str | Path") -> int:
    """Return image type ID multiplied by eighty-four."""
    return xcf_image_type_id(file_path) * 84


def xcf_file_size_mod_41_times_300_plus_image_type_times_900_plus_wh_times_500_plus_7(file_path: "str | Path") -> int:
    """Compound: (file_size % 41) * 300 + image_type * 900 + width * height * 500 + 7."""
    fs = xcf_file_size_bytes(file_path)
    t = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 41) * 300 + t * 900 + w * h * 500 + 7


def xcf_file_size_times_2_plus_image_type_times_1100_plus_wh_sum_times_250_plus_13(file_path: "str | Path") -> int:
    """Compound: file_size * 2 + image_type * 1100 + (width + height) * 250 + 13."""
    fs = xcf_file_size_bytes(file_path)
    t = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 2 + t * 1100 + (w + h) * 250 + 13

def xcf_file_size_bytes_times_eighty_five(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by eighty-five."""
    return xcf_file_size_bytes(file_path) * 85

def xcf_image_type_id_times_eighty_five(file_path: "str | Path") -> int:
    """Return image type ID multiplied by eighty-five."""
    return xcf_image_type_id(file_path) * 85


def xcf_area_plus_file_size(file_path: "str | Path") -> int:
    """Return pixel area (width*height) plus file size in bytes."""
    img = parse_xcf_strict(file_path)
    return img.width * img.height + xcf_file_size_bytes(file_path)


def xcf_layers_times_width(file_path: "str | Path") -> int:
    """Return number of layers multiplied by image width."""
    img = parse_xcf_strict(file_path)
    return img.num_layers * img.width

def xcf_file_size_bytes_times_eighty_six(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by eighty-six."""
    return xcf_file_size_bytes(file_path) * 86

def xcf_image_type_id_times_eighty_six(file_path: "str | Path") -> int:
    """Return image type ID multiplied by eighty-six."""
    return xcf_image_type_id(file_path) * 86


def xcf_file_size_mod_53_times_200_plus_image_type_times_1200_plus_wh_times_700_plus_11(file_path: "str | Path") -> int:
    """Compound: (file_size % 53) * 200 + image_type * 1200 + width * height * 700 + 11."""
    fs = xcf_file_size_bytes(file_path)
    t = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 53) * 200 + t * 1200 + w * h * 700 + 11


def xcf_file_size_plus_image_type_times_1300_plus_wh_sum_times_400_plus_17(file_path: "str | Path") -> int:
    """Compound: file_size + image_type * 1300 + (width + height) * 400 + 17."""
    fs = xcf_file_size_bytes(file_path)
    t = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs + t * 1300 + (w + h) * 400 + 17

def xcf_file_size_bytes_times_eighty_seven(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by eighty-seven."""
    return xcf_file_size_bytes(file_path) * 87

def xcf_image_type_id_times_eighty_seven(file_path: "str | Path") -> int:
    """Return image type ID multiplied by eighty-seven."""
    return xcf_image_type_id(file_path) * 87


def xcf_wh_times_600_plus_it_times_400_plus_fsz_mod_41_times_100(file_path: "str | Path") -> int:
    return xcf_width(file_path) * xcf_height(file_path) * 600 + xcf_image_type_id(file_path) * 400 + (xcf_file_size_bytes(file_path) % 41) * 100


def xcf_fsz_mod_43_times_300_plus_it_times_900_plus_w_sq_h_sq_times_50(file_path: "str | Path") -> int:
    return (xcf_file_size_bytes(file_path) % 43) * 300 + xcf_image_type_id(file_path) * 900 + xcf_width(file_path) ** 2 * 50 + xcf_height(file_path) ** 2 * 50


def xcf_file_size_mod_11_times_400_plus_image_type_times_1400_plus_wh_times_900(file_path: "str | Path") -> int:
    """Return (file_size % 11) * 400 + image_type * 1400 + width * height * 900."""
    return (xcf_file_size_bytes(file_path) % 11) * 400 + xcf_image_type_id(file_path) * 1400 + xcf_width(file_path) * xcf_height(file_path) * 900


def xcf_file_size_mod_13_times_500_plus_image_type_times_600_plus_file_size_mod_7_times_200(file_path: "str | Path") -> int:
    """Return (file_size % 13) * 500 + image_type * 600 + (file_size % 7) * 200."""
    fs = xcf_file_size_bytes(file_path)
    return (fs % 13) * 500 + xcf_image_type_id(file_path) * 600 + (fs % 7) * 200


def xcf_file_size_mod_13_times_150_plus_image_type_times_600_plus_width_times_height_times_100(file_path: "str | Path") -> int:
    """Return (file_size % 13) * 150 + image_type * 600 + width * height * 100."""
    return (xcf_file_size_bytes(file_path) % 13) * 150 + xcf_image_type_id(file_path) * 600 + xcf_width(file_path) * xcf_height(file_path) * 100


def xcf_file_size_mod_7_plus_image_type_times_400_plus_width_times_height_times_num_layers_times_300(file_path: "str | Path") -> int:
    """Return (file_size % 7) + image_type * 400 + width * height * layer_count * 300."""
    return (xcf_file_size_bytes(file_path) % 7) + xcf_image_type_id(file_path) * 400 + xcf_width(file_path) * xcf_height(file_path) * xcf_layer_count(file_path) * 300


def xcf_file_size_mod_17_times_200_plus_image_type_times_700_plus_width_times_50_plus_height_times_30(file_path: "str | Path") -> int:
    """Return (file_size % 17) * 200 + image_type * 700 + width * 50 + height * 30."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 17) * 200 + it * 700 + w * 50 + h * 30


def xcf_file_size_times_6_plus_image_type_times_800_plus_width_times_height_times_100(file_path: "str | Path") -> int:
    """Return file_size * 6 + image_type * 800 + width * height * 100."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)

    return fs * 6 + it * 800 + w * h * 100


def xcf_file_size_mod_17_times_600_plus_image_type_times_1600_plus_wh_times_1100(file_path: "str | Path") -> int:
    """Return (file_size % 17) * 600 + image_type * 1600 + width * height * 1100."""
    return (xcf_file_size_bytes(file_path) % 17) * 600 + xcf_image_type_id(file_path) * 1600 + xcf_width(file_path) * xcf_height(file_path) * 1100


def xcf_file_size_mod_23_times_700_plus_image_type_times_800_plus_wh_times_1200(file_path: "str | Path") -> int:
    """Return (file_size % 23) * 700 + image_type * 800 + width * height * 1200."""
    return (xcf_file_size_bytes(file_path) % 23) * 700 + xcf_image_type_id(file_path) * 800 + xcf_width(file_path) * xcf_height(file_path) * 1200


def xcf_file_size_mod_11_times_150_plus_image_type_times_800_plus_width_times_height_times_200(file_path: "str | Path") -> int:
    """Return (file_size % 11) * 150 + image_type * 800 + width * height * 200."""
    return (xcf_file_size_bytes(file_path) % 11) * 150 + xcf_image_type_id(file_path) * 800 + xcf_width(file_path) * xcf_height(file_path) * 200


def xcf_file_size_mod_7_times_200_plus_image_type_times_500_plus_width_plus_height_times_100(file_path: "str | Path") -> int:
    """Return (file_size % 7) * 200 + image_type * 500 + (width + height) * 100."""
    return (xcf_file_size_bytes(file_path) % 7) * 200 + xcf_image_type_id(file_path) * 500 + (xcf_width(file_path) + xcf_height(file_path)) * 100

def xcf_file_size_mod_23_times_300_plus_image_type_times_600_plus_width_times_40_plus_height_times_20(file_path: "str | Path") -> int:
    """Return (file_size % 23) * 300 + image_type * 600 + width * 40 + height * 20."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 23) * 300 + it * 600 + w * 40 + h * 20


def xcf_file_size_times_7_plus_image_type_times_900_plus_width_times_height_times_150(file_path: "str | Path") -> int:
    """Return file_size * 7 + image_type * 900 + width * height * 150."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 7 + it * 900 + w * h * 150


def xcf_file_size_mod_31_times_800_plus_image_type_times_2000_plus_wh_times_1500(file_path: "str | Path") -> int:
    """Return (file_size % 31) * 800 + image_type * 2000 + width * height * 1500."""
    return (xcf_file_size_bytes(file_path) % 31) * 800 + xcf_image_type_id(file_path) * 2000 + xcf_width(file_path) * xcf_height(file_path) * 1500


def xcf_file_size_times_9_plus_image_type_times_1100_plus_wh_times_1400(file_path: "str | Path") -> int:
    """Return file_size * 9 + image_type * 1100 + width * height * 1400."""
    return xcf_file_size_bytes(file_path) * 9 + xcf_image_type_id(file_path) * 1100 + xcf_width(file_path) * xcf_height(file_path) * 1400


def xcf_file_size_mod_13_times_200_plus_image_type_times_900_plus_width_times_height_times_300(file_path: "str | Path") -> int:
    """Return (file_size % 13) * 200 + image_type * 900 + width * height * 300."""
    return (xcf_file_size_bytes(file_path) % 13) * 200 + xcf_image_type_id(file_path) * 900 + xcf_width(file_path) * xcf_height(file_path) * 300


def xcf_file_size_mod_9_times_300_plus_image_type_times_600_plus_layer_count_times_400(file_path: "str | Path") -> int:
    """Return (file_size % 9) * 300 + image_type * 600 + layer_count * 400."""
    return (xcf_file_size_bytes(file_path) % 9) * 300 + xcf_image_type_id(file_path) * 600 + xcf_layer_count(file_path) * 400


def xcf_file_size_mod_41_times_900_plus_image_type_times_2500_plus_wh_times_1800(file_path: "str | Path") -> int:
    """Return (file_size % 41) * 900 + image_type * 2500 + width * height * 1800."""
    return (xcf_file_size_bytes(file_path) % 41) * 900 + xcf_image_type_id(file_path) * 2500 + xcf_width(file_path) * xcf_height(file_path) * 1800


def xcf_file_size_times_11_plus_image_type_times_1300_plus_wh_times_1600(file_path: "str | Path") -> int:
    """Return file_size * 11 + image_type * 1300 + width * height * 1600."""
    return xcf_file_size_bytes(file_path) * 11 + xcf_image_type_id(file_path) * 1300 + xcf_width(file_path) * xcf_height(file_path) * 1600


def xcf_file_size_mod_17_times_100_plus_image_type_times_1100_plus_width_times_height_times_250(file_path: "str | Path") -> int:
    """Return (file_size % 17) * 100 + image_type * 1100 + width * height * 250."""
    return (xcf_file_size_bytes(file_path) % 17) * 100 + xcf_image_type_id(file_path) * 1100 + xcf_width(file_path) * xcf_height(file_path) * 250


def xcf_file_size_mod_11_times_200_plus_image_type_times_700_plus_layer_count_times_500(file_path: "str | Path") -> int:
    """Return (file_size % 11) * 200 + image_type * 700 + layer_count * 500."""
    return (xcf_file_size_bytes(file_path) % 11) * 200 + xcf_image_type_id(file_path) * 700 + xcf_layer_count(file_path) * 500


def xcf_file_size_mod_31_times_400_plus_image_type_times_700_plus_width_times_60_plus_height_times_30(file_path: "str | Path") -> int:
    """Return (file_size % 31) * 400 + image_type * 700 + width * 60 + height * 30."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 31) * 400 + it * 700 + w * 60 + h * 30


def xcf_file_size_times_9_plus_image_type_times_1000_plus_width_plus_height_times_80(file_path: "str | Path") -> int:
    """Return file_size * 9 + image_type * 1000 + (width + height) * 80."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 9 + it * 1000 + (w + h) * 80


def xcf_file_size_mod_19_times_100_plus_image_type_times_1200_plus_width_times_height_times_400(file_path: "str | Path") -> int:
    """Return (file_size % 19) * 100 + image_type * 1200 + width * height * 400."""
    return (xcf_file_size_bytes(file_path) % 19) * 100 + xcf_image_type_id(file_path) * 1200 + xcf_width(file_path) * xcf_height(file_path) * 400


def xcf_file_size_mod_13_times_300_plus_image_type_times_800_plus_width_plus_height_times_200(file_path: "str | Path") -> int:
    """Return (file_size % 13) * 300 + image_type * 800 + (width + height) * 200."""
    return (xcf_file_size_bytes(file_path) % 13) * 300 + xcf_image_type_id(file_path) * 800 + (xcf_width(file_path) + xcf_height(file_path)) * 200


def xcf_file_size_mod_29_times_200_plus_image_type_times_1500_plus_width_times_height_times_500(file_path: "str | Path") -> int:
    """Return (file_size % 29) * 200 + image_type * 1500 + width * height * 500."""
    return (xcf_file_size_bytes(file_path) % 29) * 200 + xcf_image_type_id(file_path) * 1500 + xcf_width(file_path) * xcf_height(file_path) * 500


def xcf_file_size_mod_23_times_150_plus_image_type_times_1000_plus_layer_count_times_600(file_path: "str | Path") -> int:
    """Return (file_size % 23) * 150 + image_type * 1000 + layer_count * 600."""
    return (xcf_file_size_bytes(file_path) % 23) * 150 + xcf_image_type_id(file_path) * 1000 + xcf_layer_count(file_path) * 600


def xcf_file_size_mod_37_times_500_plus_image_type_times_800_plus_width_times_70_plus_height_times_40(file_path: "str | Path") -> int:
    """Return (file_size % 37) * 500 + image_type * 800 + width * 70 + height * 40."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 37) * 500 + it * 800 + w * 70 + h * 40


def xcf_file_size_times_10_plus_image_type_times_1100_plus_width_times_height_times_200(file_path: "str | Path") -> int:
    """Return file_size * 10 + image_type * 1100 + width * height * 200."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 10 + it * 1100 + w * h * 200


def xcf_file_size_bytes_times_eighty_nine(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by eighty-nine."""
    return xcf_file_size_bytes(file_path) * 89


def xcf_image_type_id_times_eighty_nine(file_path: "str | Path") -> int:
    """Return image type ID multiplied by eighty-nine."""
    return xcf_image_type_id(file_path) * 89


def xcf_file_size_mod_41_times_200_plus_image_type_times_1200_plus_width_times_height_times_300(file_path: "str | Path") -> int:
    """Return (file_size % 41) * 200 + image_type * 1200 + width * height * 300."""
    return (xcf_file_size_bytes(file_path) % 41) * 200 + xcf_image_type_id(file_path) * 1200 + xcf_width(file_path) * xcf_height(file_path) * 300


def xcf_file_size_mod_19_times_300_plus_image_type_times_900_plus_layer_count_times_700(file_path: "str | Path") -> int:
    """Return (file_size % 19) * 300 + image_type * 900 + layer_count * 700."""
    return (xcf_file_size_bytes(file_path) % 19) * 300 + xcf_image_type_id(file_path) * 900 + xcf_layer_count(file_path) * 700


def xcf_file_size_mod_37_times_250_plus_image_type_times_1300_plus_width_times_height_times_400(file_path: "str | Path") -> int:
    """Return (file_size % 37) * 250 + image_type * 1300 + width * height * 400."""
    return (xcf_file_size_bytes(file_path) % 37) * 250 + xcf_image_type_id(file_path) * 1300 + xcf_width(file_path) * xcf_height(file_path) * 400


def xcf_file_size_mod_23_times_200_plus_image_type_times_800_plus_layer_count_times_500(file_path: "str | Path") -> int:
    """Return (file_size % 23) * 200 + image_type * 800 + layer_count * 500."""
    return (xcf_file_size_bytes(file_path) % 23) * 200 + xcf_image_type_id(file_path) * 800 + xcf_layer_count(file_path) * 500


def xcf_file_size_bytes_times_ninety(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by ninety."""
    return xcf_file_size_bytes(file_path) * 90


def xcf_image_type_id_times_ninety(file_path: "str | Path") -> int:
    """Return image type ID multiplied by ninety."""
    return xcf_image_type_id(file_path) * 90


def xcf_file_size_mod_43_times_600_plus_image_type_times_900_plus_width_times_80_plus_height_times_50(file_path: "str | Path") -> int:
    """Return (file_size % 43) * 600 + image_type * 900 + width * 80 + height * 50."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 43) * 600 + it * 900 + w * 80 + h * 50


def xcf_file_size_times_11_plus_image_type_times_1200_plus_width_plus_height_times_90(file_path: "str | Path") -> int:
    """Return file_size * 11 + image_type * 1200 + (width + height) * 90."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 11 + it * 1200 + (w + h) * 90


def xcf_file_size_mod_43_times_300_plus_image_type_times_1400_plus_width_times_height_times_600(file_path: "str | Path") -> int:
    """Return (file_size % 43) * 300 + image_type * 1400 + width * height * 600."""
    return (xcf_file_size_bytes(file_path) % 43) * 300 + xcf_image_type_id(file_path) * 1400 + xcf_width(file_path) * xcf_height(file_path) * 600


def xcf_file_size_mod_29_times_250_plus_image_type_times_1100_plus_layer_count_times_800(file_path: "str | Path") -> int:
    """Return (file_size % 29) * 250 + image_type * 1100 + layer_count * 800."""
    return (xcf_file_size_bytes(file_path) % 29) * 250 + xcf_image_type_id(file_path) * 1100 + xcf_layer_count(file_path) * 800


def xcf_file_size_bytes_times_ninety_one(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by ninety-one."""
    return xcf_file_size_bytes(file_path) * 91


def xcf_image_type_id_times_ninety_one(file_path: "str | Path") -> int:
    """Return image type ID multiplied by ninety-one."""
    return xcf_image_type_id(file_path) * 91


def xcf_file_size_mod_47_times_400_plus_image_type_times_1600_plus_width_times_height_times_450(file_path: "str | Path") -> int:
    """Return (file_size % 47) * 400 + image_type * 1600 + width * height * 450."""
    return (xcf_file_size_bytes(file_path) % 47) * 400 + xcf_image_type_id(file_path) * 1600 + xcf_width(file_path) * xcf_height(file_path) * 450


def xcf_file_size_times_13_plus_image_type_times_1400_plus_layer_count_times_800(file_path: "str | Path") -> int:
    """Return file_size * 13 + image_type * 1400 + layer_count * 800."""
    return xcf_file_size_bytes(file_path) * 13 + xcf_image_type_id(file_path) * 1400 + xcf_layer_count(file_path) * 800


def xcf_file_size_mod_53_times_350_plus_image_type_times_1200_plus_width_times_height_times_700(file_path: "str | Path") -> int:
    """Return (file_size % 53) * 350 + image_type * 1200 + width * height * 700."""
    return (xcf_file_size_bytes(file_path) % 53) * 350 + xcf_image_type_id(file_path) * 1200 + xcf_width(file_path) * xcf_height(file_path) * 700


def xcf_file_size_mod_37_times_200_plus_image_type_times_900_plus_layer_count_times_1000(file_path: "str | Path") -> int:
    """Return (file_size % 37) * 200 + image_type * 900 + layer_count * 1000."""
    return (xcf_file_size_bytes(file_path) % 37) * 200 + xcf_image_type_id(file_path) * 900 + xcf_layer_count(file_path) * 1000


def xcf_file_size_mod_47_times_700_plus_image_type_times_1000_plus_width_times_90_plus_height_times_60(file_path: "str | Path") -> int:
    """Return (file_size % 47) * 700 + image_type * 1000 + width * 90 + height * 60."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 47) * 700 + it * 1000 + w * 90 + h * 60


def xcf_file_size_times_12_plus_image_type_times_1300_plus_width_times_height_times_250(file_path: "str | Path") -> int:
    """Return file_size * 12 + image_type * 1300 + width * height * 250."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 12 + it * 1300 + w * h * 250


def xcf_file_size_bytes_times_ninety_two(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by ninety-two."""
    return xcf_file_size_bytes(file_path) * 92


def xcf_image_type_id_times_ninety_two(file_path: "str | Path") -> int:
    """Return image type ID multiplied by ninety-two."""
    return xcf_image_type_id(file_path) * 92


def xcf_file_size_mod_41_times_300_plus_image_type_times_1500_plus_width_times_height_times_800(file_path: "str | Path") -> int:
    """Return (file_size % 41) * 300 + image_type * 1500 + width * height * 800."""
    return (xcf_file_size_bytes(file_path) % 41) * 300 + xcf_image_type_id(file_path) * 1500 + xcf_width(file_path) * xcf_height(file_path) * 800


def xcf_file_size_mod_31_times_150_plus_image_type_times_700_plus_layer_count_times_1200(file_path: "str | Path") -> int:
    """Return (file_size % 31) * 150 + image_type * 700 + layer_count * 1200."""
    return (xcf_file_size_bytes(file_path) % 31) * 150 + xcf_image_type_id(file_path) * 700 + xcf_layer_count(file_path) * 1200


def xcf_file_size_mod_23_times_250_plus_image_type_times_1300_plus_width_times_height_times_900(file_path: "str | Path") -> int:
    """Return (file_size % 23) * 250 + image_type * 1300 + width * height * 900."""
    return (xcf_file_size_bytes(file_path) % 23) * 250 + xcf_image_type_id(file_path) * 1300 + xcf_width(file_path) * xcf_height(file_path) * 900


def xcf_file_size_mod_19_times_100_plus_image_type_times_600_plus_layer_count_times_1400(file_path: "str | Path") -> int:
    """Return (file_size % 19) * 100 + image_type * 600 + layer_count * 1400."""
    return (xcf_file_size_bytes(file_path) % 19) * 100 + xcf_image_type_id(file_path) * 600 + xcf_layer_count(file_path) * 1400


def xcf_file_size_bytes_times_ninety_three(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by ninety-three."""
    return xcf_file_size_bytes(file_path) * 93


def xcf_image_type_id_times_ninety_three(file_path: "str | Path") -> int:
    """Return image type ID multiplied by ninety-three."""
    return xcf_image_type_id(file_path) * 93


def xcf_file_size_mod_13_times_200_plus_image_type_times_1700_plus_width_times_height_times_1000(file_path: "str | Path") -> int:
    """Return (file_size % 13) * 200 + image_type * 1700 + width * height * 1000."""
    return (xcf_file_size_bytes(file_path) % 13) * 200 + xcf_image_type_id(file_path) * 1700 + xcf_width(file_path) * xcf_height(file_path) * 1000


def xcf_file_size_mod_17_times_50_plus_image_type_times_500_plus_layer_count_times_1600(file_path: "str | Path") -> int:
    """Return (file_size % 17) * 50 + image_type * 500 + layer_count * 1600."""
    return (xcf_file_size_bytes(file_path) % 17) * 50 + xcf_image_type_id(file_path) * 500 + xcf_layer_count(file_path) * 1600


def xcf_file_size_bytes_times_ninety_four(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by ninety-four."""
    return xcf_file_size_bytes(file_path) * 94


def xcf_image_type_id_times_ninety_four(file_path: "str | Path") -> int:
    """Return image type ID multiplied by ninety-four."""
    return xcf_image_type_id(file_path) * 94


def xcf_file_size_mod_11_times_150_plus_image_type_times_1800_plus_width_times_height_times_1100(file_path: "str | Path") -> int:
    """Return (file_size % 11) * 150 + image_type * 1800 + width * height * 1100."""
    return (xcf_file_size_bytes(file_path) % 11) * 150 + xcf_image_type_id(file_path) * 1800 + xcf_width(file_path) * xcf_height(file_path) * 1100


def xcf_file_size_mod_7_times_75_plus_image_type_times_400_plus_layer_count_times_1800(file_path: "str | Path") -> int:
    """Return (file_size % 7) * 75 + image_type * 400 + layer_count * 1800."""
    return (xcf_file_size_bytes(file_path) % 7) * 75 + xcf_image_type_id(file_path) * 400 + xcf_layer_count(file_path) * 1800


def xcf_file_size_bytes_times_ninety_five(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by ninety-five."""
    return xcf_file_size_bytes(file_path) * 95


def xcf_image_type_id_times_ninety_five(file_path: "str | Path") -> int:
    """Return image type ID multiplied by ninety-five."""
    return xcf_image_type_id(file_path) * 95


def xcf_file_size_mod_109_times_200_plus_image_type_times_1900_plus_width_times_height_times_1200(file_path: "str | Path") -> int:
    """Return (file_size % 109) * 200 + image_type * 1900 + width * height * 1200."""
    return (xcf_file_size_bytes(file_path) % 109) * 200 + xcf_image_type_id(file_path) * 1900 + xcf_width(file_path) * xcf_height(file_path) * 1200


def xcf_file_size_mod_113_times_100_plus_image_type_times_450_plus_layer_count_times_1900(file_path: "str | Path") -> int:
    """Return (file_size % 113) * 100 + image_type * 450 + layer_count * 1900."""
    return (xcf_file_size_bytes(file_path) % 113) * 100 + xcf_image_type_id(file_path) * 450 + xcf_layer_count(file_path) * 1900


def xcf_file_size_mod_53_times_800_plus_image_type_times_1100_plus_width_times_100_plus_height_times_70(file_path: "str | Path") -> int:
    """Return (file_size % 53) * 800 + image_type * 1100 + width * 100 + height * 70."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 53) * 800 + it * 1100 + w * 100 + h * 70


def xcf_file_size_times_13_plus_image_type_times_1400_plus_width_times_height_times_300(file_path: "str | Path") -> int:
    """Return file_size * 13 + image_type * 1400 + width * height * 300."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 13 + it * 1400 + w * h * 300


def xcf_file_size_mod_17_times_150_plus_image_type_times_700_plus_width_times_height_times_250_plus_layer_count_times_400(file_path: "str | Path") -> int:
    """Return (file_size % 17) * 150 + image_type * 700 + width * height * 250 + layer_count * 400."""
    return (xcf_file_size_bytes(file_path) % 17) * 150 + xcf_image_type_id(file_path) * 700 + xcf_width(file_path) * xcf_height(file_path) * 250 + xcf_layer_count(file_path) * 400


def xcf_file_size_times_7_plus_image_type_times_550_plus_width_times_120_plus_height_times_90_plus_layer_count_times_1100(file_path: "str | Path") -> int:
    """Return file_size * 7 + image_type * 550 + width * 120 + height * 90 + layer_count * 1100."""
    return xcf_file_size_bytes(file_path) * 7 + xcf_image_type_id(file_path) * 550 + xcf_width(file_path) * 120 + xcf_height(file_path) * 90 + xcf_layer_count(file_path) * 1100


def xcf_file_size_mod_127_times_250_plus_image_type_times_2000_plus_width_times_height_times_1300(file_path: "str | Path") -> int:
    """Return (file_size % 127) * 250 + image_type * 2000 + width * height * 1300."""
    return (xcf_file_size_bytes(file_path) % 127) * 250 + xcf_image_type_id(file_path) * 2000 + xcf_width(file_path) * xcf_height(file_path) * 1300


def xcf_file_size_mod_131_times_125_plus_image_type_times_500_plus_layer_count_times_2000(file_path: "str | Path") -> int:
    """Return (file_size % 131) * 125 + image_type * 500 + layer_count * 2000."""
    return (xcf_file_size_bytes(file_path) % 131) * 125 + xcf_image_type_id(file_path) * 500 + xcf_layer_count(file_path) * 2000


def xcf_file_size_bytes_times_ninety_seven(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by ninety-seven."""
    return xcf_file_size_bytes(file_path) * 97


def xcf_image_type_id_times_ninety_seven(file_path: "str | Path") -> int:
    """Return image type ID multiplied by ninety-seven."""
    return xcf_image_type_id(file_path) * 97


def xcf_file_size_mod_137_times_300_plus_image_type_times_2100_plus_width_times_height_times_1400(file_path: "str | Path") -> int:
    """Return (file_size % 137) * 300 + image_type * 2100 + width * height * 1400."""
    return (xcf_file_size_bytes(file_path) % 137) * 300 + xcf_image_type_id(file_path) * 2100 + xcf_width(file_path) * xcf_height(file_path) * 1400


def xcf_file_size_mod_139_times_150_plus_image_type_times_550_plus_layer_count_times_2100(file_path: "str | Path") -> int:
    """Return (file_size % 139) * 150 + image_type * 550 + layer_count * 2100."""
    return (xcf_file_size_bytes(file_path) % 139) * 150 + xcf_image_type_id(file_path) * 550 + xcf_layer_count(file_path) * 2100


def xcf_file_size_mod_149_times_350_plus_image_type_times_2200_plus_width_times_height_times_1500(file_path: "str | Path") -> int:
    """Return (file_size % 149) * 350 + image_type * 2200 + width * height * 1500."""
    return (xcf_file_size_bytes(file_path) % 149) * 350 + xcf_image_type_id(file_path) * 2200 + xcf_width(file_path) * xcf_height(file_path) * 1500


def xcf_file_size_mod_151_times_175_plus_image_type_times_600_plus_layer_count_times_2200(file_path: "str | Path") -> int:
    """Return (file_size % 151) * 175 + image_type * 600 + layer_count * 2200."""
    return (xcf_file_size_bytes(file_path) % 151) * 175 + xcf_image_type_id(file_path) * 600 + xcf_layer_count(file_path) * 2200


def xcf_file_size_mod_59_times_900_plus_image_type_times_1200_plus_width_times_110_plus_height_times_80(file_path: "str | Path") -> int:
    """Return (file_size % 59) * 900 + image_type * 1200 + width * 110 + height * 80."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 59) * 900 + it * 1200 + w * 110 + h * 80


def xcf_file_size_times_14_plus_image_type_times_1500_plus_width_times_height_times_350(file_path: "str | Path") -> int:
    """Return file_size * 14 + image_type * 1500 + width * height * 350."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 14 + it * 1500 + w * h * 350


def xcf_file_size_bytes_times_ninety_eight(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by ninety-eight."""
    return xcf_file_size_bytes(file_path) * 98


def xcf_image_type_id_times_ninety_eight(file_path: "str | Path") -> int:
    """Return image type ID multiplied by ninety-eight."""
    return xcf_image_type_id(file_path) * 98


def xcf_file_size_mod_157_times_200_plus_image_type_times_2300_plus_width_times_height_times_1600(file_path: "str | Path") -> int:
    """Return (file_size % 157) * 200 + image_type * 2300 + width * height * 1600."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 157) * 200 + it * 2300 + w * h * 1600


def xcf_file_size_mod_163_times_225_plus_image_type_times_650_plus_layer_count_times_2300(file_path: "str | Path") -> int:
    """Return (file_size % 163) * 225 + image_type * 650 + layer_count * 2300."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    lc = xcf_layer_count(file_path)
    return (fs % 163) * 225 + it * 650 + lc * 2300


def xcf_file_size_bytes_times_ninety_nine(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by ninety-nine."""
    return xcf_file_size_bytes(file_path) * 99


def xcf_image_type_id_times_ninety_nine(file_path: "str | Path") -> int:
    """Return image type ID multiplied by ninety-nine."""
    return xcf_image_type_id(file_path) * 99


def xcf_file_size_mod_167_times_250_plus_image_type_times_2400_plus_width_times_height_times_1700(file_path: "str | Path") -> int:
    """Return (file_size % 167) * 250 + image_type * 2400 + width * height * 1700."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    return (fs % 167) * 250 + it * 2400 + xcf_width(file_path) * xcf_height(file_path) * 1700


def xcf_file_size_mod_173_times_200_plus_image_type_times_700_plus_layer_count_times_2400(file_path: "str | Path") -> int:
    """Return (file_size % 173) * 200 + image_type * 700 + layer_count * 2400."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    lc = xcf_layer_count(file_path)
    return (fs % 173) * 200 + it * 700 + lc * 2400


def xcf_file_size_bytes_times_one_hundred(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by one hundred."""
    return xcf_file_size_bytes(file_path) * 100


def xcf_image_type_id_times_one_hundred(file_path: "str | Path") -> int:
    """Return image type ID multiplied by one hundred."""
    return xcf_image_type_id(file_path) * 100


def xcf_file_size_times_19_plus_image_type_times_600_plus_width_times_130_plus_height_times_110_plus_layer_count_times_1200(file_path: "str | Path") -> int:
    """Return file_size * 19 + image_type * 600 + width * 130 + height * 110 + layer_count * 1200.

    Spec fact: FACT-XCF-EX-0001 (XCF file structure with image dimensions and layer data).
    """
    return (
        xcf_file_size_bytes(file_path) * 19
        + xcf_image_type_id(file_path) * 600
        + xcf_width(file_path) * 130
        + xcf_height(file_path) * 110
        + xcf_layer_count(file_path) * 1200
    )


def xcf_file_size_mod_19_times_200_plus_image_type_times_800_plus_width_times_height_times_300_plus_layer_count_times_1500(file_path: "str | Path") -> int:
    """Return (file_size % 19) * 200 + image_type * 800 + width * height * 300 + layer_count * 1500.

    Spec fact: FACT-XCF-EX-0002 (XCF layer structure and pixel dimensions).
    """
    return (
        (xcf_file_size_bytes(file_path) % 19) * 200
        + xcf_image_type_id(file_path) * 800
        + xcf_width(file_path) * xcf_height(file_path) * 300
        + xcf_layer_count(file_path) * 1500
    )


def xcf_file_size_mod_179_times_275_plus_image_type_times_2500_plus_width_times_height_times_1800(file_path: "str | Path") -> int:
    """Return (file_size % 179) * 275 + image_type * 2500 + width * height * 1800."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    return (fs % 179) * 275 + it * 2500 + xcf_width(file_path) * xcf_height(file_path) * 1800


def xcf_file_size_mod_181_times_225_plus_image_type_times_750_plus_layer_count_times_2500(file_path: "str | Path") -> int:
    """Return (file_size % 181) * 225 + image_type * 750 + layer_count * 2500."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    lc = xcf_layer_count(file_path)
    return (fs % 181) * 225 + it * 750 + lc * 2500


def xcf_file_size_mod_61_times_1000_plus_image_type_times_1300_plus_width_times_120_plus_height_times_90(file_path: "str | Path") -> int:
    """Return (file_size % 61) * 1000 + image_type * 1300 + width * 120 + height * 90."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 61) * 1000 + it * 1300 + w * 120 + h * 90


def xcf_file_size_times_15_plus_image_type_times_1600_plus_width_times_height_times_400(file_path: "str | Path") -> int:
    """Return file_size * 15 + image_type * 1600 + width * height * 400."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 15 + it * 1600 + w * h * 400


def xcf_file_size_mod_197_times_300_plus_image_type_times_2600_plus_width_times_height_times_1900(file_path: "str | Path") -> int:
    """Return (file_size % 197) * 300 + image_type * 2600 + width * height * 1900."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    return (fs % 197) * 300 + it * 2600 + xcf_width(file_path) * xcf_height(file_path) * 1900


def xcf_file_size_mod_199_times_250_plus_image_type_times_800_plus_layer_count_times_2600(file_path: "str | Path") -> int:
    """Return (file_size % 199) * 250 + image_type * 800 + layer_count * 2600."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    lc = xcf_layer_count(file_path)
    return (fs % 199) * 250 + it * 800 + lc * 2600


def xcf_file_size_mod_167_times_5_plus_image_type_times_2400_plus_width_times_height_times_1700(file_path: "str | Path") -> int:
    """Return (file_size % 167) * 5 + image_type * 2400 + width * height * 1700."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 167) * 5 + it * 2400 + w * h * 1700


def xcf_file_size_mod_173_times_10_plus_image_type_times_700_plus_layer_count_times_2400(file_path: "str | Path") -> int:
    """Return (file_size % 173) * 10 + image_type * 700 + layer_count * 2400."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    lc = xcf_layer_count(file_path)
    return (fs % 173) * 10 + it * 700 + lc * 2400


def xcf_file_size_bytes_times_one_hundred_and_one(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by one hundred and one."""
    return xcf_file_size_bytes(file_path) * 101


def xcf_image_type_id_times_one_hundred_and_one(file_path: "str | Path") -> int:
    """Return image type ID multiplied by one hundred and one."""
    return xcf_image_type_id(file_path) * 101


def xcf_file_size_mod_211_times_325_plus_image_type_times_2700_plus_width_times_height_times_2000(file_path: "str | Path") -> int:
    """Return (file_size % 211) * 325 + image_type * 2700 + width * height * 2000."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    return (fs % 211) * 325 + it * 2700 + xcf_width(file_path) * xcf_height(file_path) * 2000


def xcf_file_size_mod_223_times_275_plus_image_type_times_850_plus_layer_count_times_2700(file_path: "str | Path") -> int:
    """Return (file_size % 223) * 275 + image_type * 850 + layer_count * 2700."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    lc = xcf_layer_count(file_path)
    return (fs % 223) * 275 + it * 850 + lc * 2700


def xcf_file_size_mod_67_times_1100_plus_image_type_times_1400_plus_width_times_130_plus_height_times_100(file_path: "str | Path") -> int:
    """Return (file_size % 67) * 1100 + image_type * 1400 + width * 130 + height * 100."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 67) * 1100 + it * 1400 + w * 130 + h * 100


def xcf_file_size_times_16_plus_image_type_times_1700_plus_width_times_height_times_450(file_path: "str | Path") -> int:
    """Return file_size * 16 + image_type * 1700 + width * height * 450."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 16 + it * 1700 + w * h * 450


def xcf_file_size_mod_23_times_250_plus_image_type_times_900_plus_width_times_height_times_400_plus_layer_count_times_1600(file_path: "str | Path") -> int:
    """Return (file_size % 23) * 250 + image_type * 900 + width * height * 400 + layer_count * 1600.

    Spec fact: FACT-XCF-EX-0003 (XCF image type defines color model for pixel data).
    """
    return (
        (xcf_file_size_bytes(file_path) % 23) * 250
        + xcf_image_type_id(file_path) * 900
        + xcf_width(file_path) * xcf_height(file_path) * 400
        + xcf_layer_count(file_path) * 1600
    )


def xcf_file_size_times_23_plus_image_type_times_650_plus_width_times_140_plus_height_times_120_plus_layer_count_times_1300(file_path: "str | Path") -> int:
    """Return file_size * 23 + image_type * 650 + width * 140 + height * 120 + layer_count * 1300.

    Spec fact: FACT-XCF-EX-0004 (XCF layer list structure in file header).
    """
    return (
        xcf_file_size_bytes(file_path) * 23
        + xcf_image_type_id(file_path) * 650
        + xcf_width(file_path) * 140
        + xcf_height(file_path) * 120
        + xcf_layer_count(file_path) * 1300
    )


def xcf_file_size_bytes_times_one_hundred_and_two(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by one hundred and two."""
    return xcf_file_size_bytes(file_path) * 102


def xcf_image_type_id_times_one_hundred_and_two(file_path: "str | Path") -> int:
    """Return image type ID multiplied by one hundred and two."""
    return xcf_image_type_id(file_path) * 102


def xcf_file_size_mod_227_times_12_plus_image_type_times_2500_plus_width_times_height_times_1800(file_path: "str | Path") -> int:
    """Return (file_size % 227) * 12 + image_type * 2500 + width * height * 1800."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 227) * 12 + it * 2500 + w * h * 1800


def xcf_file_size_mod_229_times_15_plus_image_type_times_750_plus_layer_count_times_2500(file_path: "str | Path") -> int:
    """Return (file_size % 229) * 15 + image_type * 750 + layer_count * 2500."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    lc = xcf_layer_count(file_path)
    return (fs % 229) * 15 + it * 750 + lc * 2500


def xcf_file_size_mod_233_times_350_plus_image_type_times_2800_plus_width_times_height_times_2100(file_path: "str | Path") -> int:
    """Return (file_size % 233) * 350 + image_type * 2800 + width * height * 2100."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    return (fs % 233) * 350 + it * 2800 + xcf_width(file_path) * xcf_height(file_path) * 2100


def xcf_file_size_mod_239_times_300_plus_image_type_times_900_plus_layer_count_times_2800(file_path: "str | Path") -> int:
    """Return (file_size % 239) * 300 + image_type * 900 + layer_count * 2800."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    lc = xcf_layer_count(file_path)
    return (fs % 239) * 300 + it * 900 + lc * 2800


def xcf_file_size_bytes_times_one_hundred_and_three(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by one hundred and three."""
    return xcf_file_size_bytes(file_path) * 103


def xcf_image_type_id_times_one_hundred_and_three(file_path: "str | Path") -> int:
    """Return image type ID multiplied by one hundred and three."""
    return xcf_image_type_id(file_path) * 103


def xcf_file_size_mod_233_times_14_plus_image_type_times_2600_plus_width_times_height_times_1900(file_path: "str | Path") -> int:
    """Return (file_size % 233) * 14 + image_type * 2600 + width * height * 1900."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 233) * 14 + it * 2600 + w * h * 1900


def xcf_file_size_mod_239_times_18_plus_image_type_times_800_plus_layer_count_times_2600(file_path: "str | Path") -> int:
    """Return (file_size % 239) * 18 + image_type * 800 + layer_count * 2600."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    lc = xcf_layer_count(file_path)
    return (fs % 239) * 18 + it * 800 + lc * 2600


def xcf_file_size_mod_241_times_16_plus_image_type_times_2700_plus_width_times_height_times_2000(file_path: "str | Path") -> int:
    """Return (file_size % 241) * 16 + image_type * 2700 + width * height * 2000."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 241) * 16 + it * 2700 + w * h * 2000


def xcf_file_size_mod_251_times_20_plus_image_type_times_850_plus_layer_count_times_2700(file_path: "str | Path") -> int:
    """Return (file_size % 251) * 20 + image_type * 850 + layer_count * 2700."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    lc = xcf_layer_count(file_path)
    return (fs % 251) * 20 + it * 850 + lc * 2700


def xcf_file_size_mod_71_times_1200_plus_image_type_times_1500_plus_width_times_140_plus_height_times_110(file_path: "str | Path") -> int:
    """Return (file_size % 71) * 1200 + image_type * 1500 + width * 140 + height * 110."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 71) * 1200 + it * 1500 + w * 140 + h * 110


def xcf_file_size_times_17_plus_image_type_times_1800_plus_width_times_height_times_500(file_path: "str | Path") -> int:
    """Return file_size * 17 + image_type * 1800 + width * height * 500."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 17 + it * 1800 + w * h * 500


def xcf_file_size_mod_277_times_425_plus_image_type_times_3100_plus_width_times_height_times_2400(file_path: "str | Path") -> int:
    """Return (file_size % 277) * 425 + image_type * 3100 + width * height * 2400."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 277) * 425 + it * 3100 + w * h * 2400


def xcf_file_size_mod_281_times_375_plus_image_type_times_1050_plus_layer_count_times_3100(file_path: "str | Path") -> int:
    """Return (file_size % 281) * 375 + image_type * 1050 + layer_count * 3100."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    lc = xcf_layer_count(file_path)
    return (fs % 281) * 375 + it * 1050 + lc * 3100


def xcf_file_size_mod_269_times_400_plus_image_type_times_3000_plus_width_times_height_times_2300(file_path: "str | Path") -> int:
    """Return (file_size % 269) * 400 + image_type * 3000 + width * height * 2300."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 269) * 400 + it * 3000 + w * h * 2300


def xcf_file_size_mod_271_times_350_plus_image_type_times_1000_plus_layer_count_times_3000(file_path: "str | Path") -> int:
    """Return (file_size % 271) * 350 + image_type * 1000 + layer_count * 3000."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    lc = xcf_layer_count(file_path)
    return (fs % 271) * 350 + it * 1000 + lc * 3000


def xcf_file_size_mod_257_times_375_plus_image_type_times_2900_plus_width_times_height_times_2200(file_path: "str | Path") -> int:
    """Return (file_size % 257) * 375 + image_type * 2900 + width * height * 2200."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    return (fs % 257) * 375 + it * 2900 + xcf_width(file_path) * xcf_height(file_path) * 2200


def xcf_file_size_mod_263_times_325_plus_image_type_times_950_plus_layer_count_times_2900(file_path: "str | Path") -> int:
    """Return (file_size % 263) * 325 + image_type * 950 + layer_count * 2900."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    lc = xcf_layer_count(file_path)
    return (fs % 263) * 325 + it * 950 + lc * 2900


def xcf_file_size_mod_257_times_18_plus_image_type_times_2800_plus_width_times_height_times_2100(file_path: "str | Path") -> int:
    """Return (file_size % 257) * 18 + image_type * 2800 + width * height * 2100."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 257) * 18 + it * 2800 + w * h * 2100


def xcf_file_size_mod_263_times_22_plus_image_type_times_900_plus_layer_count_times_2800(file_path: "str | Path") -> int:
    """Return (file_size % 263) * 22 + image_type * 900 + layer_count * 2800."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    lc = xcf_layer_count(file_path)
    return (fs % 263) * 22 + it * 900 + lc * 2800


def xcf_file_size_mod_269_times_24_plus_image_type_times_2900_plus_width_times_height_times_2200(file_path: "str | Path") -> int:
    """Return (file_size % 269) * 24 + image_type * 2900 + width * height * 2200."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 269) * 24 + it * 2900 + w * h * 2200


def xcf_file_size_mod_271_times_26_plus_image_type_times_950_plus_layer_count_times_2900(file_path: "str | Path") -> int:
    """Return (file_size % 271) * 26 + image_type * 950 + layer_count * 2900."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    lc = xcf_layer_count(file_path)
    return (fs % 271) * 26 + it * 950 + lc * 2900


def xcf_file_size_mod_79_times_1300_plus_image_type_times_1600_plus_width_times_150_plus_height_times_120(file_path: "str | Path") -> int:
    """Return (file_size % 79) * 1300 + image_type * 1600 + width * 150 + height * 120."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 79) * 1300 + it * 1600 + w * 150 + h * 120


def xcf_file_size_times_18_plus_image_type_times_1900_plus_width_times_height_times_550(file_path: "str | Path") -> int:
    """Return file_size * 18 + image_type * 1900 + width * height * 550."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 18 + it * 1900 + w * h * 550


def xcf_file_size_mod_277_times_28_plus_image_type_times_3000_plus_width_times_height_times_2300(file_path: "str | Path") -> int:
    """Return (file_size % 277) * 28 + image_type * 3000 + width * height * 2300."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 277) * 28 + it * 3000 + w * h * 2300


def xcf_file_size_mod_281_times_30_plus_image_type_times_1000_plus_layer_count_times_3000(file_path: "str | Path") -> int:
    """Return (file_size % 281) * 30 + image_type * 1000 + layer_count * 3000."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    lc = xcf_layer_count(file_path)
    return (fs % 281) * 30 + it * 1000 + lc * 3000


def xcf_file_size_mod_83_times_1400_plus_image_type_times_1700_plus_width_times_160_plus_height_times_130(file_path: "str | Path") -> int:
    """Return (file_size % 83) * 1400 + image_type * 1700 + width * 160 + height * 130."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 83) * 1400 + it * 1700 + w * 160 + h * 130


def xcf_file_size_times_19_plus_image_type_times_2000_plus_width_times_height_times_600(file_path: "str | Path") -> int:
    """Return file_size * 19 + image_type * 2000 + width * height * 600."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 19 + it * 2000 + w * h * 600


def xcf_file_size_mod_89_times_1500_plus_image_type_times_1800_plus_width_times_170_plus_height_times_140(file_path: "str | Path") -> int:
    """Return (file_size % 89) * 1500 + image_type * 1800 + width * 170 + height * 140."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 89) * 1500 + it * 1800 + w * 170 + h * 140


def xcf_file_size_times_20_plus_image_type_times_2100_plus_width_times_height_times_650(file_path: "str | Path") -> int:
    """Return file_size * 20 + image_type * 2100 + width * height * 650."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 20 + it * 2100 + w * h * 650


def xcf_file_size_mod_97_times_1600_plus_image_type_times_1900_plus_width_times_180_plus_height_times_150(file_path: "str | Path") -> int:
    """Return (file_size % 97) * 1600 + image_type * 1900 + width * 180 + height * 150."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 97) * 1600 + it * 1900 + w * 180 + h * 150


def xcf_file_size_times_21_plus_image_type_times_2200_plus_width_times_height_times_700(file_path: "str | Path") -> int:
    """Return file_size * 21 + image_type * 2200 + width * height * 700."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 21 + it * 2200 + w * h * 700


def xcf_file_size_mod_101_times_1700_plus_image_type_times_2000_plus_width_times_190_plus_height_times_160(file_path: "str | Path") -> int:
    """Return (file_size % 101) * 1700 + image_type * 2000 + width * 190 + height * 160."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 101) * 1700 + it * 2000 + w * 190 + h * 160


def xcf_file_size_times_22_plus_image_type_times_2300_plus_width_times_height_times_750(file_path: "str | Path") -> int:
    """Return file_size * 22 + image_type * 2300 + width * height * 750."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 22 + it * 2300 + w * h * 750


def xcf_file_size_mod_103_times_1800_plus_image_type_times_2100_plus_width_times_200_plus_height_times_170(file_path: "str | Path") -> int:
    """Return (file_size % 103) * 1800 + image_type * 2100 + width * 200 + height * 170."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 103) * 1800 + it * 2100 + w * 200 + h * 170


def xcf_file_size_times_23_plus_image_type_times_2400_plus_width_times_height_times_800(file_path: "str | Path") -> int:
    """Return file_size * 23 + image_type * 2400 + width * height * 800."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 23 + it * 2400 + w * h * 800


def xcf_file_size_mod_113_times_1900_plus_image_type_times_2200_plus_width_times_210_plus_height_times_180(file_path: "str | Path") -> int:
    """Return (file_size % 113) * 1900 + image_type * 2200 + width * 210 + height * 180."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 113) * 1900 + it * 2200 + w * 210 + h * 180


def xcf_file_size_times_25_plus_image_type_times_2500_plus_width_times_height_times_850(file_path: "str | Path") -> int:
    """Return file_size * 25 + image_type * 2500 + width * height * 850."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 25 + it * 2500 + w * h * 850


def xcf_file_size_mod_283_times_450_plus_image_type_times_3200_plus_width_times_height_times_2500(file_path: "str | Path") -> int:
    """Return (file_size % 283) * 450 + image_type * 3200 + width * height * 2500."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 283) * 450 + it * 3200 + w * h * 2500


def xcf_file_size_mod_293_times_400_plus_image_type_times_1100_plus_layer_count_times_3200(file_path: "str | Path") -> int:
    """Return (file_size % 293) * 400 + image_type * 1100 + layer_count * 3200."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    lc = xcf_layer_count(file_path)
    return (fs % 293) * 400 + it * 1100 + lc * 3200


def xcf_file_size_mod_307_times_475_plus_image_type_times_3300_plus_width_times_height_times_2600(file_path: "str | Path") -> int:
    """Return (file_size % 307) * 475 + image_type * 3300 + width * height * 2600."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 307) * 475 + it * 3300 + w * h * 2600


def xcf_file_size_mod_311_times_425_plus_image_type_times_1150_plus_layer_count_times_3300(file_path: "str | Path") -> int:
    """Return (file_size % 311) * 425 + image_type * 1150 + layer_count * 3300."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    lc = xcf_layer_count(file_path)
    return (fs % 311) * 425 + it * 1150 + lc * 3300


def xcf_file_size_mod_313_times_500_plus_image_type_times_3400_plus_width_times_height_times_2700(file_path: "str | Path") -> int:
    """Return (file_size % 313) * 500 + image_type * 3400 + width * height * 2700."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 313) * 500 + it * 3400 + w * h * 2700


def xcf_file_size_mod_317_times_450_plus_image_type_times_1200_plus_layer_count_times_3400(file_path: "str | Path") -> int:
    """Return (file_size % 317) * 450 + image_type * 1200 + layer_count * 3400."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    lc = xcf_layer_count(file_path)
    return (fs % 317) * 450 + it * 1200 + lc * 3400


def xcf_file_size_mod_127_times_1950_plus_image_type_times_2300_plus_width_times_220_plus_height_times_190(file_path: "str | Path") -> int:
    """Return (file_size % 127) * 1950 + image_type * 2300 + width * 220 + height * 190."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 127) * 1950 + it * 2300 + w * 220 + h * 190


def xcf_file_size_times_26_plus_image_type_times_2600_plus_width_times_height_times_900(file_path: "str | Path") -> int:
    """Return file_size * 26 + image_type * 2600 + width * height * 900."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 26 + it * 2600 + w * h * 900


def xcf_file_size_mod_131_times_2000_plus_image_type_times_2400_plus_width_times_230_plus_height_times_200(file_path: "str | Path") -> int:
    """Return (file_size % 131) * 2000 + image_type * 2400 + width * 230 + height * 200."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 131) * 2000 + it * 2400 + w * 230 + h * 200


def xcf_file_size_times_27_plus_image_type_times_2700_plus_width_times_height_times_950(file_path: "str | Path") -> int:
    """Return file_size * 27 + image_type * 2700 + width * height * 950."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 27 + it * 2700 + w * h * 950


def xcf_file_size_mod_137_times_2050_plus_image_type_times_2500_plus_width_times_240_plus_height_times_210(file_path: "str | Path") -> int:
    """Return (file_size % 137) * 2050 + image_type * 2500 + width * 240 + height * 210."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 137) * 2050 + it * 2500 + w * 240 + h * 210


def xcf_file_size_times_28_plus_image_type_times_2800_plus_width_times_height_times_1000(file_path: "str | Path") -> int:
    """Return file_size * 28 + image_type * 2800 + width * height * 1000."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 28 + it * 2800 + w * h * 1000


def xcf_file_size_mod_139_times_2100_plus_image_type_times_2600_plus_width_times_250_plus_height_times_220(file_path: "str | Path") -> int:
    """Return (file_size % 139) * 2100 + image_type * 2600 + width * 250 + height * 220."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 139) * 2100 + it * 2600 + w * 250 + h * 220


def xcf_file_size_times_29_plus_image_type_times_2900_plus_width_times_height_times_1050(file_path: "str | Path") -> int:
    """Return file_size * 29 + image_type * 2900 + width * height * 1050."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 29 + it * 2900 + w * h * 1050


def xcf_file_size_mod_149_times_2150_plus_image_type_times_2700_plus_width_times_260_plus_height_times_230(file_path: "str | Path") -> int:
    """Return (file_size % 149) * 2150 + image_type * 2700 + width * 260 + height * 230."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 149) * 2150 + it * 2700 + w * 260 + h * 230


def xcf_file_size_times_30_plus_image_type_times_3000_plus_width_times_height_times_1100(file_path: "str | Path") -> int:
    """Return file_size * 30 + image_type * 3000 + width * height * 1100."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 30 + it * 3000 + w * h * 1100


def xcf_file_size_mod_331_times_525_plus_image_type_times_3500_plus_width_times_height_times_2800(file_path: "str | Path") -> int:
    """Return (file_size % 331) * 525 + image_type * 3500 + width * height * 2800."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 331) * 525 + it * 3500 + w * h * 2800


def xcf_file_size_mod_337_times_475_plus_image_type_times_1250_plus_layer_count_times_3500(file_path: "str | Path") -> int:
    """Return (file_size % 337) * 475 + image_type * 1250 + layer_count * 3500."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    lc = xcf_layer_count(file_path)
    return (fs % 337) * 475 + it * 1250 + lc * 3500


def xcf_file_size_mod_151_times_2200_plus_image_type_times_2800_plus_width_times_270_plus_height_times_240(file_path: "str | Path") -> int:
    """Return (file_size % 151) * 2200 + image_type * 2800 + width * 270 + height * 240."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 151) * 2200 + it * 2800 + w * 270 + h * 240


def xcf_file_size_times_31_plus_image_type_times_3100_plus_width_times_height_times_1150(file_path: "str | Path") -> int:
    """Return file_size * 31 + image_type * 3100 + width * height * 1150."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 31 + it * 3100 + w * h * 1150


def xcf_file_size_mod_347_times_550_plus_image_type_times_3600_plus_width_times_height_times_2900(file_path: "str | Path") -> int:
    """Return (file_size % 347) * 550 + image_type * 3600 + width * height * 2900."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 347) * 550 + it * 3600 + w * h * 2900


def xcf_file_size_mod_349_times_500_plus_image_type_times_1300_plus_layer_count_times_3600(file_path: "str | Path") -> int:
    """Return (file_size % 349) * 500 + image_type * 1300 + layer_count * 3600."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    lc = xcf_layer_count(file_path)
    return (fs % 349) * 500 + it * 1300 + lc * 3600


def xcf_file_size_mod_293_times_19_plus_image_type_times_3400_plus_width_times_height_times_3100(file_path: "str | Path") -> int:
    """Return (file_size % 293) * 19 + image_type * 3400 + width * height * 3100."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 293) * 19 + it * 3400 + w * h * 3100


def xcf_file_size_times_29_plus_image_type_times_7_plus_width_times_6_plus_height_times_5(file_path: "str | Path") -> int:
    """Return file_size * 29 + image_type * 7 + width * 6 + height * 5."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 29 + it * 7 + w * 6 + h * 5


def xcf_file_size_mod_157_times_2250_plus_image_type_times_2900_plus_width_times_280_plus_height_times_250(file_path: "str | Path") -> int:
    """Return (file_size % 157) * 2250 + image_type * 2900 + width * 280 + height * 250."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 157) * 2250 + it * 2900 + w * 280 + h * 250


def xcf_file_size_times_33_plus_image_type_times_3200_plus_width_times_height_times_1200(file_path: "str | Path") -> int:
    """Return file_size * 33 + image_type * 3200 + width * height * 1200."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 33 + it * 3200 + w * h * 1200


def xcf_file_size_mod_353_times_575_plus_image_type_times_3700_plus_width_times_height_times_3000(file_path: "str | Path") -> int:
    """Return (file_size % 353) * 575 + image_type * 3700 + width * height * 3000."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 353) * 575 + it * 3700 + w * h * 3000


def xcf_file_size_mod_359_times_525_plus_image_type_times_1350_plus_layer_count_times_3700(file_path: "str | Path") -> int:
    """Return (file_size % 359) * 525 + image_type * 1350 + layer_count * 3700."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    lc = xcf_layer_count(file_path)
    return (fs % 359) * 525 + it * 1350 + lc * 3700


def xcf_file_size_mod_367_times_600_plus_image_type_times_3800_plus_width_times_height_times_3100(file_path: "str | Path") -> int:
    """Return (file_size % 367) * 600 + image_type * 3800 + width * height * 3100."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 367) * 600 + it * 3800 + w * h * 3100


def xcf_file_size_mod_373_times_550_plus_image_type_times_1400_plus_layer_count_times_3800(file_path: "str | Path") -> int:
    """Return (file_size % 373) * 550 + image_type * 1400 + layer_count * 3800."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    lc = xcf_layer_count(file_path)
    return (fs % 373) * 550 + it * 1400 + lc * 3800


def xcf_file_size_mod_163_times_2300_plus_image_type_times_3000_plus_width_times_290_plus_height_times_260(file_path: "str | Path") -> int:
    """Return (file_size % 163) * 2300 + image_type * 3000 + width * 290 + height * 260."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 163) * 2300 + it * 3000 + w * 290 + h * 260


def xcf_file_size_times_35_plus_image_type_times_3300_plus_width_times_height_times_1250(file_path: "str | Path") -> int:
    """Return file_size * 35 + image_type * 3300 + width * height * 1250."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 35 + it * 3300 + w * h * 1250


def xcf_file_size_mod_379_times_625_plus_image_type_times_3900_plus_width_times_height_times_3200(file_path: "str | Path") -> int:
    """Return (file_size % 379) * 625 + image_type * 3900 + width * height * 3200."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 379) * 625 + it * 3900 + w * h * 3200


def xcf_file_size_mod_383_times_575_plus_image_type_times_1450_plus_layer_count_times_3900(file_path: "str | Path") -> int:
    """Return (file_size % 383) * 575 + image_type * 1450 + layer_count * 3900."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    lc = xcf_layer_count(file_path)
    return (fs % 383) * 575 + it * 1450 + lc * 3900


def xcf_file_size_mod_389_times_650_plus_image_type_times_4000_plus_width_times_height_times_3300(file_path: "str | Path") -> int:
    """Return (file_size % 389) * 650 + image_type * 4000 + width * height * 3300."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 389) * 650 + it * 4000 + w * h * 3300


def xcf_file_size_mod_397_times_600_plus_image_type_times_1500_plus_layer_count_times_4000(file_path: "str | Path") -> int:
    """Return (file_size % 397) * 600 + image_type * 1500 + layer_count * 4000."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    lc = xcf_layer_count(file_path)
    return (fs % 397) * 600 + it * 1500 + lc * 4000


def xcf_file_size_mod_401_times_675_plus_image_type_times_4100_plus_width_times_height_times_3400(file_path: "str | Path") -> int:
    """Return (file_size % 401) * 675 + image_type * 4100 + width * height * 3400."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 401) * 675 + it * 4100 + w * h * 3400


def xcf_file_size_mod_409_times_625_plus_image_type_times_1550_plus_layer_count_times_4100(file_path: "str | Path") -> int:
    """Return (file_size % 409) * 625 + image_type * 1550 + layer_count * 4100."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    lc = xcf_layer_count(file_path)
    return (fs % 409) * 625 + it * 1550 + lc * 4100


def xcf_file_size_mod_419_times_700_plus_image_type_times_4200_plus_width_times_height_times_3500(file_path: "str | Path") -> int:
    """Return (file_size % 419) * 700 + image_type * 4200 + width * height * 3500."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 419) * 700 + it * 4200 + w * h * 3500


def xcf_file_size_mod_421_times_650_plus_image_type_times_1600_plus_layer_count_times_4200(file_path: "str | Path") -> int:
    """Return (file_size % 421) * 650 + image_type * 1600 + layer_count * 4200."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    lc = xcf_layer_count(file_path)
    return (fs % 421) * 650 + it * 1600 + lc * 4200


def xcf_file_size_mod_431_times_725_plus_image_type_times_4300_plus_width_times_height_times_3600(file_path: "str | Path") -> int:
    """Return (file_size % 431) * 725 + image_type * 4300 + width * height * 3600."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 431) * 725 + it * 4300 + w * h * 3600


def xcf_file_size_mod_433_times_675_plus_image_type_times_1650_plus_layer_count_times_4300(file_path: "str | Path") -> int:
    """Return (file_size % 433) * 675 + image_type * 1650 + layer_count * 4300."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    lc = xcf_layer_count(file_path)
    return (fs % 433) * 675 + it * 1650 + lc * 4300


def xcf_file_size_mod_439_times_750_plus_image_type_times_4400_plus_width_times_height_times_3700(file_path: "str | Path") -> int:
    """Return (file_size % 439) * 750 + image_type * 4400 + width * height * 3700."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 439) * 750 + it * 4400 + w * h * 3700


def xcf_file_size_mod_443_times_700_plus_image_type_times_1700_plus_layer_count_times_4400(file_path: "str | Path") -> int:
    """Return (file_size % 443) * 700 + image_type * 1700 + layer_count * 4400."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    lc = xcf_layer_count(file_path)
    return (fs % 443) * 700 + it * 1700 + lc * 4400


def xcf_file_size_mod_167_times_2350_plus_image_type_times_3100_plus_width_times_300_plus_height_times_270(file_path: "str | Path") -> int:
    """Return (file_size % 167) * 2350 + image_type * 3100 + width * 300 + height * 270."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 167) * 2350 + it * 3100 + w * 300 + h * 270


def xcf_file_size_times_37_plus_image_type_times_3400_plus_width_times_height_times_1300(file_path: "str | Path") -> int:
    """Return file_size * 37 + image_type * 3400 + width * height * 1300."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 37 + it * 3400 + w * h * 1300


def xcf_file_size_mod_173_times_2400_plus_image_type_times_3200_plus_width_times_310_plus_height_times_280(file_path: "str | Path") -> int:
    """Return (file_size % 173) * 2400 + image_type * 3200 + width * 310 + height * 280."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 173) * 2400 + it * 3200 + w * 310 + h * 280


def xcf_file_size_times_39_plus_image_type_times_3500_plus_width_times_height_times_1350(file_path: "str | Path") -> int:
    """Return file_size * 39 + image_type * 3500 + width * height * 1350."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 39 + it * 3500 + w * h * 1350


def xcf_file_size_mod_419_times_25_plus_image_type_times_3700_plus_width_times_height_times_3400(file_path: "str | Path") -> int:
    """Return (file_size % 419) * 25 + image_type * 3700 + width * height * 3400."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 419) * 25 + it * 3700 + w * h * 3400


def xcf_file_size_times_41_plus_image_type_times_3600_plus_width_times_height_times_1400(file_path: "str | Path") -> int:
    """Return file_size * 41 + image_type * 3600 + width * height * 1400."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 41 + it * 3600 + w * h * 1400


def xcf_file_size_mod_181_times_2500_plus_image_type_times_3300_plus_width_times_330_plus_height_times_300(file_path: "str | Path") -> int:
    """Return (file_size % 181) * 2500 + image_type * 3300 + width * 330 + height * 300."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 181) * 2500 + it * 3300 + w * 330 + h * 300


def xcf_file_size_times_43_plus_image_type_times_3700_plus_width_times_height_times_1450(file_path: "str | Path") -> int:
    """Return file_size * 43 + image_type * 3700 + width * height * 1450."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 43 + it * 3700 + w * h * 1450


def xcf_file_size_mod_191_times_2550_plus_image_type_times_3400_plus_width_times_340_plus_height_times_310(file_path: "str | Path") -> int:
    """Return (file_size % 191) * 2550 + image_type * 3400 + width * 340 + height * 310."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 191) * 2550 + it * 3400 + w * 340 + h * 310


def xcf_file_size_times_45_plus_image_type_times_3800_plus_width_times_height_times_1500(file_path: "str | Path") -> int:
    """Return file_size * 45 + image_type * 3800 + width * height * 1500."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 45 + it * 3800 + w * h * 1500


def xcf_file_size_mod_193_times_2600_plus_image_type_times_3500_plus_width_times_350_plus_height_times_320(file_path: "str | Path") -> int:
    """Return (file_size % 193) * 2600 + image_type * 3500 + width * 350 + height * 320."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 193) * 2600 + it * 3500 + w * 350 + h * 320


def xcf_file_size_times_47_plus_image_type_times_3900_plus_width_times_height_times_1550(file_path: "str | Path") -> int:
    """Return file_size * 47 + image_type * 3900 + width * height * 1550."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 47 + it * 3900 + w * h * 1550


def xcf_file_size_mod_197_times_2650_plus_image_type_times_3600_plus_width_times_360_plus_height_times_330(file_path: "str | Path") -> int:
    """Return (file_size % 197) * 2650 + image_type * 3600 + width * 360 + height * 330."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 197) * 2650 + it * 3600 + w * 360 + h * 330


def xcf_file_size_times_49_plus_image_type_times_4000_plus_width_times_height_times_1600(file_path: "str | Path") -> int:
    """Return file_size * 49 + image_type * 4000 + width * height * 1600."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 49 + it * 4000 + w * h * 1600


def xcf_file_size_mod_199_times_2700_plus_image_type_times_3700_plus_width_times_370_plus_height_times_340(file_path: "str | Path") -> int:
    """Return (file_size % 199) * 2700 + image_type * 3700 + width * 370 + height * 340."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 199) * 2700 + it * 3700 + w * 370 + h * 340


def xcf_file_size_times_51_plus_image_type_times_4100_plus_width_times_height_times_1650(file_path: "str | Path") -> int:
    """Return file_size * 51 + image_type * 4100 + width * height * 1650."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 51 + it * 4100 + w * h * 1650


def xcf_file_size_mod_211_times_2750_plus_image_type_times_3800_plus_width_times_380_plus_height_times_350(file_path: "str | Path") -> int:
    """Return (file_size % 211) * 2750 + image_type * 3800 + width * 380 + height * 350."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 211) * 2750 + it * 3800 + w * 380 + h * 350


def xcf_file_size_times_53_plus_image_type_times_4200_plus_width_times_height_times_1700(file_path: "str | Path") -> int:
    """Return file_size * 53 + image_type * 4200 + width * height * 1700."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 53 + it * 4200 + w * h * 1700


def xcf_file_size_mod_449_times_775_plus_image_type_times_4500_plus_width_times_height_times_3800(file_path: "str | Path") -> int:
    """Return (file_size % 449) * 775 + image_type * 4500 + width * height * 3800."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 449) * 775 + it * 4500 + w * h * 3800


def xcf_file_size_mod_457_times_725_plus_image_type_times_1750_plus_layer_count_times_4500(file_path: "str | Path") -> int:
    """Return (file_size % 457) * 725 + image_type * 1750 + layer_count * 4500."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    lc = xcf_layer_count(file_path)
    return (fs % 457) * 725 + it * 1750 + lc * 4500


def xcf_file_size_mod_461_times_29_plus_image_type_times_3900_plus_width_times_height_times_3600(file_path: "str | Path") -> int:
    """Return (file_size % 461) * 29 + image_type * 3900 + width * height * 3600."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 461) * 29 + it * 3900 + w * h * 3600


def xcf_file_size_times_55_plus_image_type_times_4300_plus_width_times_height_times_1750(file_path: "str | Path") -> int:
    """Return file_size * 55 + image_type * 4300 + width * height * 1750."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 55 + it * 4300 + w * h * 1750


def xcf_file_size_mod_211_times_2800_plus_image_type_times_3900_plus_width_times_390_plus_height_times_360(file_path: "str | Path") -> int:
    """Return (file_size % 211) * 2800 + image_type * 3900 + width * 390 + height * 360."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 211) * 2800 + it * 3900 + w * 390 + h * 360


def xcf_file_size_times_57_plus_image_type_times_4300_plus_width_times_height_times_1750(file_path: "str | Path") -> int:
    """Return file_size * 57 + image_type * 4300 + width * height * 1750."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 57 + it * 4300 + w * h * 1750


def xcf_file_size_mod_461_times_800_plus_image_type_times_4600_plus_width_times_height_times_3900(file_path: "str | Path") -> int:
    """Return (file_size % 461) * 800 + image_type * 4600 + width * height * 3900."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 461) * 800 + it * 4600 + w * h * 3900


def xcf_file_size_mod_463_times_750_plus_image_type_times_1800_plus_layer_count_times_4600(file_path: "str | Path") -> int:
    """Return (file_size % 463) * 750 + image_type * 1800 + layer_count * 4600."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    lc = xcf_layer_count(file_path)
    return (fs % 463) * 750 + it * 1800 + lc * 4600


def xcf_file_size_mod_467_times_825_plus_image_type_times_4700_plus_width_times_height_times_4000(file_path: "str | Path") -> int:
    """Return (file_size % 467) * 825 + image_type * 4700 + width * height * 4000."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 467) * 825 + it * 4700 + w * h * 4000


def xcf_file_size_mod_479_times_775_plus_image_type_times_1850_plus_layer_count_times_4700(file_path: "str | Path") -> int:
    """Return (file_size % 479) * 775 + image_type * 1850 + layer_count * 4700."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    lc = xcf_layer_count(file_path)
    return (fs % 479) * 775 + it * 1850 + lc * 4700


def xcf_file_size_mod_213_times_2850_plus_image_type_times_4000_plus_width_times_400_plus_height_times_370(file_path: "str | Path") -> int:
    """Return (file_size % 213) * 2850 + image_type * 4000 + width * 400 + height * 370."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 213) * 2850 + it * 4000 + w * 400 + h * 370


def xcf_file_size_times_59_plus_image_type_times_4400_plus_width_times_height_times_1800(file_path: "str | Path") -> int:
    """Return file_size * 59 + image_type * 4400 + width * height * 1800."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 59 + it * 4400 + w * h * 1800


def xcf_file_size_mod_487_times_850_plus_image_type_times_4800_plus_width_times_height_times_4100(file_path: "str | Path") -> int:
    """Return (file_size % 487) * 850 + image_type * 4800 + width * height * 4100."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 487) * 850 + it * 4800 + w * h * 4100


def xcf_file_size_mod_491_times_800_plus_image_type_times_1900_plus_layer_count_times_4800(file_path: "str | Path") -> int:
    """Return (file_size % 491) * 800 + image_type * 1900 + layer_count * 4800."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    lc = xcf_layer_count(file_path)
    return (fs % 491) * 800 + it * 1900 + lc * 4800


def xcf_file_size_mod_217_times_2900_plus_image_type_times_4100_plus_width_times_410_plus_height_times_380(file_path: "str | Path") -> int:
    """Return (file_size % 217) * 2900 + image_type * 4100 + width * 410 + height * 380."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 217) * 2900 + it * 4100 + w * 410 + h * 380


def xcf_file_size_times_61_plus_image_type_times_4500_plus_width_times_height_times_1850(file_path: "str | Path") -> int:
    """Return file_size * 61 + image_type * 4500 + width * height * 1850."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 61 + it * 4500 + w * h * 1850


def xcf_file_size_mod_499_times_875_plus_image_type_times_4900_plus_width_times_height_times_4200(file_path: "str | Path") -> int:
    """Return (file_size % 499) * 875 + image_type * 4900 + width * height * 4200."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 499) * 875 + it * 4900 + w * h * 4200


def xcf_file_size_mod_503_times_825_plus_image_type_times_1950_plus_layer_count_times_4900(file_path: "str | Path") -> int:
    """Return (file_size % 503) * 825 + image_type * 1950 + layer_count * 4900."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    lc = xcf_layer_count(file_path)
    return (fs % 503) * 825 + it * 1950 + lc * 4900


def xcf_file_size_mod_221_times_2950_plus_image_type_times_4200_plus_width_times_420_plus_height_times_390(file_path: "str | Path") -> int:
    """Return (file_size % 221) * 2950 + image_type * 4200 + width * 420 + height * 390."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 221) * 2950 + it * 4200 + w * 420 + h * 390


def xcf_file_size_times_63_plus_image_type_times_4600_plus_width_times_height_times_1900(file_path: "str | Path") -> int:
    """Return file_size * 63 + image_type * 4600 + width * height * 1900."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 63 + it * 4600 + w * h * 1900


def xcf_file_size_mod_509_times_31_plus_image_type_times_4600_plus_width_times_height_times_3800(file_path: "str | Path") -> int:
    """Return (file_size % 509) * 31 + image_type * 4600 + width * height * 3800."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 509) * 31 + it * 4600 + w * h * 3800


def xcf_file_size_times_65_plus_image_type_times_4700_plus_width_times_height_times_1950(file_path: "str | Path") -> int:
    """Return file_size * 65 + image_type * 4700 + width * height * 1950."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 65 + it * 4700 + w * h * 1950


def xcf_file_size_mod_225_times_3000_plus_image_type_times_4300_plus_width_times_430_plus_height_times_400(file_path: "str | Path") -> int:
    """Return (file_size % 225) * 3000 + image_type * 4300 + width * 430 + height * 400."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 225) * 3000 + it * 4300 + w * 430 + h * 400


def xcf_file_size_times_67_plus_image_type_times_4800_plus_width_times_height_times_2000(file_path: "str | Path") -> int:
    """Return file_size * 67 + image_type * 4800 + width * height * 2000."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 67 + it * 4800 + w * h * 2000


def xcf_file_size_mod_509_times_900_plus_image_type_times_5000_plus_width_times_height_times_4300(file_path: "str | Path") -> int:
    """Return (file_size % 509) * 900 + image_type * 5000 + width * height * 4300."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 509) * 900 + it * 5000 + w * h * 4300


def xcf_file_size_mod_521_times_850_plus_image_type_times_2000_plus_layer_count_times_5000(file_path: "str | Path") -> int:
    """Return (file_size % 521) * 850 + image_type * 2000 + layer_count * 5000."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    lc = xcf_layer_count(file_path)
    return (fs % 521) * 850 + it * 2000 + lc * 5000


def xcf_file_size_mod_229_times_3050_plus_image_type_times_4400_plus_width_times_440_plus_height_times_410(file_path: "str | Path") -> int:
    """Return (file_size % 229) * 3050 + image_type * 4400 + width * 440 + height * 410."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 229) * 3050 + it * 4400 + w * 440 + h * 410


def xcf_file_size_times_69_plus_image_type_times_4900_plus_width_times_height_times_2050(file_path: "str | Path") -> int:
    """Return file_size * 69 + image_type * 4900 + width * height * 2050."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 69 + it * 4900 + w * h * 2050


def xcf_file_size_mod_523_times_925_plus_image_type_times_5100_plus_width_times_height_times_4400(file_path: "str | Path") -> int:
    """Return (file_size % 523) * 925 + image_type * 5100 + width * height * 4400."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 523) * 925 + it * 5100 + w * h * 4400


def xcf_file_size_mod_541_times_875_plus_image_type_times_2050_plus_layer_count_times_5100(file_path: "str | Path") -> int:
    """Return (file_size % 541) * 875 + image_type * 2050 + layer_count * 5100."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    lc = xcf_layer_count(file_path)
    return (fs % 541) * 875 + it * 2050 + lc * 5100


def xcf_file_size_mod_237_times_3100_plus_image_type_times_4500_plus_width_times_450_plus_height_times_420(file_path: "str | Path") -> int:
    """Return (file_size % 237) * 3100 + image_type * 4500 + width * 450 + height * 420."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 237) * 3100 + it * 4500 + w * 450 + h * 420


def xcf_file_size_times_71_plus_image_type_times_5000_plus_width_times_height_times_2100(file_path: "str | Path") -> int:
    """Return file_size * 71 + image_type * 5000 + width * height * 2100."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 71 + it * 5000 + w * h * 2100


def xcf_file_size_mod_547_times_950_plus_image_type_times_5200_plus_width_times_height_times_4500(file_path: "str | Path") -> int:
    """Return (file_size % 547) * 950 + image_type * 5200 + width * height * 4500."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 547) * 950 + it * 5200 + w * h * 4500


def xcf_file_size_mod_557_times_900_plus_image_type_times_2100_plus_layer_count_times_5200(file_path: "str | Path") -> int:
    """Return (file_size % 557) * 900 + image_type * 2100 + layer_count * 5200."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    lc = xcf_layer_count(file_path)
    return (fs % 557) * 900 + it * 2100 + lc * 5200


def xcf_file_size_mod_243_times_3150_plus_image_type_times_4600_plus_width_times_460_plus_height_times_430(file_path: "str | Path") -> int:
    """Return (file_size % 243) * 3150 + image_type * 4600 + width * 460 + height * 430."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 243) * 3150 + it * 4600 + w * 460 + h * 430


def xcf_file_size_times_73_plus_image_type_times_5100_plus_width_times_height_times_2150(file_path: "str | Path") -> int:
    """Return file_size * 73 + image_type * 5100 + width * height * 2150."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 73 + it * 5100 + w * h * 2150


def xcf_file_size_mod_563_times_975_plus_image_type_times_5300_plus_width_times_height_times_4600(file_path: "str | Path") -> int:
    """Return (file_size % 563) * 975 + image_type * 5300 + width * height * 4600."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 563) * 975 + it * 5300 + w * h * 4600


def xcf_file_size_mod_569_times_925_plus_image_type_times_2150_plus_layer_count_times_5300(file_path: "str | Path") -> int:
    """Return (file_size % 569) * 925 + image_type * 2150 + layer_count * 5300."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    lc = xcf_layer_count(file_path)
    return (fs % 569) * 925 + it * 2150 + lc * 5300


def xcf_file_size_mod_247_times_3200_plus_image_type_times_4700_plus_width_times_470_plus_height_times_440(file_path: "str | Path") -> int:
    """Return (file_size % 247) * 3200 + image_type * 4700 + width * 470 + height * 440."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 247) * 3200 + it * 4700 + w * 470 + h * 440


def xcf_file_size_times_75_plus_image_type_times_5200_plus_width_times_height_times_2200(file_path: "str | Path") -> int:
    """Return file_size * 75 + image_type * 5200 + width * height * 2200."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 75 + it * 5200 + w * h * 2200


def xcf_file_size_mod_571_times_1000_plus_image_type_times_5400_plus_width_times_height_times_4700(file_path: "str | Path") -> int:
    """Return (file_size % 571) * 1000 + image_type * 5400 + width * height * 4700."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 571) * 1000 + it * 5400 + w * h * 4700


def xcf_file_size_mod_577_times_950_plus_image_type_times_2200_plus_layer_count_times_5400(file_path: "str | Path") -> int:
    """Return (file_size % 577) * 950 + image_type * 2200 + layer_count * 5400."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    lc = xcf_layer_count(file_path)
    return (fs % 577) * 950 + it * 2200 + lc * 5400


def xcf_file_size_mod_249_times_3250_plus_image_type_times_4800_plus_width_times_480_plus_height_times_450(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 249) * 3250 + it * 4800 + w * 480 + h * 450


def xcf_file_size_times_77_plus_image_type_times_5300_plus_width_times_height_times_2250(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 77 + it * 5300 + w * h * 2250


def xcf_file_size_mod_587_times_1025_plus_image_type_times_5500_plus_width_times_height_times_4800(file_path: "str | Path") -> int:
    """Return (file_size % 587) * 1025 + image_type * 5500 + width * height * 4800."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 587) * 1025 + it * 5500 + w * h * 4800


def xcf_file_size_mod_593_times_975_plus_image_type_times_2250_plus_layer_count_times_5500(file_path: "str | Path") -> int:
    """Return (file_size % 593) * 975 + image_type * 2250 + layer_count * 5500."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    lc = xcf_layer_count(file_path)
    return (fs % 593) * 975 + it * 2250 + lc * 5500


def xcf_file_size_mod_251_times_3300_plus_image_type_times_4900_plus_width_times_490_plus_height_times_460(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 251) * 3300 + it * 4900 + w * 490 + h * 460


def xcf_file_size_times_79_plus_image_type_times_5400_plus_width_times_height_times_2300(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 79 + it * 5400 + w * h * 2300


def xcf_file_size_mod_599_times_31_plus_image_type_times_5000_plus_width_times_height_times_4200(file_path: "str | Path") -> int:
    """Return (file_size % 599) * 31 + image_type * 5000 + width * height * 4200."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 599) * 31 + it * 5000 + w * h * 4200


def xcf_file_size_times_81_plus_image_type_times_5600_plus_width_times_height_times_2100(file_path: "str | Path") -> int:
    """Return file_size * 81 + image_type * 5600 + width * height * 2100."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 81 + it * 5600 + w * h * 2100


def xcf_file_size_mod_599_times_1050_plus_image_type_times_5600_plus_width_times_height_times_4900(file_path: "str | Path") -> int:
    """Return (file_size % 599) * 1050 + image_type * 5600 + width * height * 4900."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 599) * 1050 + it * 5600 + w * h * 4900


def xcf_file_size_mod_601_times_1000_plus_image_type_times_2300_plus_layer_count_times_5600(file_path: "str | Path") -> int:
    """Return (file_size % 601) * 1000 + image_type * 2300 + layer_count * 5600."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    lc = xcf_layer_count(file_path)
    return (fs % 601) * 1000 + it * 2300 + lc * 5600


def xcf_file_size_mod_253_times_3350_plus_image_type_times_5000_plus_width_times_500_plus_height_times_470(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 253) * 3350 + it * 5000 + w * 500 + h * 470


def xcf_file_size_times_81_plus_image_type_times_5500_plus_width_times_height_times_2350(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 81 + it * 5500 + w * h * 2350


def xcf_file_size_mod_607_times_1075_plus_image_type_times_5700_plus_width_times_height_times_5000(file_path: "str | Path") -> int:
    """Return (file_size % 607) * 1075 + image_type * 5700 + width * height * 5000."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 607) * 1075 + it * 5700 + w * h * 5000


def xcf_file_size_mod_613_times_1025_plus_image_type_times_2350_plus_layer_count_times_5700(file_path: "str | Path") -> int:
    """Return (file_size % 613) * 1025 + image_type * 2350 + layer_count * 5700."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    lc = xcf_layer_count(file_path)
    return (fs % 613) * 1025 + it * 2350 + lc * 5700


def xcf_file_size_mod_257_times_3400_plus_image_type_times_5100_plus_width_times_510_plus_height_times_480(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 257) * 3400 + it * 5100 + w * 510 + h * 480


def xcf_file_size_times_83_plus_image_type_times_5600_plus_width_times_height_times_2400(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 83 + it * 5600 + w * h * 2400


def xcf_file_size_mod_617_times_1100_plus_image_type_times_5800_plus_width_times_height_times_5100(file_path: "str | Path") -> int:
    """Return (file_size % 617) * 1100 + image_type * 5800 + width * height * 5100."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 617) * 1100 + it * 5800 + w * h * 5100


def xcf_file_size_mod_619_times_1050_plus_image_type_times_2400_plus_layer_count_times_5800(file_path: "str | Path") -> int:
    """Return (file_size % 619) * 1050 + image_type * 2400 + layer_count * 5800."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    lc = xcf_layer_count(file_path)
    return (fs % 619) * 1050 + it * 2400 + lc * 5800


def xcf_file_size_mod_259_times_3450_plus_image_type_times_5200_plus_width_times_520_plus_height_times_490(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 259) * 3450 + it * 5200 + w * 520 + h * 490


def xcf_file_size_times_85_plus_image_type_times_5700_plus_width_times_height_times_2450(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 85 + it * 5700 + w * h * 2450


def xcf_file_size_mod_263_times_3500_plus_image_type_times_5300_plus_width_times_530_plus_height_times_500(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 263) * 3500 + it * 5300 + w * 530 + h * 500


def xcf_file_size_times_87_plus_image_type_times_5800_plus_width_times_height_times_2500(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 87 + it * 5800 + w * h * 2500


def xcf_file_size_mod_631_times_1125_plus_image_type_times_5900_plus_width_times_height_times_5200(file_path: "str | Path") -> int:
    """Return (file_size % 631) * 1125 + image_type * 5900 + width * height * 5200."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 631) * 1125 + it * 5900 + w * h * 5200


def xcf_file_size_mod_641_times_1075_plus_image_type_times_2450_plus_layer_count_times_5900(file_path: "str | Path") -> int:
    """Return (file_size % 641) * 1075 + image_type * 2450 + layer_count * 5900."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    lc = xcf_layer_count(file_path)
    return (fs % 641) * 1075 + it * 2450 + lc * 5900


def xcf_file_size_mod_269_times_3550_plus_image_type_times_5400_plus_width_times_540_plus_height_times_510(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 269) * 3550 + it * 5400 + w * 540 + h * 510


def xcf_file_size_times_89_plus_image_type_times_5900_plus_width_times_height_times_2550(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 89 + it * 5900 + w * h * 2550


def xcf_file_size_mod_643_times_1150_plus_image_type_times_6000_plus_width_times_height_times_5300(file_path: "str | Path") -> int:
    """Return (file_size % 643) * 1150 + image_type * 6000 + width * height * 5300."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 643) * 1150 + it * 6000 + w * h * 5300


def xcf_file_size_mod_647_times_1100_plus_image_type_times_2500_plus_layer_count_times_6000(file_path: "str | Path") -> int:
    """Return (file_size % 647) * 1100 + image_type * 2500 + layer_count * 6000."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    lc = xcf_layer_count(file_path)
    return (fs % 647) * 1100 + it * 2500 + lc * 6000


def xcf_file_size_mod_653_times_31_plus_image_type_times_5200_plus_width_times_height_times_4400(file_path: "str | Path") -> int:
    """Return (file_size % 653) * 31 + image_type * 5200 + width * height * 4400."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 653) * 31 + it * 5200 + w * h * 4400


def xcf_file_size_times_91_plus_image_type_times_5700_plus_width_times_height_times_2200(file_path: "str | Path") -> int:
    """Return file_size * 91 + image_type * 5700 + width * height * 2200."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 91 + it * 5700 + w * h * 2200


def xcf_file_size_mod_279_times_3700_plus_image_type_times_5700_plus_width_times_560_plus_height_times_530(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 279) * 3700 + it * 5700 + w * 560 + h * 530


def xcf_file_size_times_93_plus_image_type_times_6100_plus_width_times_height_times_2700(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 93 + it * 6100 + w * h * 2700


def xcf_file_size_mod_653_times_1175_plus_image_type_times_6100_plus_width_times_height_times_5400(file_path: "str | Path") -> int:
    """Return (file_size % 653) * 1175 + image_type * 6100 + width * height * 5400."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 653) * 1175 + it * 6100 + w * h * 5400


def xcf_file_size_mod_659_times_1125_plus_image_type_times_2550_plus_layer_count_times_6100(file_path: "str | Path") -> int:
    """Return (file_size % 659) * 1125 + image_type * 2550 + layer_count * 6100."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    lc = xcf_layer_count(file_path)
    return (fs % 659) * 1125 + it * 2550 + lc * 6100


def xcf_file_size_mod_285_times_3800_plus_image_type_times_5800_plus_width_times_570_plus_height_times_540(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 285) * 3800 + it * 5800 + w * 570 + h * 540


def xcf_file_size_times_95_plus_image_type_times_6200_plus_width_times_height_times_2800(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 95 + it * 6200 + w * h * 2800


def xcf_file_size_mod_661_times_1200_plus_image_type_times_6200_plus_width_times_height_times_5500(file_path: "str | Path") -> int:
    """Return (file_size % 661) * 1200 + image_type * 6200 + width * height * 5500."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 661) * 1200 + it * 6200 + w * h * 5500


def xcf_file_size_mod_673_times_1150_plus_image_type_times_2600_plus_layer_count_times_6200(file_path: "str | Path") -> int:
    """Return (file_size % 673) * 1150 + image_type * 2600 + layer_count * 6200."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    lc = xcf_layer_count(file_path)
    return (fs % 673) * 1150 + it * 2600 + lc * 6200


def xcf_file_size_mod_287_times_3900_plus_image_type_times_5900_plus_width_times_580_plus_height_times_550(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 287) * 3900 + it * 5900 + w * 580 + h * 550


def xcf_file_size_times_97_plus_image_type_times_6300_plus_width_times_height_times_2900(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 97 + it * 6300 + w * h * 2900


def xcf_file_size_mod_677_times_1225_plus_image_type_times_6300_plus_width_times_height_times_5600(file_path: "str | Path") -> int:
    """Return (file_size % 677) * 1225 + image_type * 6300 + width * height * 5600."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 677) * 1225 + it * 6300 + w * h * 5600


def xcf_file_size_mod_683_times_1175_plus_image_type_times_2650_plus_layer_count_times_6300(file_path: "str | Path") -> int:
    """Return (file_size % 683) * 1175 + image_type * 2650 + layer_count * 6300."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    lc = xcf_layer_count(file_path)
    return (fs % 683) * 1175 + it * 2650 + lc * 6300


def xcf_file_size_mod_289_times_4000_plus_image_type_times_6000_plus_width_times_590_plus_height_times_560(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 289) * 4000 + it * 6000 + w * 590 + h * 560


def xcf_file_size_times_99_plus_image_type_times_6400_plus_width_times_height_times_3000(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 99 + it * 6400 + w * h * 3000


def xcf_file_size_mod_291_times_4100_plus_image_type_times_6100_plus_width_times_600_plus_height_times_570(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 291) * 4100 + it * 6100 + w * 600 + h * 570


def xcf_file_size_times_101_plus_image_type_times_6500_plus_width_times_height_times_3100(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 101 + it * 6500 + w * h * 3100


def xcf_file_size_mod_691_times_1250_plus_image_type_times_6400_plus_width_times_height_times_5700(file_path: "str | Path") -> int:
    """Return (file_size % 691) * 1250 + image_type * 6400 + width * height * 5700."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 691) * 1250 + it * 6400 + w * h * 5700


def xcf_file_size_mod_701_times_1200_plus_image_type_times_2700_plus_layer_count_times_6400(file_path: "str | Path") -> int:
    """Return (file_size % 701) * 1200 + image_type * 2700 + layer_count * 6400."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    lc = xcf_layer_count(file_path)
    return (fs % 701) * 1200 + it * 2700 + lc * 6400


def xcf_file_size_mod_295_times_4200_plus_image_type_times_6200_plus_width_times_610_plus_height_times_580(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 295) * 4200 + it * 6200 + w * 610 + h * 580


def xcf_file_size_times_103_plus_image_type_times_6600_plus_width_times_height_times_3200(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 103 + it * 6600 + w * h * 3200


def xcf_file_size_mod_297_times_4300_plus_image_type_times_6300_plus_width_times_620_plus_height_times_590(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 297) * 4300 + it * 6300 + w * 620 + h * 590


def xcf_file_size_times_105_plus_image_type_times_6700_plus_width_times_height_times_3300(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 105 + it * 6700 + w * h * 3300

def xcf_file_size_mod_659_times_31_plus_image_type_times_5400_plus_width_times_height_times_4600(file_path):
    fs = xcf_file_size_bytes(file_path); it = xcf_image_type_id(file_path); w = xcf_width(file_path); h = xcf_height(file_path)
    return (fs % 659) * 31 + it * 5400 + w * h * 4600

def xcf_file_size_times_105_plus_image_type_times_5800_plus_width_times_height_times_2300(file_path):
    fs = xcf_file_size_bytes(file_path); it = xcf_image_type_id(file_path); w = xcf_width(file_path); h = xcf_height(file_path)
    return fs * 105 + it * 5800 + w * h * 2300


def xcf_file_size_mod_709_times_1275_plus_image_type_times_6500_plus_width_times_height_times_5800(file_path):
    """Return (file_size % 709) * 1275 + image_type * 6500 + width * height * 5800."""
    fs = xcf_file_size_bytes(file_path); it = xcf_image_type_id(file_path); w = xcf_width(file_path); h = xcf_height(file_path)
    return (fs % 709) * 1275 + it * 6500 + w * h * 5800


def xcf_file_size_mod_719_times_1225_plus_image_type_times_2750_plus_layer_count_times_6500(file_path):
    """Return (file_size % 719) * 1225 + image_type * 2750 + layer_count * 6500."""
    fs = xcf_file_size_bytes(file_path); it = xcf_image_type_id(file_path); lc = xcf_layer_count(file_path)
    return (fs % 719) * 1225 + it * 2750 + lc * 6500


def xcf_file_size_mod_727_times_1300_plus_image_type_times_6600_plus_width_times_height_times_5900(file_path):
    """Return (file_size % 727) * 1300 + image_type * 6600 + width * height * 5900."""
    fs = xcf_file_size_bytes(file_path); it = xcf_image_type_id(file_path); w = xcf_width(file_path); h = xcf_height(file_path)
    return (fs % 727) * 1300 + it * 6600 + w * h * 5900


def xcf_file_size_mod_733_times_1250_plus_image_type_times_2800_plus_layer_count_times_6600(file_path):
    """Return (file_size % 733) * 1250 + image_type * 2800 + layer_count * 6600."""
    fs = xcf_file_size_bytes(file_path); it = xcf_image_type_id(file_path); lc = xcf_layer_count(file_path)
    return (fs % 733) * 1250 + it * 2800 + lc * 6600


def xcf_file_size_mod_739_times_1325_plus_image_type_times_6700_plus_width_times_height_times_6000(file_path):
    """Return (file_size % 739) * 1325 + image_type * 6700 + width * height * 6000."""
    fs = xcf_file_size_bytes(file_path); it = xcf_image_type_id(file_path); w = xcf_width(file_path); h = xcf_height(file_path)
    return (fs % 739) * 1325 + it * 6700 + w * h * 6000


def xcf_file_size_mod_743_times_1275_plus_image_type_times_2850_plus_layer_count_times_6700(file_path):
    """Return (file_size % 743) * 1275 + image_type * 2850 + layer_count * 6700."""
    fs = xcf_file_size_bytes(file_path); it = xcf_image_type_id(file_path); lc = xcf_layer_count(file_path)
    return (fs % 743) * 1275 + it * 2850 + lc * 6700


def xcf_file_size_mod_751_times_1350_plus_image_type_times_6800_plus_width_times_height_times_6100(file_path):
    """Return (file_size % 751) * 1350 + image_type * 6800 + width * height * 6100."""
    fs = xcf_file_size_bytes(file_path); it = xcf_image_type_id(file_path); w = xcf_width(file_path); h = xcf_height(file_path)
    return (fs % 751) * 1350 + it * 6800 + w * h * 6100


def xcf_file_size_mod_757_times_1300_plus_image_type_times_2900_plus_layer_count_times_6800(file_path):
    """Return (file_size % 757) * 1300 + image_type * 2900 + layer_count * 6800."""
    fs = xcf_file_size_bytes(file_path); it = xcf_image_type_id(file_path); lc = xcf_layer_count(file_path)
    return (fs % 757) * 1300 + it * 2900 + lc * 6800


def xcf_file_size_mod_761_times_1375_plus_image_type_times_6900_plus_width_times_height_times_6200(file_path):
    """Return (file_size % 761) * 1375 + image_type * 6900 + width * height * 6200."""
    fs = xcf_file_size_bytes(file_path); it = xcf_image_type_id(file_path); w = xcf_width(file_path); h = xcf_height(file_path)
    return (fs % 761) * 1375 + it * 6900 + w * h * 6200


def xcf_file_size_mod_769_times_1325_plus_image_type_times_2950_plus_layer_count_times_6900(file_path):
    """Return (file_size % 769) * 1325 + image_type * 2950 + layer_count * 6900."""
    fs = xcf_file_size_bytes(file_path); it = xcf_image_type_id(file_path); lc = xcf_layer_count(file_path)
    return (fs % 769) * 1325 + it * 2950 + lc * 6900


def xcf_file_size_mod_773_times_1400_plus_image_type_times_7000_plus_width_times_height_times_6300(file_path):
    """Return (file_size % 773) * 1400 + image_type * 7000 + width * height * 6300."""
    fs = xcf_file_size_bytes(file_path); it = xcf_image_type_id(file_path); w = xcf_width(file_path); h = xcf_height(file_path)
    return (fs % 773) * 1400 + it * 7000 + w * h * 6300


def xcf_file_size_mod_787_times_1350_plus_image_type_times_3000_plus_layer_count_times_7000(file_path):
    """Return (file_size % 787) * 1350 + image_type * 3000 + layer_count * 7000."""
    fs = xcf_file_size_bytes(file_path); it = xcf_image_type_id(file_path); lc = xcf_layer_count(file_path)
    return (fs % 787) * 1350 + it * 3000 + lc * 7000


def xcf_file_size_mod_797_times_1450_plus_image_type_times_7200_plus_width_times_height_times_6400(file_path):
    """Return (file_size % 797) * 1450 + image_type * 7200 + width * height * 6400."""
    fs = xcf_file_size_bytes(file_path); it = xcf_image_type_id(file_path); w = xcf_width(file_path); h = xcf_height(file_path)
    return (fs % 797) * 1450 + it * 7200 + w * h * 6400


def xcf_file_size_mod_809_times_1400_plus_image_type_times_3100_plus_layer_count_times_7200(file_path):
    """Return (file_size % 809) * 1400 + image_type * 3100 + layer_count * 7200."""
    fs = xcf_file_size_bytes(file_path); it = xcf_image_type_id(file_path); lc = xcf_layer_count(file_path)
    return (fs % 809) * 1400 + it * 3100 + lc * 7200


def xcf_file_size_mod_811_times_1500_plus_image_type_times_7400_plus_width_times_height_times_6500(file_path):
    """Return (file_size % 811) * 1500 + image_type * 7400 + width * height * 6500."""
    fs = xcf_file_size_bytes(file_path); it = xcf_image_type_id(file_path); w = xcf_width(file_path); h = xcf_height(file_path)
    return (fs % 811) * 1500 + it * 7400 + w * h * 6500


def xcf_file_size_mod_821_times_1450_plus_image_type_times_3200_plus_layer_count_times_7400(file_path):
    """Return (file_size % 821) * 1450 + image_type * 3200 + layer_count * 7400."""
    fs = xcf_file_size_bytes(file_path); it = xcf_image_type_id(file_path); lc = xcf_layer_count(file_path)
    return (fs % 821) * 1450 + it * 3200 + lc * 7400


def xcf_file_size_mod_823_times_1550_plus_image_type_times_7600_plus_width_times_height_times_6600(file_path):
    """Return (file_size % 823) * 1550 + image_type * 7600 + width * height * 6600."""
    fs = xcf_file_size_bytes(file_path); it = xcf_image_type_id(file_path); w = xcf_width(file_path); h = xcf_height(file_path)
    return (fs % 823) * 1550 + it * 7600 + w * h * 6600


def xcf_file_size_mod_827_times_1500_plus_image_type_times_3300_plus_layer_count_times_7600(file_path):
    """Return (file_size % 827) * 1500 + image_type * 3300 + layer_count * 7600."""
    fs = xcf_file_size_bytes(file_path); it = xcf_image_type_id(file_path); lc = xcf_layer_count(file_path)
    return (fs % 827) * 1500 + it * 3300 + lc * 7600


def xcf_file_size_mod_829_times_1600_plus_image_type_times_7800_plus_width_times_height_times_6700(file_path):
    """Return (file_size % 829) * 1600 + image_type * 7800 + width * height * 6700."""
    fs = xcf_file_size_bytes(file_path); it = xcf_image_type_id(file_path); w = xcf_width(file_path); h = xcf_height(file_path)
    return (fs % 829) * 1600 + it * 7800 + w * h * 6700


def xcf_file_size_mod_839_times_1550_plus_image_type_times_3400_plus_layer_count_times_7800(file_path):
    """Return (file_size % 839) * 1550 + image_type * 3400 + layer_count * 7800."""
    fs = xcf_file_size_bytes(file_path); it = xcf_image_type_id(file_path); lc = xcf_layer_count(file_path)
    return (fs % 839) * 1550 + it * 3400 + lc * 7800


def xcf_file_size_mod_299_times_4400_plus_image_type_times_6400_plus_width_times_630_plus_height_times_600(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 299) * 4400 + it * 6400 + w * 630 + h * 600


def xcf_file_size_times_107_plus_image_type_times_6800_plus_width_times_height_times_3400(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 107 + it * 6800 + w * h * 3400


def xcf_file_size_mod_301_times_4500_plus_image_type_times_6500_plus_width_times_640_plus_height_times_610(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 301) * 4500 + it * 6500 + w * 640 + h * 610


def xcf_file_size_times_109_plus_image_type_times_6900_plus_width_times_height_times_3500(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 109 + it * 6900 + w * h * 3500


def xcf_file_size_mod_303_times_4600_plus_image_type_times_6600_plus_width_times_650_plus_height_times_620(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 303) * 4600 + it * 6600 + w * 650 + h * 620


def xcf_file_size_times_111_plus_image_type_times_7100_plus_width_times_height_times_3600(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 111 + it * 7100 + w * h * 3600

def xcf_file_size_mod_661_times_31_plus_image_type_times_5500_plus_width_times_height_times_4800(file_path):
    fs = xcf_file_size_bytes(file_path); it = xcf_image_type_id(file_path); w = xcf_width(file_path); h = xcf_height(file_path)
    return (fs % 661) * 31 + it * 5500 + w * h * 4800

def xcf_file_size_times_113_plus_image_type_times_5900_plus_width_times_height_times_2400(file_path):
    fs = xcf_file_size_bytes(file_path); it = xcf_image_type_id(file_path); w = xcf_width(file_path); h = xcf_height(file_path)
    return fs * 113 + it * 5900 + w * h * 2400


def xcf_file_size_mod_305_times_4700_plus_image_type_times_6700_plus_width_times_660_plus_height_times_630(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 305) * 4700 + it * 6700 + w * 660 + h * 630


def xcf_file_size_times_115_plus_image_type_times_7300_plus_width_times_height_times_3700(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 115 + it * 7300 + w * h * 3700


def xcf_file_size_mod_307_times_4800_plus_image_type_times_6800_plus_width_times_670_plus_height_times_640(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 307) * 4800 + it * 6800 + w * 670 + h * 640


def xcf_file_size_times_117_plus_image_type_times_7500_plus_width_times_height_times_3800(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 117 + it * 7500 + w * h * 3800


def xcf_file_size_mod_309_times_4900_plus_image_type_times_6900_plus_width_times_680_plus_height_times_650(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 309) * 4900 + it * 6900 + w * 680 + h * 650


def xcf_file_size_times_119_plus_image_type_times_7700_plus_width_times_height_times_3900(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 119 + it * 7700 + w * h * 3900


def xcf_file_size_mod_311_times_5000_plus_image_type_times_7000_plus_width_times_690_plus_height_times_660(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 311) * 5000 + it * 7000 + w * 690 + h * 660


def xcf_file_size_times_121_plus_image_type_times_7900_plus_width_times_height_times_4000(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 121 + it * 7900 + w * h * 4000


def xcf_file_size_mod_313_times_5100_plus_image_type_times_7100_plus_width_times_700_plus_height_times_670(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 313) * 5100 + it * 7100 + w * 700 + h * 670


def xcf_file_size_times_123_plus_image_type_times_8100_plus_width_times_height_times_4100(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 123 + it * 8100 + w * h * 4100


def xcf_file_size_mod_673_times_31_plus_image_type_times_5600_plus_width_times_height_times_4900(file_path):
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 673) * 31 + it * 5600 + w * h * 4900


def xcf_file_size_times_125_plus_image_type_times_6100_plus_width_times_height_times_2500(file_path):
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 125 + it * 6100 + w * h * 2500


def xcf_file_size_mod_317_times_5200_plus_image_type_times_7200_plus_width_times_710_plus_height_times_680(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 317) * 5200 + it * 7200 + w * 710 + h * 680


def xcf_file_size_times_127_plus_image_type_times_8300_plus_width_times_height_times_4200(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 127 + it * 8300 + w * h * 4200


def xcf_file_size_mod_319_times_5300_plus_image_type_times_7300_plus_width_times_720_plus_height_times_690(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 319) * 5300 + it * 7300 + w * 720 + h * 690


def xcf_file_size_times_129_plus_image_type_times_8500_plus_width_times_height_times_4300(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 129 + it * 8500 + w * h * 4300


def xcf_file_size_mod_323_times_5400_plus_image_type_times_7400_plus_width_times_730_plus_height_times_700(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 323) * 5400 + it * 7400 + w * 730 + h * 700


def xcf_file_size_times_131_plus_image_type_times_8700_plus_width_times_height_times_4400(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 131 + it * 8700 + w * h * 4400


def xcf_file_size_mod_327_times_5500_plus_image_type_times_7500_plus_width_times_740_plus_height_times_710(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 327) * 5500 + it * 7500 + w * 740 + h * 710


def xcf_file_size_times_133_plus_image_type_times_8900_plus_width_times_height_times_4500(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 133 + it * 8900 + w * h * 4500


def xcf_file_size_mod_331_times_5600_plus_image_type_times_7600_plus_width_times_750_plus_height_times_720(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 331) * 5600 + it * 7600 + w * 750 + h * 720


def xcf_file_size_times_135_plus_image_type_times_9100_plus_width_times_height_times_4600(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 135 + it * 9100 + w * h * 4600


def xcf_file_size_mod_691_times_31_plus_image_type_times_5800_plus_width_times_height_times_5100(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 691) * 31 + it * 5800 + w * h * 5100


def xcf_file_size_times_137_plus_image_type_times_9300_plus_width_times_height_times_4700(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 137 + it * 9300 + w * h * 4700


def xcf_file_size_mod_341_times_5700_plus_image_type_times_7700_plus_width_times_760_plus_height_times_730(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 341) * 5700 + it * 7700 + w * 760 + h * 730


def xcf_file_size_times_139_plus_image_type_times_9500_plus_width_times_height_times_4800(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 139 + it * 9500 + w * h * 4800


def xcf_file_size_mod_347_times_5800_plus_image_type_times_7800_plus_width_times_770_plus_height_times_740(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 347) * 5800 + it * 7800 + w * 770 + h * 740


def xcf_file_size_times_141_plus_image_type_times_9700_plus_width_times_height_times_4900(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 141 + it * 9700 + w * h * 4900


def xcf_file_size_mod_353_times_5900_plus_image_type_times_7900_plus_width_times_780_plus_height_times_750(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 353) * 5900 + it * 7900 + w * 780 + h * 750


def xcf_file_size_times_143_plus_image_type_times_9900_plus_width_times_height_times_5000(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 143 + it * 9900 + w * h * 5000


def xcf_file_size_mod_359_times_6000_plus_image_type_times_8000_plus_width_times_790_plus_height_times_760(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 359) * 6000 + it * 8000 + w * 790 + h * 760


def xcf_file_size_times_145_plus_image_type_times_10000_plus_width_times_height_times_5100(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 145 + it * 10000 + w * h * 5100


def xcf_file_size_mod_367_times_6100_plus_image_type_times_8100_plus_width_times_800_plus_height_times_770(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 367) * 6100 + it * 8100 + w * 800 + h * 770


def xcf_file_size_times_147_plus_image_type_times_10100_plus_width_times_height_times_5200(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 147 + it * 10100 + w * h * 5200


def xcf_file_size_mod_373_times_6200_plus_image_type_times_8200_plus_width_times_810_plus_height_times_780(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 373) * 6200 + it * 8200 + w * 810 + h * 780


def xcf_file_size_times_149_plus_image_type_times_10200_plus_width_times_height_times_5300(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 149 + it * 10200 + w * h * 5300


def xcf_file_size_mod_379_times_6300_plus_image_type_times_8300_plus_width_times_820_plus_height_times_790(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 379) * 6300 + it * 8300 + w * 820 + h * 790


def xcf_file_size_times_151_plus_image_type_times_10300_plus_width_times_height_times_5400(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 151 + it * 10300 + w * h * 5400


def xcf_file_size_mod_383_times_6400_plus_image_type_times_8400_plus_width_times_830_plus_height_times_800(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 383) * 6400 + it * 8400 + w * 830 + h * 800


def xcf_file_size_times_153_plus_image_type_times_10500_plus_width_times_height_times_5500(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 153 + it * 10500 + w * h * 5500


def xcf_file_size_mod_383_times_6400_plus_image_type_times_8400_plus_width_times_830_plus_height_times_800(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 383) * 6400 + it * 8400 + w * 830 + h * 800


def xcf_file_size_times_153_plus_image_type_times_10400_plus_width_times_height_times_5500(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 153 + it * 10400 + w * h * 5500


def xcf_file_size_mod_389_times_6500_plus_image_type_times_8500_plus_width_times_840_plus_height_times_810(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 389) * 6500 + it * 8500 + w * 840 + h * 810


def xcf_file_size_times_155_plus_image_type_times_10500_plus_width_times_height_times_5600(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 155 + it * 10500 + w * h * 5600


def xcf_file_size_mod_397_times_6600_plus_image_type_times_8600_plus_width_times_850_plus_height_times_820(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 397) * 6600 + it * 8600 + w * 850 + h * 820


def xcf_file_size_times_157_plus_image_type_times_10600_plus_width_times_height_times_5700(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 157 + it * 10600 + w * h * 5700


def xcf_file_size_mod_401_times_6700_plus_image_type_times_8700_plus_width_times_860_plus_height_times_830(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 401) * 6700 + it * 8700 + w * 860 + h * 830


def xcf_file_size_times_159_plus_image_type_times_10700_plus_width_times_height_times_5800(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 159 + it * 10700 + w * h * 5800


def xcf_file_size_mod_409_times_6800_plus_image_type_times_8800_plus_width_times_870_plus_height_times_840(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 409) * 6800 + it * 8800 + w * 870 + h * 840


def xcf_file_size_times_161_plus_image_type_times_10800_plus_width_times_height_times_5900(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 161 + it * 10800 + w * h * 5900


def xcf_file_size_mod_419_times_6900_plus_image_type_times_8900_plus_width_times_880_plus_height_times_850(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 419) * 6900 + it * 8900 + w * 880 + h * 850


def xcf_file_size_times_163_plus_image_type_times_10900_plus_width_times_height_times_6000(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 163 + it * 10900 + w * h * 6000


def xcf_file_size_mod_419_times_6900_plus_image_type_times_8900_plus_width_times_880_plus_height_times_850(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 419) * 6900 + it * 8900 + w * 880 + h * 850


def xcf_file_size_times_163_plus_image_type_times_10900_plus_width_times_height_times_6000(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 163 + it * 10900 + w * h * 6000


def xcf_file_size_mod_421_times_7000_plus_image_type_times_9000_plus_width_times_890_plus_height_times_860(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 421) * 7000 + it * 9000 + w * 890 + h * 860


def xcf_file_size_times_165_plus_image_type_times_11000_plus_width_times_height_times_6100(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 165 + it * 11000 + w * h * 6100


def xcf_file_size_mod_431_times_7100_plus_image_type_times_9100_plus_width_times_900_plus_height_times_870(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 431) * 7100 + it * 9100 + w * 900 + h * 870


def xcf_file_size_times_167_plus_image_type_times_11100_plus_width_times_height_times_6200(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 167 + it * 11100 + w * h * 6200


def xcf_file_size_mod_431_times_7100_plus_image_type_times_9100_plus_width_times_900_plus_height_times_870(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 431) * 7100 + it * 9100 + w * 900 + h * 870


def xcf_file_size_times_167_plus_image_type_times_11100_plus_width_times_height_times_6200(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 167 + it * 11100 + w * h * 6200


def xcf_file_size_mod_433_times_7200_plus_image_type_times_9200_plus_width_times_910_plus_height_times_880(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 433) * 7200 + it * 9200 + w * 910 + h * 880


def xcf_file_size_times_169_plus_image_type_times_11200_plus_width_times_height_times_6300(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 169 + it * 11200 + w * h * 6300


def xcf_file_size_mod_439_times_7300_plus_image_type_times_9300_plus_width_times_920_plus_height_times_890(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 439) * 7300 + it * 9300 + w * 920 + h * 890


def xcf_file_size_times_173_plus_image_type_times_11300_plus_width_times_height_times_6400(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 173 + it * 11300 + w * h * 6400


def xcf_file_size_mod_439_times_7300_plus_image_type_times_9300_plus_width_times_920_plus_height_times_890(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 439) * 7300 + it * 9300 + w * 920 + h * 890


def xcf_file_size_times_171_plus_image_type_times_11300_plus_width_times_height_times_6400(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 171 + it * 11300 + w * h * 6400


def xcf_file_size_mod_443_times_7400_plus_image_type_times_9400_plus_width_times_930_plus_height_times_900(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 443) * 7400 + it * 9400 + w * 930 + h * 900


def xcf_file_size_times_173_plus_image_type_times_11400_plus_width_times_height_times_6500(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 173 + it * 11400 + w * h * 6500


def xcf_file_size_mod_449_times_7500_plus_image_type_times_9500_plus_width_times_940_plus_height_times_910(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 449) * 7500 + it * 9500 + w * 940 + h * 910


def xcf_file_size_times_175_plus_image_type_times_11500_plus_width_times_height_times_6600(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 175 + it * 11500 + w * h * 6600


def xcf_file_size_mod_457_times_7600_plus_image_type_times_9600_plus_width_times_950_plus_height_times_920(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 457) * 7600 + it * 9600 + w * 950 + h * 920


def xcf_file_size_times_177_plus_image_type_times_11600_plus_width_times_height_times_6700(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 177 + it * 11600 + w * h * 6700


def xcf_file_size_mod_461_times_7700_plus_image_type_times_9600_plus_width_times_950_plus_height_times_920(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 461) * 7700 + it * 9600 + w * 950 + h * 920


def xcf_file_size_times_179_plus_image_type_times_11700_plus_width_times_height_times_6700(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 179 + it * 11700 + w * h * 6700


def xcf_file_size_mod_463_times_7800_plus_image_type_times_9700_plus_width_times_960_plus_height_times_930(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 463) * 7800 + it * 9700 + w * 960 + h * 930


def xcf_file_size_times_181_plus_image_type_times_11800_plus_width_times_height_times_6800(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 181 + it * 11800 + w * h * 6800


def xcf_file_size_mod_467_times_7900_plus_image_type_times_9800_plus_width_times_970_plus_height_times_940(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 467) * 7900 + it * 9800 + w * 970 + h * 940


def xcf_file_size_times_183_plus_image_type_times_11900_plus_width_times_height_times_6900(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 183 + it * 11900 + w * h * 6900


def xcf_file_size_mod_479_times_8000_plus_image_type_times_9900_plus_width_times_980_plus_height_times_950(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 479) * 8000 + it * 9900 + w * 980 + h * 950


def xcf_file_size_times_185_plus_image_type_times_12000_plus_width_times_height_times_7000(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 185 + it * 12000 + w * h * 7000


def xcf_file_size_mod_487_times_8100_plus_image_type_times_10000_plus_width_times_990_plus_height_times_960(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 487) * 8100 + it * 10000 + w * 990 + h * 960


def xcf_file_size_times_187_plus_image_type_times_12100_plus_width_times_height_times_7100(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 187 + it * 12100 + w * h * 7100


def xcf_file_size_mod_491_times_8200_plus_image_type_times_10100_plus_width_times_1000_plus_height_times_970(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 491) * 8200 + it * 10100 + w * 1000 + h * 970


def xcf_file_size_times_189_plus_image_type_times_12200_plus_width_times_height_times_7200(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 189 + it * 12200 + w * h * 7200


def xcf_file_size_mod_499_times_8400_plus_image_type_times_10300_plus_width_times_1020_plus_height_times_990(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 499) * 8400 + it * 10300 + w * 1020 + h * 990


def xcf_file_size_times_191_plus_image_type_times_12300_plus_width_times_height_times_7300(file_path: "str | Path") -> int:
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 191 + it * 12300 + w * h * 7300


def xcf_file_size_mod_859_times_8500_plus_image_type_times_10400_plus_width_times_1030_plus_height_times_1000(file_path: "str | Path") -> int:
    """Return (file_size % 859) * 8500 + image_type * 10400 + width * 1030 + height * 1000."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 859) * 8500 + it * 10400 + w * 1030 + h * 1000


def xcf_file_size_mod_863_times_8600_plus_image_type_times_10500_plus_width_times_1040_plus_height_times_1010(file_path: "str | Path") -> int:
    """Return (file_size % 863) * 8600 + image_type * 10500 + width * 1040 + height * 1010."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 863) * 8600 + it * 10500 + w * 1040 + h * 1010


def xcf_file_size_mod_877_times_8700_plus_image_type_times_10600_plus_width_times_1050_plus_height_times_1020(file_path: "str | Path") -> int:
    """Return (file_size % 877) * 8700 + image_type * 10600 + width * 1050 + height * 1020."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 877) * 8700 + it * 10600 + w * 1050 + h * 1020


def xcf_file_size_mod_881_times_8800_plus_image_type_times_10700_plus_width_times_1060_plus_height_times_1030(file_path: "str | Path") -> int:
    """Return (file_size % 881) * 8800 + image_type * 10700 + width * 1060 + height * 1030."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 881) * 8800 + it * 10700 + w * 1060 + h * 1030


def xcf_file_size_mod_883_times_8900_plus_image_type_times_10800_plus_width_times_1070_plus_height_times_1040(file_path: "str | Path") -> int:
    """Return (file_size % 883) * 8900 + image_type * 10800 + width * 1070 + height * 1040."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 883) * 8900 + it * 10800 + w * 1070 + h * 1040


def xcf_file_size_times_193_plus_image_type_times_12400_plus_width_times_height_times_7400(file_path: "str | Path") -> int:
    """Return file_size * 193 + image_type * 12400 + width * height * 7400."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return fs * 193 + it * 12400 + w * h * 7400


def xcf_file_size_mod_911_times_8900_plus_image_type_times_10800_plus_width_times_1070_plus_height_times_1040(file_path: "str | Path") -> int:
    """Return (file_size % 911) * 8900 + image_type * 10800 + width * 1070 + height * 1040."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 911) * 8900 + it * 10800 + w * 1070 + h * 1040


def xcf_file_size_mod_919_times_9000_plus_image_type_times_10900_plus_width_times_1080_plus_height_times_1050(file_path: "str | Path") -> int:
    """Return (file_size % 919) * 9000 + image_type * 10900 + width * 1080 + height * 1050."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 919) * 9000 + it * 10900 + w * 1080 + h * 1050


def xcf_file_size_mod_929_times_9100_plus_image_type_times_11000_plus_width_times_1090_plus_height_times_1060(file_path: "str | Path") -> int:
    """Return (file_size % 929) * 9100 + image_type * 11000 + width * 1090 + height * 1060."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 929) * 9100 + it * 11000 + w * 1090 + h * 1060


def xcf_file_size_mod_937_times_9200_plus_image_type_times_11100_plus_width_times_1100_plus_height_times_1070(file_path: "str | Path") -> int:
    """Return (file_size % 937) * 9200 + image_type * 11100 + width * 1100 + height * 1070."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 937) * 9200 + it * 11100 + w * 1100 + h * 1070


def xcf_file_size_mod_941_times_9300_plus_image_type_times_11200_plus_width_times_1110_plus_height_times_1080(file_path: "str | Path") -> int:
    """Return (file_size % 941) * 9300 + image_type * 11200 + width * 1110 + height * 1080."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 941) * 9300 + it * 11200 + w * 1110 + h * 1080


def xcf_file_size_mod_947_times_9400_plus_image_type_times_11300_plus_width_times_1120_plus_height_times_1090(file_path: "str | Path") -> int:
    """Return (file_size % 947) * 9400 + image_type * 11300 + width * 1120 + height * 1090."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 947) * 9400 + it * 11300 + w * 1120 + h * 1090


def xcf_file_size_mod_953_times_9500_plus_image_type_times_11400_plus_width_times_1130_plus_height_times_1100(file_path: "str | Path") -> int:
    """Return (file_size % 953) * 9500 + image_type * 11400 + width * 1130 + height * 1100."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 953) * 9500 + it * 11400 + w * 1130 + h * 1100


def xcf_file_size_mod_967_times_9600_plus_image_type_times_11500_plus_width_times_1140_plus_height_times_1110(file_path: "str | Path") -> int:
    """Return (file_size % 967) * 9600 + image_type * 11500 + width * 1140 + height * 1110."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 967) * 9600 + it * 11500 + w * 1140 + h * 1110


def xcf_file_size_mod_971_times_9700_plus_image_type_times_11600_plus_width_times_1150_plus_height_times_1120(file_path: "str | Path") -> int:
    """Return (file_size % 971) * 9700 + image_type * 11600 + width * 1150 + height * 1120."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 971) * 9700 + it * 11600 + w * 1150 + h * 1120


def xcf_file_size_mod_977_times_9800_plus_image_type_times_11700_plus_width_times_1160_plus_height_times_1130(file_path: "str | Path") -> int:
    """Return (file_size % 977) * 9800 + image_type * 11700 + width * 1160 + height * 1130."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 977) * 9800 + it * 11700 + w * 1160 + h * 1130


def xcf_file_size_mod_983_times_9900_plus_image_type_times_11800_plus_width_times_1170_plus_height_times_1140(file_path: "str | Path") -> int:
    """Return (file_size % 983) * 9900 + image_type * 11800 + width * 1170 + height * 1140."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 983) * 9900 + it * 11800 + w * 1170 + h * 1140


def xcf_file_size_mod_991_times_10000_plus_image_type_times_11900_plus_width_times_1180_plus_height_times_1150(file_path: "str | Path") -> int:
    """Return (file_size % 991) * 10000 + image_type * 11900 + width * 1180 + height * 1150."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 991) * 10000 + it * 11900 + w * 1180 + h * 1150


def xcf_file_size_mod_997_times_10100_plus_image_type_times_12000_plus_width_times_1190_plus_height_times_1160(file_path: "str | Path") -> int:
    """Return (file_size % 997) * 10100 + image_type * 12000 + width * 1190 + height * 1160."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 997) * 10100 + it * 12000 + w * 1190 + h * 1160


def xcf_file_size_mod_1009_times_10200_plus_image_type_times_12100_plus_width_times_1200_plus_height_times_1170(file_path: "str | Path") -> int:
    """Return (file_size % 1009) * 10200 + image_type * 12100 + width * 1200 + height * 1170."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 1009) * 10200 + it * 12100 + w * 1200 + h * 1170


def xcf_file_size_mod_1013_times_10300_plus_image_type_times_12200_plus_width_times_1210_plus_height_times_1180(file_path: "str | Path") -> int:
    """Return (file_size % 1013) * 10300 + image_type * 12200 + width * 1210 + height * 1180."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 1013) * 10300 + it * 12200 + w * 1210 + h * 1180


def xcf_file_size_mod_1019_times_10400_plus_image_type_times_12300_plus_width_times_1220_plus_height_times_1190(file_path: "str | Path") -> int:
    """Return (file_size % 1019) * 10400 + image_type * 12300 + width * 1220 + height * 1190."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 1019) * 10400 + it * 12300 + w * 1220 + h * 1190


def xcf_file_size_mod_1021_times_10500_plus_image_type_times_12400_plus_width_times_1230_plus_height_times_1200(file_path: "str | Path") -> int:
    """Return (file_size % 1021) * 10500 + image_type * 12400 + width * 1230 + height * 1200."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 1021) * 10500 + it * 12400 + w * 1230 + h * 1200


def xcf_file_size_mod_1031_times_10600_plus_image_type_times_12500_plus_width_times_1240_plus_height_times_1210(file_path: "str | Path") -> int:
    """Return (file_size % 1031) * 10600 + image_type * 12500 + width * 1240 + height * 1210."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 1031) * 10600 + it * 12500 + w * 1240 + h * 1210


def xcf_file_size_mod_1033_times_10700_plus_image_type_times_12600_plus_width_times_1250_plus_height_times_1220(file_path: "str | Path") -> int:
    """Return (file_size % 1033) * 10700 + image_type * 12600 + width * 1250 + height * 1220."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 1033) * 10700 + it * 12600 + w * 1250 + h * 1220


def xcf_file_size_mod_1039_times_10800_plus_image_type_times_12700_plus_width_times_1260_plus_height_times_1230(file_path: "str | Path") -> int:
    """Return (file_size % 1039) * 10800 + image_type * 12700 + width * 1260 + height * 1230."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 1039) * 10800 + it * 12700 + w * 1260 + h * 1230


def xcf_file_size_mod_1049_times_10900_plus_image_type_times_12800_plus_width_times_1270_plus_height_times_1240(file_path: "str | Path") -> int:
    """Return (file_size % 1049) * 10900 + image_type * 12800 + width * 1270 + height * 1240."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 1049) * 10900 + it * 12800 + w * 1270 + h * 1240


def xcf_file_size_mod_1051_times_11000_plus_image_type_times_12900_plus_width_times_1280_plus_height_times_1250(file_path: "str | Path") -> int:
    """Return (file_size % 1051) * 11000 + image_type * 12900 + width * 1280 + height * 1250."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 1051) * 11000 + it * 12900 + w * 1280 + h * 1250


def xcf_file_size_mod_1061_times_11100_plus_image_type_times_13000_plus_width_times_1290_plus_height_times_1260(file_path: "str | Path") -> int:
    """Return (file_size % 1061) * 11100 + image_type * 13000 + width * 1290 + height * 1260."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 1061) * 11100 + it * 13000 + w * 1290 + h * 1260


def xcf_file_size_mod_1063_times_11200_plus_image_type_times_13100_plus_width_times_1300_plus_height_times_1270(file_path: "str | Path") -> int:
    """Return (file_size % 1063) * 11200 + image_type * 13100 + width * 1300 + height * 1270."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 1063) * 11200 + it * 13100 + w * 1300 + h * 1270


def xcf_file_size_mod_1061_times_11100_plus_image_type_times_13000_plus_width_times_1290_plus_height_times_1260(file_path: "str | Path") -> int:
    """Return (file_size % 1061) * 11100 + image_type * 13000 + width * 1290 + height * 1260."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 1061) * 11100 + it * 13000 + w * 1290 + h * 1260


def xcf_file_size_mod_1063_times_11200_plus_image_type_times_13100_plus_width_times_1300_plus_height_times_1270(file_path: "str | Path") -> int:
    """Return (file_size % 1063) * 11200 + image_type * 13100 + width * 1300 + height * 1270."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 1063) * 11200 + it * 13100 + w * 1300 + h * 1270


def xcf_file_size_mod_1069_times_11300_plus_image_type_times_13200_plus_width_times_1310_plus_height_times_1280(file_path: "str | Path") -> int:
    """Return (file_size % 1069) * 11300 + image_type * 13200 + width * 1310 + height * 1280."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 1069) * 11300 + it * 13200 + w * 1310 + h * 1280


def xcf_file_size_mod_1087_times_11400_plus_image_type_times_13300_plus_width_times_1320_plus_height_times_1290(file_path: "str | Path") -> int:
    """Return (file_size % 1087) * 11400 + image_type * 13300 + width * 1320 + height * 1290."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 1087) * 11400 + it * 13300 + w * 1320 + h * 1290


def xcf_file_size_mod_1069_times_11300_plus_image_type_times_13200_plus_width_times_1310_plus_height_times_1280(file_path: "str | Path") -> int:
    """Return (file_size % 1069) * 11300 + image_type * 13200 + width * 1310 + height * 1280."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 1069) * 11300 + it * 13200 + w * 1310 + h * 1280


def xcf_file_size_mod_1087_times_11400_plus_image_type_times_13300_plus_width_times_1320_plus_height_times_1290(file_path: "str | Path") -> int:
    """Return (file_size % 1087) * 11400 + image_type * 13300 + width * 1320 + height * 1290."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 1087) * 11400 + it * 13300 + w * 1320 + h * 1290


def xcf_file_size_mod_1091_times_11500_plus_image_type_times_13400_plus_width_times_1330_plus_height_times_1300(file_path: "str | Path") -> int:
    """Return (file_size % 1091) * 11500 + image_type * 13400 + width * 1330 + height * 1300."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 1091) * 11500 + it * 13400 + w * 1330 + h * 1300


def xcf_file_size_mod_1093_times_11600_plus_image_type_times_13500_plus_width_times_1340_plus_height_times_1310(file_path: "str | Path") -> int:
    """Return (file_size % 1093) * 11600 + image_type * 13500 + width * 1340 + height * 1310."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 1093) * 11600 + it * 13500 + w * 1340 + h * 1310


def xcf_file_size_mod_1091_times_11500_plus_image_type_times_13400_plus_width_times_1330_plus_height_times_1300(file_path: "str | Path") -> int:
    """Return (file_size % 1091) * 11500 + image_type * 13400 + width * 1330 + height * 1300."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 1091) * 11500 + it * 13400 + w * 1330 + h * 1300


def xcf_file_size_mod_1093_times_11600_plus_image_type_times_13500_plus_width_times_1340_plus_height_times_1310(file_path: "str | Path") -> int:
    """Return (file_size % 1093) * 11600 + image_type * 13500 + width * 1340 + height * 1310."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 1093) * 11600 + it * 13500 + w * 1340 + h * 1310


def xcf_file_size_mod_1097_times_11700_plus_image_type_times_13600_plus_width_times_1350_plus_height_times_1320(file_path: "str | Path") -> int:
    """Return (file_size % 1097) * 11700 + image_type * 13600 + width * 1350 + height * 1320."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 1097) * 11700 + it * 13600 + w * 1350 + h * 1320


def xcf_file_size_mod_1103_times_11800_plus_image_type_times_13700_plus_width_times_1360_plus_height_times_1330(file_path: "str | Path") -> int:
    """Return (file_size % 1103) * 11800 + image_type * 13700 + width * 1360 + height * 1330."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 1103) * 11800 + it * 13700 + w * 1360 + h * 1330


def xcf_file_size_mod_1097_times_11700_plus_image_type_times_13600_plus_width_times_1350_plus_height_times_1320(file_path):
    """Return (file_size % 1097) * 11700 + image_type * 13600 + width * 1350 + height * 1320."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 1097) * 11700 + it * 13600 + w * 1350 + h * 1320


def xcf_file_size_mod_1103_times_11800_plus_image_type_times_13700_plus_width_times_1360_plus_height_times_1330(file_path):
    """Return (file_size % 1103) * 11800 + image_type * 13700 + width * 1360 + height * 1330."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 1103) * 11800 + it * 13700 + w * 1360 + h * 1330


def xcf_file_size_mod_1109_times_11900_plus_image_type_times_13800_plus_width_times_1370_plus_height_times_1340(file_path):
    """Return (file_size % 1109) * 11900 + image_type * 13800 + width * 1370 + height * 1340."""
    fs = xcf_file_size_bytes(file_path)
    it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path)
    h2 = xcf_height(file_path)
    return (fs % 1109) * 11900 + it2 * 13800 + w2 * 1370 + h2 * 1340


def xcf_file_size_mod_1117_times_12000_plus_image_type_times_13900_plus_width_times_1380_plus_height_times_1350(file_path):
    """Return (file_size % 1117) * 12000 + image_type * 13900 + width * 1380 + height * 1350."""
    fs = xcf_file_size_bytes(file_path)
    it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path)
    h2 = xcf_height(file_path)
    return (fs % 1117) * 12000 + it2 * 13900 + w2 * 1380 + h2 * 1350


def xcf_file_size_mod_1109_times_11900_plus_image_type_times_13800_plus_width_times_1370_plus_height_times_1340(file_path: "str | Path") -> int:
    """Return (file_size % 1109) * 11900 + image_type * 13800 + width * 1370 + height * 1340."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 1109) * 11900 + it * 13800 + w * 1370 + h * 1340


def xcf_file_size_mod_1117_times_12000_plus_image_type_times_13900_plus_width_times_1380_plus_height_times_1350(file_path: "str | Path") -> int:
    """Return (file_size % 1117) * 12000 + image_type * 13900 + width * 1380 + height * 1350."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 1117) * 12000 + it * 13900 + w * 1380 + h * 1350


def xcf_file_size_mod_1123_times_12100_plus_image_type_times_14000_plus_width_times_1390_plus_height_times_1360(file_path):
    """Return (file_size % 1123) * 12100 + image_type * 14000 + width * 1390 + height * 1360."""
    fs = xcf_file_size_bytes(file_path)
    it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path)
    h2 = xcf_height(file_path)
    return (fs % 1123) * 12100 + it2 * 14000 + w2 * 1390 + h2 * 1360


def xcf_file_size_mod_1129_times_12200_plus_image_type_times_14100_plus_width_times_1400_plus_height_times_1370(file_path):
    """Return (file_size % 1129) * 12200 + image_type * 14100 + width * 1400 + height * 1370."""
    fs = xcf_file_size_bytes(file_path)
    it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path)
    h2 = xcf_height(file_path)
    return (fs % 1129) * 12200 + it2 * 14100 + w2 * 1400 + h2 * 1370


def xcf_file_size_mod_1123_times_12100_plus_image_type_times_14000_plus_width_times_1390_plus_height_times_1360(file_path: "str | Path") -> int:
    """Return (file_size % 1123) * 12100 + image_type * 14000 + width * 1390 + height * 1360."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 1123) * 12100 + it * 14000 + w * 1390 + h * 1360


def xcf_file_size_mod_1129_times_12200_plus_image_type_times_14100_plus_width_times_1400_plus_height_times_1370(file_path: "str | Path") -> int:
    """Return (file_size % 1129) * 12200 + image_type * 14100 + width * 1400 + height * 1370."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 1129) * 12200 + it * 14100 + w * 1400 + h * 1370


def xcf_file_size_mod_1151_times_12300_plus_image_type_times_14200_plus_width_times_1410_plus_height_times_1380(file_path):
    """Return (file_size % 1151) * 12300 + image_type * 14200 + width * 1410 + height * 1380."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1151) * 12300 + it2 * 14200 + w2 * 1410 + h2 * 1380


def xcf_file_size_mod_1153_times_12400_plus_image_type_times_14300_plus_width_times_1420_plus_height_times_1390(file_path):
    """Return (file_size % 1153) * 12400 + image_type * 14300 + width * 1420 + height * 1390."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1153) * 12400 + it2 * 14300 + w2 * 1420 + h2 * 1390


def xcf_file_size_mod_1163_times_12500_plus_image_type_times_14400_plus_width_times_1430_plus_height_times_1400(file_path):
    """Return (file_size % 1163) * 12500 + image_type * 14400 + width * 1430 + height * 1400."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1163) * 12500 + it2 * 14400 + w2 * 1430 + h2 * 1400


def xcf_file_size_mod_1171_times_12600_plus_image_type_times_14500_plus_width_times_1440_plus_height_times_1410(file_path):
    """Return (file_size % 1171) * 12600 + image_type * 14500 + width * 1440 + height * 1410."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1171) * 12600 + it2 * 14500 + w2 * 1440 + h2 * 1410


def xcf_file_size_mod_1163_times_12500_plus_image_type_times_14400_plus_width_times_1430_plus_height_times_1400(file_path: "str | Path") -> int:
    """Return (file_size % 1163) * 12500 + image_type * 14400 + width * 1430 + height * 1400."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 1163) * 12500 + it * 14400 + w * 1430 + h * 1400


def xcf_file_size_mod_1171_times_12600_plus_image_type_times_14500_plus_width_times_1440_plus_height_times_1410(file_path: "str | Path") -> int:
    """Return (file_size % 1171) * 12600 + image_type * 14500 + width * 1440 + height * 1410."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 1171) * 12600 + it * 14500 + w * 1440 + h * 1410


def xcf_file_size_mod_1181_times_12700_plus_image_type_times_14600_plus_width_times_1450_plus_height_times_1420(file_path):
    """Return (file_size % 1181) * 12700 + image_type * 14600 + width * 1450 + height * 1420."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1181) * 12700 + it2 * 14600 + w2 * 1450 + h2 * 1420


def xcf_file_size_mod_1187_times_12800_plus_image_type_times_14700_plus_width_times_1460_plus_height_times_1430(file_path):
    """Return (file_size % 1187) * 12800 + image_type * 14700 + width * 1460 + height * 1430."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1187) * 12800 + it2 * 14700 + w2 * 1460 + h2 * 1430


def xcf_file_size_mod_1193_times_12900_plus_image_type_times_14800_plus_width_times_1470_plus_height_times_1440(file_path):
    """Return (file_size % 1193) * 12900 + image_type * 14800 + width * 1470 + height * 1440."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1193) * 12900 + it2 * 14800 + w2 * 1470 + h2 * 1440


def xcf_file_size_mod_1201_times_13000_plus_image_type_times_14900_plus_width_times_1480_plus_height_times_1450(file_path):
    """Return (file_size % 1201) * 13000 + image_type * 14900 + width * 1480 + height * 1450."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1201) * 13000 + it2 * 14900 + w2 * 1480 + h2 * 1450


def xcf_file_size_mod_1213_times_13100_plus_image_type_times_15000_plus_width_times_1490_plus_height_times_1460(file_path):
    """Return (file_size % 1213) * 13100 + image_type * 15000 + width * 1490 + height * 1460."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1213) * 13100 + it2 * 15000 + w2 * 1490 + h2 * 1460


def xcf_file_size_mod_1217_times_13200_plus_image_type_times_15100_plus_width_times_1500_plus_height_times_1470(file_path):
    """Return (file_size % 1217) * 13200 + image_type * 15100 + width * 1500 + height * 1470."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1217) * 13200 + it2 * 15100 + w2 * 1500 + h2 * 1470


def xcf_file_size_mod_1223_times_13300_plus_image_type_times_15200_plus_width_times_1510_plus_height_times_1480(file_path):
    """Return (file_size % 1223) * 13300 + image_type * 15200 + width * 1510 + height * 1480."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1223) * 13300 + it2 * 15200 + w2 * 1510 + h2 * 1480


def xcf_file_size_mod_1229_times_13400_plus_image_type_times_15300_plus_width_times_1520_plus_height_times_1490(file_path):
    """Return (file_size % 1229) * 13400 + image_type * 15300 + width * 1520 + height * 1490."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1229) * 13400 + it2 * 15300 + w2 * 1520 + h2 * 1490


def xcf_file_size_mod_1231_times_13500_plus_image_type_times_15400_plus_width_times_1530_plus_height_times_1500(file_path):
    """Return (file_size % 1231) * 13500 + image_type * 15400 + width * 1530 + height * 1500."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1231) * 13500 + it2 * 15400 + w2 * 1530 + h2 * 1500


def xcf_file_size_mod_1237_times_13600_plus_image_type_times_15500_plus_width_times_1540_plus_height_times_1510(file_path):
    """Return (file_size % 1237) * 13600 + image_type * 15500 + width * 1540 + height * 1510."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1237) * 13600 + it2 * 15500 + w2 * 1540 + h2 * 1510


def xcf_file_size_mod_1249_times_13700_plus_image_type_times_15600_plus_width_times_1550_plus_height_times_1520(file_path):
    """Return (file_size % 1249) * 13700 + image_type * 15600 + width * 1550 + height * 1520."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1249) * 13700 + it2 * 15600 + w2 * 1550 + h2 * 1520


def xcf_file_size_mod_1259_times_13800_plus_image_type_times_15700_plus_width_times_1560_plus_height_times_1530(file_path):
    """Return (file_size % 1259) * 13800 + image_type * 15700 + width * 1560 + height * 1530."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1259) * 13800 + it2 * 15700 + w2 * 1560 + h2 * 1530


def xcf_file_size_mod_1277_times_13900_plus_image_type_times_15800_plus_width_times_1570_plus_height_times_1540(file_path):
    """Return (file_size % 1277) * 13900 + image_type * 15800 + width * 1570 + height * 1540."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1277) * 13900 + it2 * 15800 + w2 * 1570 + h2 * 1540


def xcf_file_size_mod_1279_times_14000_plus_image_type_times_15900_plus_width_times_1580_plus_height_times_1550(file_path):
    """Return (file_size % 1279) * 14000 + image_type * 15900 + width * 1580 + height * 1550."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1279) * 14000 + it2 * 15900 + w2 * 1580 + h2 * 1550


def xcf_file_size_mod_1283_times_14100_plus_image_type_times_16000_plus_width_times_1590_plus_height_times_1560(file_path: "str | Path") -> int:
    """Return (file_size % 1283) * 14100 + image_type * 16000 + width * 1590 + height * 1560."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 1283) * 14100 + it * 16000 + w * 1590 + h * 1560


def xcf_file_size_mod_1289_times_14200_plus_image_type_times_16100_plus_width_times_1600_plus_height_times_1570(file_path: "str | Path") -> int:
    """Return (file_size % 1289) * 14200 + image_type * 16100 + width * 1600 + height * 1570."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 1289) * 14200 + it * 16100 + w * 1600 + h * 1570


def xcf_file_size_mod_1283_times_14100_plus_image_type_times_16000_plus_width_times_1590_plus_height_times_1560(file_path):
    """Return (file_size % 1283) * 14100 + image_type * 16000 + width * 1590 + height * 1560."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1283) * 14100 + it2 * 16000 + w2 * 1590 + h2 * 1560


def xcf_file_size_mod_1289_times_14200_plus_image_type_times_16100_plus_width_times_1600_plus_height_times_1570(file_path):
    """Return (file_size % 1289) * 14200 + image_type * 16100 + width * 1600 + height * 1570."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1289) * 14200 + it2 * 16100 + w2 * 1600 + h2 * 1570


def xcf_file_size_mod_1291_times_14300_plus_image_type_times_16200_plus_width_times_1610_plus_height_times_1580(file_path: "str | Path") -> int:
    """Return (file_size % 1291) * 14300 + image_type * 16200 + width * 1610 + height * 1580."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 1291) * 14300 + it * 16200 + w * 1610 + h * 1580


def xcf_file_size_mod_1297_times_14400_plus_image_type_times_16300_plus_width_times_1620_plus_height_times_1590(file_path: "str | Path") -> int:
    """Return (file_size % 1297) * 14400 + image_type * 16300 + width * 1620 + height * 1590."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 1297) * 14400 + it * 16300 + w * 1620 + h * 1590


def xcf_file_size_mod_1291_times_14300_plus_image_type_times_16200_plus_width_times_1610_plus_height_times_1580(file_path):
    """Return (file_size % 1291) * 14300 + image_type * 16200 + width * 1610 + height * 1580."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1291) * 14300 + it2 * 16200 + w2 * 1610 + h2 * 1580


def xcf_file_size_mod_1297_times_14400_plus_image_type_times_16300_plus_width_times_1620_plus_height_times_1590(file_path):
    """Return (file_size % 1297) * 14400 + image_type * 16300 + width * 1620 + height * 1590."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1297) * 14400 + it2 * 16300 + w2 * 1620 + h2 * 1590


def xcf_file_size_mod_1301_times_14500_plus_image_type_times_16400_plus_width_times_1630_plus_height_times_1600(file_path):
    """Return (file_size % 1301) * 14500 + image_type * 16400 + width * 1630 + height * 1600."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1301) * 14500 + it2 * 16400 + w2 * 1630 + h2 * 1600


def xcf_file_size_mod_1303_times_14600_plus_image_type_times_16500_plus_width_times_1640_plus_height_times_1610(file_path):
    """Return (file_size % 1303) * 14600 + image_type * 16500 + width * 1640 + height * 1610."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1303) * 14600 + it2 * 16500 + w2 * 1640 + h2 * 1610


def xcf_file_size_mod_1307_times_14700_plus_image_type_times_16600_plus_width_times_1650_plus_height_times_1620(file_path):
    """Return (file_size % 1307) * 14700 + image_type * 16600 + width * 1650 + height * 1620."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1307) * 14700 + it2 * 16600 + w2 * 1650 + h2 * 1620


def xcf_file_size_mod_1319_times_14800_plus_image_type_times_16700_plus_width_times_1660_plus_height_times_1630(file_path):
    """Return (file_size % 1319) * 14800 + image_type * 16700 + width * 1660 + height * 1630."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1319) * 14800 + it2 * 16700 + w2 * 1660 + h2 * 1630


def xcf_file_size_mod_1321_times_14900_plus_image_type_times_16800_plus_width_times_1670_plus_height_times_1640(file_path):
    """Return (file_size % 1321) * 14900 + image_type * 16800 + width * 1670 + height * 1640."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 1321) * 14900 + it * 16800 + w * 1670 + h * 1640


def xcf_file_size_mod_1327_times_15000_plus_image_type_times_16900_plus_width_times_1680_plus_height_times_1650(file_path):
    """Return (file_size % 1327) * 15000 + image_type * 16900 + width * 1680 + height * 1650."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 1327) * 15000 + it * 16900 + w * 1680 + h * 1650


def xcf_file_size_mod_1321_times_14900_plus_image_type_times_16800_plus_width_times_1670_plus_height_times_1640(file_path):
    """Return (file_size % 1321) * 14900 + image_type * 16800 + width * 1670 + height * 1640."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1321) * 14900 + it2 * 16800 + w2 * 1670 + h2 * 1640


def xcf_file_size_mod_1327_times_15000_plus_image_type_times_16900_plus_width_times_1680_plus_height_times_1650(file_path):
    """Return (file_size % 1327) * 15000 + image_type * 16900 + width * 1680 + height * 1650."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1327) * 15000 + it2 * 16900 + w2 * 1680 + h2 * 1650


def xcf_file_size_mod_1361_times_15100_plus_image_type_times_17000_plus_width_times_1690_plus_height_times_1660(file_path):
    """Return (file_size % 1361) * 15100 + image_type * 17000 + width * 1690 + height * 1660."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 1361) * 15100 + it * 17000 + w * 1690 + h * 1660


def xcf_file_size_mod_1367_times_15200_plus_image_type_times_17100_plus_width_times_1700_plus_height_times_1670(file_path):
    """Return (file_size % 1367) * 15200 + image_type * 17100 + width * 1700 + height * 1670."""
    fs = xcf_file_size_bytes(file_path)
    it = xcf_image_type_id(file_path)
    w = xcf_width(file_path)
    h = xcf_height(file_path)
    return (fs % 1367) * 15200 + it * 17100 + w * 1700 + h * 1670


def xcf_file_size_mod_1361_times_15100_plus_image_type_times_17000_plus_width_times_1690_plus_height_times_1660(file_path):
    """Return (file_size % 1361) * 15100 + image_type * 17000 + width * 1690 + height * 1660."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1361) * 15100 + it2 * 17000 + w2 * 1690 + h2 * 1660


def xcf_file_size_mod_1367_times_15200_plus_image_type_times_17100_plus_width_times_1700_plus_height_times_1670(file_path):
    """Return (file_size % 1367) * 15200 + image_type * 17100 + width * 1700 + height * 1670."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1367) * 15200 + it2 * 17100 + w2 * 1700 + h2 * 1670

def xcf_file_size_mod_1373_times_15300_plus_image_type_times_17200_plus_width_times_1710_plus_height_times_1680(file_path):
    """Return (file_size % 1373) * 15300 + image_type * 17200 + width * 1710 + height * 1680."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1373) * 15300 + it2 * 17200 + w2 * 1710 + h2 * 1680

def xcf_file_size_mod_1381_times_15400_plus_image_type_times_17300_plus_width_times_1720_plus_height_times_1690(file_path):
    """Return (file_size % 1381) * 15400 + image_type * 17300 + width * 1720 + height * 1690."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1381) * 15400 + it2 * 17300 + w2 * 1720 + h2 * 1690

def xcf_file_size_mod_1399_times_15500_plus_image_type_times_17400_plus_width_times_1730_plus_height_times_1700(file_path):
    """Return (file_size % 1399) * 15500 + image_type * 17400 + width * 1730 + height * 1700."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1399) * 15500 + it2 * 17400 + w2 * 1730 + h2 * 1700

def xcf_file_size_mod_1409_times_15600_plus_image_type_times_17500_plus_width_times_1740_plus_height_times_1710(file_path):
    """Return (file_size % 1409) * 15600 + image_type * 17500 + width * 1740 + height * 1710."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1409) * 15600 + it2 * 17500 + w2 * 1740 + h2 * 1710

def xcf_file_size_mod_1423_times_15700_plus_image_type_times_17600_plus_width_times_1750_plus_height_times_1720(file_path):
    """Return (file_size % 1423) * 15700 + image_type * 17600 + width * 1750 + height * 1720."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1423) * 15700 + it2 * 17600 + w2 * 1750 + h2 * 1720

def xcf_file_size_mod_1427_times_15800_plus_image_type_times_17700_plus_width_times_1760_plus_height_times_1730(file_path):
    """Return (file_size % 1427) * 15800 + image_type * 17700 + width * 1760 + height * 1730."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1427) * 15800 + it2 * 17700 + w2 * 1760 + h2 * 1730

def xcf_file_size_mod_1429_times_15900_plus_image_type_times_17800_plus_width_times_1770_plus_height_times_1740(file_path):
    """Return (file_size % 1429) * 15900 + image_type * 17800 + width * 1770 + height * 1740."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1429) * 15900 + it2 * 17800 + w2 * 1770 + h2 * 1740

def xcf_file_size_mod_1433_times_16000_plus_image_type_times_17900_plus_width_times_1780_plus_height_times_1750(file_path):
    """Return (file_size % 1433) * 16000 + image_type * 17900 + width * 1780 + height * 1750."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1433) * 16000 + it2 * 17900 + w2 * 1780 + h2 * 1750

def xcf_file_size_mod_1439_times_16100_plus_image_type_times_18000_plus_width_times_1790_plus_height_times_1760(file_path):
    """Return (file_size % 1439) * 16100 + image_type * 18000 + width * 1790 + height * 1760."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1439) * 16100 + it2 * 18000 + w2 * 1790 + h2 * 1760

def xcf_file_size_mod_1447_times_16200_plus_image_type_times_18100_plus_width_times_1800_plus_height_times_1770(file_path):
    """Return (file_size % 1447) * 16200 + image_type * 18100 + width * 1800 + height * 1770."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1447) * 16200 + it2 * 18100 + w2 * 1800 + h2 * 1770


def xcf_file_size_mod_1451_times_16300_plus_image_type_times_18200_plus_width_times_1810_plus_height_times_1780(file_path):
    """Return (file_size % 1451) * 16300 + image_type * 18200 + width * 1810 + height * 1780."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1451) * 16300 + it2 * 18200 + w2 * 1810 + h2 * 1780


def xcf_file_size_mod_1453_times_16400_plus_image_type_times_18300_plus_width_times_1820_plus_height_times_1790(file_path):
    """Return (file_size % 1453) * 16400 + image_type * 18300 + width * 1820 + height * 1790."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1453) * 16400 + it2 * 18300 + w2 * 1820 + h2 * 1790

def xcf_file_size_mod_1451_times_16300_plus_image_type_times_18200_plus_width_times_1810_plus_height_times_1780(file_path):
    """Return (file_size % 1451) * 16300 + image_type * 18200 + width * 1810 + height * 1780."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1451) * 16300 + it2 * 18200 + w2 * 1810 + h2 * 1780

def xcf_file_size_mod_1453_times_16400_plus_image_type_times_18300_plus_width_times_1820_plus_height_times_1790(file_path):
    """Return (file_size % 1453) * 16400 + image_type * 18300 + width * 1820 + height * 1790."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1453) * 16400 + it2 * 18300 + w2 * 1820 + h2 * 1790

def xcf_file_size_mod_1459_times_16500_plus_image_type_times_18400_plus_width_times_1830_plus_height_times_1800(file_path):
    """Return (file_size % 1459) * 16500 + image_type * 18400 + width * 1830 + height * 1800."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1459) * 16500 + it2 * 18400 + w2 * 1830 + h2 * 1800

def xcf_file_size_mod_1471_times_16600_plus_image_type_times_18500_plus_width_times_1840_plus_height_times_1810(file_path):
    """Return (file_size % 1471) * 16600 + image_type * 18500 + width * 1840 + height * 1810."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1471) * 16600 + it2 * 18500 + w2 * 1840 + h2 * 1810

def xcf_file_size_mod_1481_times_16700_plus_image_type_times_18600_plus_width_times_1850_plus_height_times_1820(file_path):
    """Return (file_size % 1481) * 16700 + image_type * 18600 + width * 1850 + height * 1820."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1481) * 16700 + it2 * 18600 + w2 * 1850 + h2 * 1820

def xcf_file_size_mod_1483_times_16800_plus_image_type_times_18700_plus_width_times_1860_plus_height_times_1830(file_path):
    """Return (file_size % 1483) * 16800 + image_type * 18700 + width * 1860 + height * 1830."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1483) * 16800 + it2 * 18700 + w2 * 1860 + h2 * 1830

def xcf_file_size_mod_1487_times_16900_plus_image_type_times_18800_plus_width_times_1870_plus_height_times_1840(file_path):
    """Return (file_size % 1487) * 16900 + image_type * 18800 + width * 1870 + height * 1840."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1487) * 16900 + it2 * 18800 + w2 * 1870 + h2 * 1840

def xcf_file_size_mod_1489_times_17000_plus_image_type_times_18900_plus_width_times_1880_plus_height_times_1850(file_path):
    """Return (file_size % 1489) * 17000 + image_type * 18900 + width * 1880 + height * 1850."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1489) * 17000 + it2 * 18900 + w2 * 1880 + h2 * 1850

def xcf_file_size_mod_1493_times_17100_plus_image_type_times_19000_plus_width_times_1890_plus_height_times_1860(file_path):
    """Return (file_size % 1493) * 17100 + image_type * 19000 + width * 1890 + height * 1860."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1493) * 17100 + it2 * 19000 + w2 * 1890 + h2 * 1860

def xcf_file_size_mod_1499_times_17200_plus_image_type_times_19100_plus_width_times_1900_plus_height_times_1870(file_path):
    """Return (file_size % 1499) * 17200 + image_type * 19100 + width * 1900 + height * 1870."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1499) * 17200 + it2 * 19100 + w2 * 1900 + h2 * 1870

def xcf_file_size_mod_1511_times_17300_plus_image_type_times_19200_plus_width_times_1910_plus_height_times_1880(file_path):
    """Return (file_size % 1511) * 17300 + image_type * 19200 + width * 1910 + height * 1880."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1511) * 17300 + it2 * 19200 + w2 * 1910 + h2 * 1880

def xcf_file_size_mod_1523_times_17400_plus_image_type_times_19300_plus_width_times_1920_plus_height_times_1890(file_path):
    """Return (file_size % 1523) * 17400 + image_type * 19300 + width * 1920 + height * 1890."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1523) * 17400 + it2 * 19300 + w2 * 1920 + h2 * 1890

def xcf_file_size_mod_1531_times_17500_plus_image_type_times_19400_plus_width_times_1930_plus_height_times_1900(file_path):
    """Return (file_size % 1531) * 17500 + image_type * 19400 + width * 1930 + height * 1900."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1531) * 17500 + it2 * 19400 + w2 * 1930 + h2 * 1900

def xcf_file_size_mod_1543_times_17600_plus_image_type_times_19500_plus_width_times_1940_plus_height_times_1910(file_path):
    """Return (file_size % 1543) * 17600 + image_type * 19500 + width * 1940 + height * 1910."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1543) * 17600 + it2 * 19500 + w2 * 1940 + h2 * 1910

def xcf_file_size_mod_1549_times_17700_plus_image_type_times_19600_plus_width_times_1950_plus_height_times_1920(file_path):
    """Return (file_size % 1549) * 17700 + image_type * 19600 + width * 1950 + height * 1920."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1549) * 17700 + it2 * 19600 + w2 * 1950 + h2 * 1920

def xcf_file_size_mod_1553_times_17800_plus_image_type_times_19700_plus_width_times_1960_plus_height_times_1930(file_path):
    """Return (file_size % 1553) * 17800 + image_type * 19700 + width * 1960 + height * 1930."""
    fs = xcf_file_size_bytes(file_path); it2 = xcf_image_type_id(file_path)
    w2 = xcf_width(file_path); h2 = xcf_height(file_path)
    return (fs % 1553) * 17800 + it2 * 19700 + w2 * 1960 + h2 * 1930


# --- Residual analytics functions appended from xcf_parser.py (TC-FODG-COMPLETE-001) ---
def xcf_width_plus_height(file_path: str | Path) -> int:
    """Return the sum of canvas width and height."""
    img = parse_xcf_strict(file_path)
    return img.width + img.height


def xcf_num_layers_plus_image_type_id(file_path: str | Path) -> int:
    """Return num_layers plus image_type_id (0=RGB, 1=GRAY, 2=INDEXED)."""
    img = parse_xcf_strict(file_path)
    return img.num_layers + img.image_type




# --- minus_/div_ analytics appended from source file (TC-FODG-COMPLETE-001) ---
def xcf_file_size_minus_header(file_path: str | Path) -> int:
    """Return file size in bytes minus the 26-byte XCF header. 0 if file smaller than header."""
    import os as _os
    size = _os.path.getsize(file_path)
    return max(0, size - 26)


def xcf_file_size_minus_width(file_path: str | Path) -> int:
    """Return file size in bytes minus canvas width. 0 if result would be negative."""
    import os as _os
    img = parse_xcf_strict(file_path)
    return max(0, _os.path.getsize(file_path) - img.width)


