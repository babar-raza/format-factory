"""
FODG analytics functions.

All analytics/statistics functions for the FODG format package.
Imports core functions from .fodg_codec for use in analytics computations.
"""
from __future__ import annotations

import os
from pathlib import Path

# Import core codec functions that analytics functions depend on
from .fodg_codec import (
    load,
    get_page_count,
    get_shape_count,
    get_page_metadata,
    extract_text,
    count_shapes,
    total_text_length,
    get_all_text,
    get_page_text,
)
from .fodg_analytics_extra import *

def fodg_text_item_count_plus_page_count(file_path: "str | bytes | Path") -> int:
    """Return the sum of text item count and page count."""
    return fodg_text_item_count(file_path) + fodg_page_count(file_path)

def fodg_total_shape_count_plus_text_item_count(file_path: "str | bytes | Path") -> int:
    """Return the sum of total shape count and text item count."""
    return fodg_total_shape_count(file_path) + fodg_text_item_count(file_path)

def fodg_page_count_plus_shape_count(file_path: "str | bytes | Path") -> int:
    """Return the sum of page count and total shape count."""
    return fodg_page_count(file_path) + fodg_total_shape_count(file_path)

def fodg_non_text_shape_count_plus_text_item_count(file_path: "str | bytes | Path") -> int:
    """Return the sum of non-text shape count and text item count."""
    return fodg_non_text_shape_count(file_path) + fodg_text_item_count(file_path)

def fodg_shape_plus_text_plus_page_count(file_path: "str | bytes | Path") -> int:
    """Return sum of total shapes, text items, and page count."""
    doc = load(file_path)
    pages = doc.get("pages", [])
    shapes = sum(p.get("shape_count", 0) for p in pages)
    texts = sum(len(p.get("text_content", [])) for p in pages)
    return shapes + texts + len(pages)

def fodg_file_size_plus_page_count(file_path: "str | bytes | Path") -> int:
    """Return file size in bytes plus total page count."""
    return fodg_file_size_bytes(file_path) + fodg_page_count(file_path)

def fodg_shape_count_times_two_plus_text_count(file_path: "str | bytes | Path") -> int:
    """Return total shape count multiplied by two plus total text item count."""
    return fodg_total_shape_count(file_path) * 2 + fodg_text_item_count(file_path)

def fodg_file_size_minus_shape_count_hundreds(file_path: "str | bytes | Path") -> int:
    """Return file size in bytes minus shape count multiplied by 100. 0 if result negative."""
    return max(0, fodg_file_size_bytes(file_path) - fodg_total_shape_count(file_path) * 100)

def fodg_shapes_plus_texts_squared(file_path: "str | bytes | Path") -> int:
    """Return the square of (total shape count + total text item count)."""
    total = fodg_total_shape_count(file_path) + fodg_text_item_count(file_path)
    return total * total

def fodg_file_size_div_10(file_path: "str | bytes | Path") -> int:
    """Return file size in bytes divided by 10 (integer floor division)."""
    return fodg_file_size_bytes(file_path) // 10

def fodg_shape_count_squared_plus_text_count_squared(file_path: "str | bytes | Path") -> int:
    """Return sum of shape count squared and text item count squared."""
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return sc * sc + tc * tc

def fodg_file_size_div_shape_count(file_path: "str | bytes | Path") -> int:
    """Return file size in bytes divided by shape count (floor). 0 if no shapes."""
    sc = fodg_total_shape_count(file_path)
    if sc == 0:
        return 0
    return fodg_file_size_bytes(file_path) // sc

def fodg_max_shapes_per_page_plus_page_count(file_path: "str | bytes | Path") -> int:
    """Return the sum of max shapes per page and total page count."""
    return fodg_max_shapes_per_page(file_path) + fodg_page_count(file_path)

def fodg_shape_count_plus_page_count_squared(file_path: "str | bytes | Path") -> int:
    """Return the square of (total shape count + page count)."""
    total = fodg_total_shape_count(file_path) + fodg_page_count(file_path)
    return total * total

def fodg_text_count_plus_page_count(file_path: "str | bytes | Path") -> int:
    """Return the sum of text item count and page count."""
    return fodg_text_item_count(file_path) + fodg_page_count(file_path)

def fodg_shape_plus_text_count(file_path: "str | bytes | Path") -> int:
    """Return the sum of total shape count and text item count."""
    return fodg_total_shape_count(file_path) + fodg_text_item_count(file_path)

def fodg_max_shapes_plus_text_count(file_path: "str | bytes | Path") -> int:
    """Return the sum of max shapes per page and text item count."""
    return fodg_max_shapes_per_page(file_path) + fodg_text_item_count(file_path)

def fodg_shape_count_div_page_count(file_path: "str | bytes | Path") -> int:
    """Return integer floor division of total shape count by page count."""
    pages = fodg_page_count(file_path)
    return fodg_total_shape_count(file_path) // pages if pages > 0 else 0

def fodg_shape_plus_text_times_page(file_path: "str | bytes | Path") -> int:
    """Return (total shape count + text item count) * page count."""
    return (fodg_total_shape_count(file_path) + fodg_text_item_count(file_path)) * fodg_page_count(file_path)

def fodg_total_shape_count_plus_page_count(file_path: "str | bytes | Path") -> int:
    """Return total shape count plus page count."""
    return fodg_total_shape_count(file_path) + fodg_page_count(file_path)

def fodg_shape_count_minus_page_count(file_path: "str | bytes | Path") -> int:
    """Return total shape count minus page count."""
    return fodg_total_shape_count(file_path) - fodg_page_count(file_path)

def fodg_text_count_plus_shape_count_squared(file_path: "str | bytes | Path") -> int:
    """Return text item count plus total shape count squared."""
    sc = fodg_total_shape_count(file_path)
    return fodg_text_item_count(file_path) + sc * sc

def fodg_text_times_shape_plus_page_count(file_path: "str | bytes | Path") -> int:
    """Return text_count * shape_count + page_count."""
    return (fodg_text_item_count(file_path) * fodg_total_shape_count(file_path)
            + fodg_page_count(file_path))

def fodg_page_count_plus_text_times_two(file_path: "str | bytes | Path") -> int:
    """Return page_count + text_item_count * 2."""
    return fodg_page_count(file_path) + fodg_text_item_count(file_path) * 2

def fodg_shape_count_plus_text_times_three(file_path: "str | bytes | Path") -> int:
    """Return shape_count + text_count * 3."""
    return (fodg_total_shape_count(file_path)
            + fodg_text_item_count(file_path) * 3)

def fodg_text_count_times_two_plus_shape_count(file_path: "str | bytes | Path") -> int:
    """Return text_count * 2 + shape_count."""
    return fodg_text_item_count(file_path) * 2 + fodg_total_shape_count(file_path)

def fodg_text_count_plus_shape_count_times_two(file_path: "str | bytes | Path") -> int:
    """Return text_count + (shape_count * 2)."""
    return fodg_text_item_count(file_path) + fodg_total_shape_count(file_path) * 2

def fodg_shape_count_squared_plus_text_count(file_path: "str | bytes | Path") -> int:
    """Return shape_count^2 + text_count."""
    return fodg_total_shape_count(file_path) ** 2 + fodg_text_item_count(file_path)

def fodg_shape_count_times_three_plus_text_count(file_path: "str | bytes | Path") -> int:
    """Return (shape_count * 3) + text_count."""
    return fodg_total_shape_count(file_path) * 3 + fodg_text_item_count(file_path)

def fodg_page_count_plus_shape_count_times_three(file_path: "str | bytes | Path") -> int:
    """Return page_count + (shape_count * 3)."""
    return fodg_page_count(file_path) + fodg_total_shape_count(file_path) * 3

def fodg_shape_count_plus_text_count_times_three(file_path: "str | bytes | Path") -> int:
    """Return shape_count + (text_count * 3)."""
    return fodg_total_shape_count(file_path) + fodg_text_item_count(file_path) * 3

def fodg_text_count_times_page_count_plus_shape_count(file_path: "str | bytes | Path") -> int:
    """Return (text_count * page_count) + shape_count."""
    return fodg_text_item_count(file_path) * fodg_page_count(file_path) + fodg_total_shape_count(file_path)

def fodg_page_count_plus_text_count(file_path: "str | bytes | Path") -> int:
    """Return page count plus text item count."""
    return fodg_page_count(file_path) + fodg_text_item_count(file_path)

def fodg_shape_count_plus_page_count_times_two(file_path: "str | bytes | Path") -> int:
    """Return shape_count + (page_count * 2)."""
    return fodg_total_shape_count(file_path) + fodg_page_count(file_path) * 2

def fodg_page_count_squared_plus_text_count(file_path):
    pc = fodg_page_count(file_path)
    return pc * pc + fodg_text_item_count(file_path)

def fodg_shape_count_times_two_plus_page_count(file_path):
    return fodg_total_shape_count(file_path) * 2 + fodg_page_count(file_path)

def fodg_text_count_times_three_plus_page_count(file_path):
    return fodg_text_item_count(file_path) * 3 + fodg_page_count(file_path)

def fodg_shape_count_times_page_count_plus_text_count(file_path):
    return fodg_total_shape_count(file_path) * fodg_page_count(file_path) + fodg_text_item_count(file_path)

def fodg_file_size_div_20(file_path: "str | bytes | Path") -> int:
    """Return file size in bytes divided by 20 (integer floor division)."""
    return fodg_file_size_bytes(file_path) // 20

def fodg_shape_count_squared_plus_page_count_times_10(file_path: "str | bytes | Path") -> int:
    """Return shape count squared plus page count multiplied by 10."""
    sc = fodg_total_shape_count(file_path)
    return sc * sc + fodg_page_count(file_path) * 10

def fodg_text_count_times_file_size_div_100(file_path: "str | bytes | Path") -> int:
    """Return text item count multiplied by file size divided by 100 (integer floor)."""
    return fodg_text_item_count(file_path) * fodg_file_size_bytes(file_path) // 100

def fodg_file_size_plus_text_count_times_10(file_path: "str | bytes | Path") -> int:
    """Return file size in bytes plus text item count multiplied by 10."""
    return fodg_file_size_bytes(file_path) + fodg_text_item_count(file_path) * 10

def fodg_file_size_minus_shape_count_times_50(file_path: "str | bytes | Path") -> int:
    """Return file size in bytes minus (shape count * 50). 0 if result negative."""
    return max(0, fodg_file_size_bytes(file_path) - fodg_total_shape_count(file_path) * 50)

def fodg_shape_count_times_text_count_plus_file_size_div_100(file_path: "str | bytes | Path") -> int:
    """Return (shape count * text item count) plus (file size // 100)."""
    return (fodg_total_shape_count(file_path) * fodg_text_item_count(file_path)
            + fodg_file_size_bytes(file_path) // 100)

def fodg_file_size_plus_shape_count_times_100(file_path: "str | bytes | Path") -> int:
    """Return file size in bytes plus (shape count * 100)."""
    return fodg_file_size_bytes(file_path) + fodg_total_shape_count(file_path) * 100

def fodg_file_size_div_10_plus_text_count(file_path: "str | bytes | Path") -> int:
    """Return (file size // 10) plus text item count."""
    return fodg_file_size_bytes(file_path) // 10 + fodg_text_item_count(file_path)

def fodg_file_size_div_shape_count_plus_1(file_path: "str | bytes | Path") -> int:
    """Return file size floor-divided by (shape_count + 1)."""
    return fodg_file_size_bytes(file_path) // (fodg_total_shape_count(file_path) + 1)

def fodg_file_size_plus_shape_count_times_text_count_times_10(file_path: "str | bytes | Path") -> int:
    """Return file size plus (shape_count * text_count * 10)."""
    return (fodg_file_size_bytes(file_path)
            + fodg_total_shape_count(file_path) * fodg_text_item_count(file_path) * 10)

def fodg_file_size_times_2_plus_shape_count_times_50(file_path: "str | bytes | Path") -> int:
    """Return (file_size * 2) plus (shape_count * 50)."""
    return fodg_file_size_bytes(file_path) * 2 + fodg_total_shape_count(file_path) * 50

def fodg_file_size_minus_text_count_times_100(file_path: "str | bytes | Path") -> int:
    """Return file size minus (text_count * 100), minimum 0."""
    return max(0, fodg_file_size_bytes(file_path) - fodg_text_item_count(file_path) * 100)

def fodg_file_size_plus_shape_count_plus_text_count_times_2(file_path: "str | bytes | Path") -> int:
    """Return (file_size + shape_count + text_count) * 2."""
    return (fodg_file_size_bytes(file_path)
            + fodg_total_shape_count(file_path)
            + fodg_text_item_count(file_path)) * 2

def fodg_file_size_div_5_plus_shape_count_times_text_count(file_path: "str | bytes | Path") -> int:
    """Return (file_size // 5) plus (shape_count * text_count)."""
    return fodg_file_size_bytes(file_path) // 5 + fodg_total_shape_count(file_path) * fodg_text_item_count(file_path)

def fodg_file_size_times_3_div_10_plus_text_count_times_shape_count(file_path: "str | bytes | Path") -> int:
    """Return (file_size * 3 // 10) plus (text_count * shape_count)."""
    return (fodg_file_size_bytes(file_path) * 3 // 10
            + fodg_text_item_count(file_path) * fodg_total_shape_count(file_path))

def fodg_file_size_plus_shape_count_times_200_plus_text_count(file_path: "str | bytes | Path") -> int:
    """Return file_size plus (shape_count * 200) plus text_count."""
    return (fodg_file_size_bytes(file_path)
            + fodg_total_shape_count(file_path) * 200
            + fodg_text_item_count(file_path))

def fodg_shape_count_plus_text_count(file_path: "str | bytes | Path") -> int:
    """Return total shape count plus text item count."""
    return fodg_total_shape_count(file_path) + fodg_text_item_count(file_path)

def fodg_file_size_div_10_times_shape_count_plus_text_count_times_50(file_path: "str | bytes | Path") -> int:
    """Return (file_size // 10 * shape_count) plus (text_count * 50)."""
    return (fodg_file_size_bytes(file_path) // 10 * fodg_total_shape_count(file_path)
            + fodg_text_item_count(file_path) * 50)

def fodg_shape_count_times_text_count_times_100_plus_file_size_div_10(file_path: "str | bytes | Path") -> int:
    """Return (shape_count * text_count * 100) plus (file_size // 10)."""
    return (fodg_total_shape_count(file_path) * fodg_text_item_count(file_path) * 100
            + fodg_file_size_bytes(file_path) // 10)

def fodg_file_size_plus_shape_count_plus_text_count_squared(file_path: "str | bytes | Path") -> int:
    """Return file_size plus (shape_count + text_count) squared."""
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return fodg_file_size_bytes(file_path) + (sc + tc) ** 2

def fodg_file_size_div_100_plus_shape_count_times_text_count_plus_1(file_path: "str | bytes | Path") -> int:
    """Return (file_size // 100) plus (shape_count * text_count) plus 1."""
    return (fodg_file_size_bytes(file_path) // 100
            + fodg_total_shape_count(file_path) * fodg_text_item_count(file_path)
            + 1)

def fodg_page_count_plus_shape_count(file_path: "str | bytes | Path") -> int:
    """Return page count plus total shape count."""
    return fodg_page_count(file_path) + fodg_total_shape_count(file_path)

def fodg_file_size_mod_500_plus_shape_count_plus_text_count(file_path: "str | bytes | Path") -> int:
    """Return (file_size % 500) + shape_count + text_count."""
    return (fodg_file_size_bytes(file_path) % 500
            + fodg_total_shape_count(file_path)
            + fodg_text_item_count(file_path))

def fodg_file_size_div_50_times_shape_count_plus_1(file_path: "str | bytes | Path") -> int:
    """Return (file_size // 50) * (shape_count + 1)."""
    return fodg_file_size_bytes(file_path) // 50 * (fodg_total_shape_count(file_path) + 1)

def fodg_file_size_div_20_plus_shape_count_times_50_plus_text_count(file_path: "str | bytes | Path") -> int:
    """Return (file_size // 20) + (shape_count * 50) + text_count."""
    return (fodg_file_size_bytes(file_path) // 20
            + fodg_total_shape_count(file_path) * 50
            + fodg_text_item_count(file_path))

def fodg_file_size_plus_text_count_times_shape_count_times_1000(file_path: "str | bytes | Path") -> int:
    """Return file_size + (text_count * shape_count * 1000)."""
    return (fodg_file_size_bytes(file_path)
            + fodg_text_item_count(file_path) * fodg_total_shape_count(file_path) * 1000)

def fodg_file_size_times_shape_count_plus_1_div_100(file_path: "str | bytes | Path") -> int:
    """Return (file_size * (shape_count + 1)) // 100."""
    return fodg_file_size_bytes(file_path) * (fodg_total_shape_count(file_path) + 1) // 100

def fodg_file_size_mod_200_plus_shape_count_times_100(file_path: "str | bytes | Path") -> int:
    """Return (file_size % 200) + (shape_count * 100)."""
    return fodg_file_size_bytes(file_path) % 200 + fodg_total_shape_count(file_path) * 100

def fodg_text_item_count_plus_page_count(file_path: "str | bytes | Path") -> int:
    """Return text item count plus page count."""
    return fodg_text_item_count(file_path) + fodg_page_count(file_path)

def fodg_file_size_div_10_plus_shape_count_squared_times_100_plus_text_count(file_path: "str | bytes | Path") -> int:
    """Return (file_size // 10) + (shape_count ** 2 * 100) + text_count."""
    return fodg_file_size_bytes(file_path) // 10 + fodg_total_shape_count(file_path) ** 2 * 100 + fodg_text_item_count(file_path)

def fodg_file_size_times_text_count_plus_1_div_50(file_path: "str | bytes | Path") -> int:
    """Return file_size * (text_count + 1) // 50."""
    return fodg_file_size_bytes(file_path) * (fodg_text_item_count(file_path) + 1) // 50

def fodg_file_size_mod_300_plus_shape_count_times_text_count_times_200(file_path: "str | bytes | Path") -> int:
    """Return (file_size % 300) + (shape_count * text_count * 200)."""
    return fodg_file_size_bytes(file_path) % 300 + fodg_total_shape_count(file_path) * fodg_text_item_count(file_path) * 200

def fodg_file_size_plus_shape_count_times_100_div_text_count_plus_1(file_path: "str | bytes | Path") -> int:
    """Return (file_size + shape_count * 100) // (text_count + 1)."""
    return (fodg_file_size_bytes(file_path) + fodg_total_shape_count(file_path) * 100) // (fodg_text_item_count(file_path) + 1)

def fodg_file_size_div_shape_count_plus_text_count_plus_1(file_path: "str | bytes | Path") -> int:
    """Return file_size // (shape_count + text_count + 1)."""
    return fodg_file_size_bytes(file_path) // (fodg_total_shape_count(file_path) + fodg_text_item_count(file_path) + 1)

def fodg_file_size_times_3_plus_shape_count_times_500_minus_text_count_times_200(file_path: "str | bytes | Path") -> int:
    """Return file_size * 3 + shape_count * 500 - text_count * 200."""
    return fodg_file_size_bytes(file_path) * 3 + fodg_total_shape_count(file_path) * 500 - fodg_text_item_count(file_path) * 200

def fodg_file_size_mod_100_plus_shape_count_times_300_plus_text_count_times_150(file_path: "str | bytes | Path") -> int:
    """Return (file_size % 100) + shape_count * 300 + text_count * 150."""
    return fodg_file_size_bytes(file_path) % 100 + fodg_total_shape_count(file_path) * 300 + fodg_text_item_count(file_path) * 150

def fodg_file_size_plus_shape_count_times_text_count_div_100(file_path: "str | bytes | Path") -> int:
    """Return (file_size + shape_count * text_count) // 100."""
    return (fodg_file_size_bytes(file_path) + fodg_total_shape_count(file_path) * fodg_text_item_count(file_path)) // 100

def fodg_file_size_mod_7_plus_shape_count_times_400_plus_text_count_times_250(file_path: "str | bytes | Path") -> int:
    """Return (file_size % 7) + shape_count * 400 + text_count * 250."""
    return fodg_file_size_bytes(file_path) % 7 + fodg_total_shape_count(file_path) * 400 + fodg_text_item_count(file_path) * 250

def fodg_file_size_div_100_times_shape_count_plus_1_plus_text_count_times_50(file_path: "str | bytes | Path") -> int:
    """Return (file_size // 100) * (shape_count + 1) + text_count * 50."""
    return fodg_file_size_bytes(file_path) // 100 * (fodg_total_shape_count(file_path) + 1) + fodg_text_item_count(file_path) * 50

def fodg_file_size_mod_11_plus_shape_count_times_500_plus_text_count_times_350(file_path: "str | bytes | Path") -> int:
    """Return (file_size % 11) + shape_count * 500 + text_count * 350."""
    return fodg_file_size_bytes(file_path) % 11 + fodg_total_shape_count(file_path) * 500 + fodg_text_item_count(file_path) * 350

def fodg_file_size_times_2_mod_500_plus_shape_count_times_200_plus_text_count_times_150(file_path: "str | bytes | Path") -> int:
    """Return (file_size * 2 % 500) + shape_count * 200 + text_count * 150."""
    return fodg_file_size_bytes(file_path) * 2 % 500 + fodg_total_shape_count(file_path) * 200 + fodg_text_item_count(file_path) * 150

def fodg_file_size_plus_shape_count_times_600_plus_text_count_times_400_div_10(file_path: "str | bytes | Path") -> int:
    """Return (file_size + shape_count * 600 + text_count * 400) // 10."""
    return (fodg_file_size_bytes(file_path) + fodg_total_shape_count(file_path) * 600 + fodg_text_item_count(file_path) * 400) // 10

def fodg_file_size_mod_17_plus_shape_count_times_700_plus_text_count_times_500(file_path: "str | bytes | Path") -> int:
    """Return (file_size % 17) + shape_count * 700 + text_count * 500."""
    return fodg_file_size_bytes(file_path) % 17 + fodg_total_shape_count(file_path) * 700 + fodg_text_item_count(file_path) * 500

def fodg_shape_plus_page_squared(file_path: "str | bytes | Path") -> int:
    """Return the square of (shape_count + page_count)."""
    s = fodg_total_shape_count(file_path) + fodg_page_count(file_path)
    return s * s

def fodg_file_size_mod_23_plus_shape_count_times_800_plus_text_count_times_600(file_path: "str | bytes | Path") -> int:
    """Return (file_size % 23) + shape_count * 800 + text_count * 600."""
    return fodg_file_size_bytes(file_path) % 23 + fodg_total_shape_count(file_path) * 800 + fodg_text_item_count(file_path) * 600

def fodg_file_size_times_3_mod_1000_plus_shape_count_times_100_plus_text_count_times_80(file_path: "str | bytes | Path") -> int:
    """Return (file_size * 3 % 1000) + shape_count * 100 + text_count * 80."""
    return fodg_file_size_bytes(file_path) * 3 % 1000 + fodg_total_shape_count(file_path) * 100 + fodg_text_item_count(file_path) * 80

def fodg_file_size_mod_11_times_3_plus_shape_count_times_900_plus_text_count_times_700(file_path: "str | bytes | Path") -> int:
    """Return (file_size % 11) * 3 + shape_count * 900 + text_count * 700."""
    return fodg_file_size_bytes(file_path) % 11 * 3 + fodg_total_shape_count(file_path) * 900 + fodg_text_item_count(file_path) * 700

def fodg_file_size_mod_7_times_50_plus_shape_count_times_800_plus_text_count_times_500(file_path: "str | bytes | Path") -> int:
    """Return (file_size % 7) * 50 + shape_count * 800 + text_count * 500."""
    return fodg_file_size_bytes(file_path) % 7 * 50 + fodg_total_shape_count(file_path) * 800 + fodg_text_item_count(file_path) * 500

def fodg_file_size_mod_19_times_4_plus_shape_count_times_1000_plus_text_count_times_600(file_path: "str | bytes | Path") -> int:
    """Return (file_size % 19) * 4 + shape_count * 1000 + text_count * 600."""
    return fodg_file_size_bytes(file_path) % 19 * 4 + fodg_total_shape_count(file_path) * 1000 + fodg_text_item_count(file_path) * 600

def fodg_file_size_mod_23_times_3_plus_shape_count_times_700_plus_text_count_times_300(file_path: "str | bytes | Path") -> int:
    """Return (file_size % 23) * 3 + shape_count * 700 + text_count * 300."""
    return fodg_file_size_bytes(file_path) % 23 * 3 + fodg_total_shape_count(file_path) * 700 + fodg_text_item_count(file_path) * 300

def fodg_file_size_mod_29_times_2_plus_shape_count_times_1100_plus_text_count_times_800(file_path: "str | bytes | Path") -> int:
    """Return (file_size % 29) * 2 + shape_count * 1100 + text_count * 800."""
    return fodg_file_size_bytes(file_path) % 29 * 2 + fodg_total_shape_count(file_path) * 1100 + fodg_text_item_count(file_path) * 800

def fodg_file_size_mod_17_times_5_plus_shape_count_times_850_plus_text_count_times_450(file_path: "str | bytes | Path") -> int:
    """Return (file_size % 17) * 5 + shape_count * 850 + text_count * 450."""
    return fodg_file_size_bytes(file_path) % 17 * 5 + fodg_total_shape_count(file_path) * 850 + fodg_text_item_count(file_path) * 450

def fodg_file_size_mod_31_times_3_plus_shape_count_times_1200_plus_text_count_times_900(file_path: "str | bytes | Path") -> int:
    """Return (file_size % 31) * 3 + shape_count * 1200 + text_count * 900."""
    return fodg_file_size_bytes(file_path) % 31 * 3 + fodg_total_shape_count(file_path) * 1200 + fodg_text_item_count(file_path) * 900

def fodg_file_size_mod_37_plus_shape_count_times_900_plus_text_count_times_600(file_path: "str | bytes | Path") -> int:
    """Return (file_size % 37) + shape_count * 900 + text_count * 600."""
    return fodg_file_size_bytes(file_path) % 37 + fodg_total_shape_count(file_path) * 900 + fodg_text_item_count(file_path) * 600

def fodg_file_size_mod_43_times_2_plus_shape_count_times_1400_plus_text_count_times_700(file_path: "str | bytes | Path") -> int:
    """Return (file_size % 43) * 2 + shape_count * 1400 + text_count * 700."""
    return fodg_file_size_bytes(file_path) % 43 * 2 + fodg_total_shape_count(file_path) * 1400 + fodg_text_item_count(file_path) * 700

def fodg_file_size_mod_47_plus_shape_count_times_800_plus_text_count_times_500(file_path: "str | bytes | Path") -> int:
    """Return (file_size % 47) + shape_count * 800 + text_count * 500."""
    return fodg_file_size_bytes(file_path) % 47 + fodg_total_shape_count(file_path) * 800 + fodg_text_item_count(file_path) * 500

def fodg_file_size_mod_29_times_5_plus_shape_count_times_1100_plus_text_count_times_800(file_path: "str | Path") -> int:
    """Composite: (file_size % 29) * 5 + shape_count * 1100 + text_count * 800."""
    return (fodg_file_size_bytes(file_path) % 29) * 5 + fodg_total_shape_count(file_path) * 1100 + fodg_text_item_count(file_path) * 800

def fodg_file_size_mod_31_times_4_plus_shape_count_times_900_plus_text_count_times_400(file_path: "str | Path") -> int:
    """Composite: (file_size % 31) * 4 + shape_count * 900 + text_count * 400."""
    return (fodg_file_size_bytes(file_path) % 31) * 4 + fodg_total_shape_count(file_path) * 900 + fodg_text_item_count(file_path) * 400

def fodg_page_count_times_shape_count_times_1000_plus_text_count_times_500_plus_file_size_mod_37(file_path: "str | Path") -> int:
    """Composite: page_count * shape_count * 1000 + text_count * 500 + file_size % 37."""
    return fodg_page_count(file_path) * fodg_total_shape_count(file_path) * 1000 + fodg_text_item_count(file_path) * 500 + fodg_file_size_bytes(file_path) % 37

def fodg_shape_count_squared_plus_text_count_squared_plus_page_count_times_100(file_path: "str | Path") -> int:
    """Composite: shape_count^2 + text_count^2 + page_count * 100."""
    return fodg_total_shape_count(file_path) ** 2 + fodg_text_item_count(file_path) ** 2 + fodg_page_count(file_path) * 100

def fodg_total_shape_count_times_300_plus_text_item_count_times_200_plus_file_size_mod_31_times_10(file_path: "str | Path") -> int:
    """Return total_shape_count * 300 + text_item_count * 200 + (file_size % 31) * 10."""
    return fodg_total_shape_count(file_path) * 300 + fodg_text_item_count(file_path) * 200 + (fodg_file_size_bytes(file_path) % 31) * 10

def fodg_page_count_times_500_plus_total_shape_count_times_100_plus_file_size_mod_37(file_path: "str | Path") -> int:
    """Return page_count * 500 + total_shape_count * 100 + file_size % 37."""
    return fodg_page_count(file_path) * 500 + fodg_total_shape_count(file_path) * 100 + fodg_file_size_bytes(file_path) % 37

def fodg_page_times_600_plus_shape_times_400_plus_file_size_mod_29_times_50(file_path: "str | Path") -> int:
    return fodg_page_count(file_path) * 600 + fodg_total_shape_count(file_path) * 400 + (fodg_file_size_bytes(file_path) % 29) * 50

def fodg_shape_times_text_times_500_plus_page_times_700_plus_file_size_mod_41(file_path: "str | Path") -> int:
    return fodg_total_shape_count(file_path) * fodg_text_item_count(file_path) * 500 + fodg_page_count(file_path) * 700 + fodg_file_size_bytes(file_path) % 41

def fodg_file_size_mod_43_times_5_plus_shape_times_1100_plus_text_times_800_plus_page_times_300(file_path: "str | Path") -> int:
    """Compound: (file_size % 43) * 5 + shapes * 1100 + text * 800 + pages * 300."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 43) * 5 + sc * 1100 + tc * 800 + pc * 300

def fodg_file_size_times_3_plus_shape_times_900_plus_text_times_600_plus_page_times_200(file_path: "str | Path") -> int:
    """Compound: file_size * 3 + shapes * 900 + text * 600 + pages * 200."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 3 + sc * 900 + tc * 600 + pc * 200

def fodg_file_size_mod_53_times_7_plus_shape_times_1200_plus_text_times_900_plus_page_times_400(file_path: "str | Path") -> int:
    """Compound: (file_size % 53) * 7 + shapes * 1200 + text * 900 + pages * 400."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 53) * 7 + sc * 1200 + tc * 900 + pc * 400

def fodg_file_size_times_4_plus_shape_times_800_plus_text_times_500_plus_page_times_100(file_path: "str | Path") -> int:
    """Compound: file_size * 4 + shapes * 800 + text * 500 + pages * 100."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 4 + sc * 800 + tc * 500 + pc * 100

def fodg_file_size_mod_59_times_6_plus_shape_times_1300_plus_text_times_1000_plus_page_times_500(file_path: "str | Path") -> int:
    """Compound: (file_size % 59) * 6 + shapes * 1300 + text * 1000 + pages * 500."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 59) * 6 + sc * 1300 + tc * 1000 + pc * 500

def fodg_file_size_times_5_plus_shape_times_700_plus_text_times_400_plus_page_times_200(file_path: "str | Path") -> int:
    """Compound: file_size * 5 + shapes * 700 + text * 400 + pages * 200."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 5 + sc * 700 + tc * 400 + pc * 200

def fodg_file_size_mod_11_times_200_plus_shape_count_times_900_plus_text_count_times_400(file_path: "str | Path") -> int:
    """Return (file_size % 11) * 200 + shape_count * 900 + text_count * 400."""
    return fodg_file_size_bytes(file_path) % 11 * 200 + fodg_total_shape_count(file_path) * 900 + fodg_text_item_count(file_path) * 400

def fodg_file_size_mod_7_times_100_plus_shape_count_times_600_plus_text_count_times_500(file_path: "str | Path") -> int:
    """Return (file_size % 7) * 100 + shape_count * 600 + text_count * 500."""
    return fodg_file_size_bytes(file_path) % 7 * 100 + fodg_total_shape_count(file_path) * 600 + fodg_text_item_count(file_path) * 500

def fodg_file_size_mod_29_times_500_plus_shape_count_times_1100_plus_text_count_times_800(file_path: "str | Path") -> int:
    """Return (file_size % 29) * 500 + shape_count * 1100 + text_count * 800."""
    return fodg_file_size_bytes(file_path) % 29 * 500 + fodg_total_shape_count(file_path) * 1100 + fodg_text_item_count(file_path) * 800

def fodg_file_size_mod_19_times_400_plus_shape_count_times_900_plus_text_count_times_700(file_path: "str | Path") -> int:
    """Return (file_size % 19) * 400 + shape_count * 900 + text_count * 700."""
    return fodg_file_size_bytes(file_path) % 19 * 400 + fodg_total_shape_count(file_path) * 900 + fodg_text_item_count(file_path) * 700

def fodg_file_size_mod_37_times_600_plus_shape_count_times_1200_plus_text_count_times_900(file_path: "str | Path") -> int:
    """Return (file_size % 37) * 600 + shape_count * 1200 + text_count * 900."""
    return fodg_file_size_bytes(file_path) % 37 * 600 + fodg_total_shape_count(file_path) * 1200 + fodg_text_item_count(file_path) * 900

def fodg_file_size_mod_43_times_800_plus_shape_count_times_850_plus_text_count_times_650(file_path: "str | Path") -> int:
    """Return (file_size % 43) * 800 + shape_count * 850 + text_count * 650."""
    return fodg_file_size_bytes(file_path) % 43 * 800 + fodg_total_shape_count(file_path) * 850 + fodg_text_item_count(file_path) * 650

def fodg_file_size_mod_61_times_8_plus_shape_times_1500_plus_text_times_1100_plus_page_times_600(file_path: "str | Path") -> int:
    """Compound: (file_size % 61) * 8 + shapes * 1500 + text * 1100 + pages * 600."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 61) * 8 + sc * 1500 + tc * 1100 + pc * 600

def fodg_file_size_times_7_plus_shape_times_600_plus_text_times_300_plus_page_times_250(file_path: "str | Path") -> int:
    """Compound: file_size * 7 + shapes * 600 + text * 300 + pages * 250."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 7 + sc * 600 + tc * 300 + pc * 250

def fodg_file_size_mod_7_times_300_plus_shape_count_times_800_plus_text_count_times_400(file_path: "str | Path") -> int:
    """Return (file_size % 7) * 300 + shape_count * 800 + text_count * 400."""
    return fodg_file_size_bytes(file_path) % 7 * 300 + fodg_total_shape_count(file_path) * 800 + fodg_text_item_count(file_path) * 400

def fodg_file_size_mod_17_times_50_plus_shape_count_times_500_plus_text_count_times_250(file_path: "str | Path") -> int:
    """Return (file_size % 17) * 50 + shape_count * 500 + text_count * 250."""
    return fodg_file_size_bytes(file_path) % 17 * 50 + fodg_total_shape_count(file_path) * 500 + fodg_text_item_count(file_path) * 250

def fodg_file_size_mod_29_times_5_plus_shape_times_1600_plus_text_times_1200_plus_page_times_700(file_path):
    """Return (file_size % 29) * 5 + shape * 1600 + text * 1200 + page * 700."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 29) * 5 + sc * 1600 + tc * 1200 + pc * 700

def fodg_file_size_times_8_plus_shape_times_500_plus_text_times_250_plus_page_times_150(file_path):
    """Return file_size * 8 + shape * 500 + text * 250 + page * 150."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 8 + sc * 500 + tc * 250 + pc * 150

def fodg_file_size_mod_23_times_100_plus_shape_count_times_700_plus_text_count_times_350(file_path: "str | Path") -> int:
    """Return (file_size % 23) * 100 + shape_count * 700 + text_count * 350."""
    return fodg_file_size_bytes(file_path) % 23 * 100 + fodg_total_shape_count(file_path) * 700 + fodg_text_item_count(file_path) * 350

def fodg_file_size_mod_11_times_250_plus_shape_count_times_400_plus_text_count_times_600(file_path: "str | Path") -> int:
    """Return (file_size % 11) * 250 + shape_count * 400 + text_count * 600."""
    return fodg_file_size_bytes(file_path) % 11 * 250 + fodg_total_shape_count(file_path) * 400 + fodg_text_item_count(file_path) * 600

def fodg_file_size_mod_19_times_150_plus_shape_count_times_600_plus_text_count_times_300(file_path: "str | Path") -> int:
    """Return (file_size % 19) * 150 + shape_count * 600 + text_count * 300."""
    return fodg_file_size_bytes(file_path) % 19 * 150 + fodg_total_shape_count(file_path) * 600 + fodg_text_item_count(file_path) * 300

def fodg_file_size_mod_29_times_100_plus_shape_count_times_600_plus_text_count_times_450(file_path: "str | Path") -> int:
    """Return (file_size % 29) * 100 + shape_count * 600 + text_count * 450."""
    return fodg_file_size_bytes(file_path) % 29 * 100 + fodg_total_shape_count(file_path) * 600 + fodg_text_item_count(file_path) * 450

def fodg_file_size_mod_37_times_7_plus_shape_times_1700_plus_text_times_1300_plus_page_times_800(file_path):
    """Return (file_size % 37) * 7 + shape * 1700 + text * 1300 + page * 800."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 37) * 7 + sc * 1700 + tc * 1300 + pc * 800

def fodg_file_size_times_9_plus_shape_times_400_plus_text_times_200_plus_page_times_100(file_path):
    """Return file_size * 9 + shape * 400 + text * 200 + page * 100."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 9 + sc * 400 + tc * 200 + pc * 100

def fodg_file_size_mod_31_times_100_plus_shape_count_times_750_plus_text_count_times_350(file_path: "str | Path") -> int:
    """Return (file_size % 31) * 100 + shape_count * 750 + text_count * 350."""
    return fodg_file_size_bytes(file_path) % 31 * 100 + fodg_total_shape_count(file_path) * 750 + fodg_text_item_count(file_path) * 350

def fodg_file_size_mod_23_times_200_plus_shape_count_times_450_plus_text_count_times_550(file_path: "str | Path") -> int:
    """Return (file_size % 23) * 200 + shape_count * 450 + text_count * 550."""
    return fodg_file_size_bytes(file_path) % 23 * 200 + fodg_total_shape_count(file_path) * 450 + fodg_text_item_count(file_path) * 550

def fodg_file_size_mod_31_times_150_plus_shape_count_times_800_plus_text_count_times_400(file_path: "str | Path") -> int:
    """Return (file_size % 31) * 150 + shape_count * 800 + text_count * 400."""
    return fodg_file_size_bytes(file_path) % 31 * 150 + fodg_total_shape_count(file_path) * 800 + fodg_text_item_count(file_path) * 400

def fodg_file_size_mod_17_times_250_plus_shape_count_times_500_plus_text_count_times_350(file_path: "str | Path") -> int:
    """Return (file_size % 17) * 250 + shape_count * 500 + text_count * 350."""
    return fodg_file_size_bytes(file_path) % 17 * 250 + fodg_total_shape_count(file_path) * 500 + fodg_text_item_count(file_path) * 350

def fodg_file_size_mod_41_times_9_plus_shape_times_1800_plus_text_times_1400_plus_page_times_900(file_path):
    """Return (file_size % 41) * 9 + shape * 1800 + text * 1400 + page * 900."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 41) * 9 + sc * 1800 + tc * 1400 + pc * 900

def fodg_file_size_times_10_plus_shape_times_300_plus_text_times_150_plus_page_times_75(file_path):
    """Return file_size * 10 + shape * 300 + text * 150 + page * 75."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 10 + sc * 300 + tc * 150 + pc * 75

def fodg_file_size_mod_43_times_100_plus_shape_count_times_900_plus_text_count_times_500(file_path: "str | Path") -> int:
    """Return (file_size % 43) * 100 + shape_count * 900 + text_count * 500."""
    return fodg_file_size_bytes(file_path) % 43 * 100 + fodg_total_shape_count(file_path) * 900 + fodg_text_item_count(file_path) * 500

def fodg_file_size_mod_29_times_150_plus_shape_count_times_600_plus_text_count_times_250(file_path: "str | Path") -> int:
    """Return (file_size % 29) * 150 + shape_count * 600 + text_count * 250."""
    return fodg_file_size_bytes(file_path) % 29 * 150 + fodg_total_shape_count(file_path) * 600 + fodg_text_item_count(file_path) * 250

def fodg_file_size_mod_37_times_200_plus_shape_count_times_700_plus_text_count_times_300(file_path: "str | Path") -> int:
    """Return (file_size % 37) * 200 + shape_count * 700 + text_count * 300."""
    return fodg_file_size_bytes(file_path) % 37 * 200 + fodg_total_shape_count(file_path) * 700 + fodg_text_item_count(file_path) * 300

def fodg_file_size_mod_53_times_100_plus_shape_count_times_1000_plus_text_count_times_600(file_path: "str | Path") -> int:
    """Return (file_size % 53) * 100 + shape_count * 1000 + text_count * 600."""
    return fodg_file_size_bytes(file_path) % 53 * 100 + fodg_total_shape_count(file_path) * 1000 + fodg_text_item_count(file_path) * 600

def fodg_file_size_mod_43_times_11_plus_shape_times_2000_plus_text_times_1600_plus_page_times_1000(file_path):
    """Return (file_size % 43) * 11 + shape * 2000 + text * 1600 + page * 1000."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 43) * 11 + sc * 2000 + tc * 1600 + pc * 1000

def fodg_file_size_times_11_plus_shape_times_200_plus_text_times_100_plus_page_times_50(file_path):
    """Return file_size * 11 + shape * 200 + text * 100 + page * 50."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 11 + sc * 200 + tc * 100 + pc * 50

def fodg_file_size_mod_47_times_150_plus_shape_count_times_850_plus_text_count_times_450(file_path: "str | Path") -> int:
    """Return (file_size % 47) * 150 + shape_count * 850 + text_count * 450."""
    return fodg_file_size_bytes(file_path) % 47 * 150 + fodg_total_shape_count(file_path) * 850 + fodg_text_item_count(file_path) * 450

def fodg_file_size_mod_59_times_200_plus_shape_count_times_950_plus_text_count_times_550(file_path: "str | Path") -> int:
    """Return (file_size % 59) * 200 + shape_count * 950 + text_count * 550."""
    return fodg_file_size_bytes(file_path) % 59 * 200 + fodg_total_shape_count(file_path) * 950 + fodg_text_item_count(file_path) * 550

def fodg_file_size_mod_61_times_250_plus_shape_count_times_1050_plus_text_count_times_650(file_path: "str | Path") -> int:
    """Return (file_size % 61) * 250 + shape_count * 1050 + text_count * 650."""
    return fodg_file_size_bytes(file_path) % 61 * 250 + fodg_total_shape_count(file_path) * 1050 + fodg_text_item_count(file_path) * 650

def fodg_file_size_mod_71_times_100_plus_shape_count_times_750_plus_text_count_times_350(file_path: "str | Path") -> int:
    """Return (file_size % 71) * 100 + shape_count * 750 + text_count * 350."""
    return fodg_file_size_bytes(file_path) % 71 * 100 + fodg_total_shape_count(file_path) * 750 + fodg_text_item_count(file_path) * 350

def fodg_file_size_mod_83_times_350_plus_shape_count_times_1150_plus_text_count_times_750(file_path: "str | Path") -> int:
    """Return (file_size % 83) * 350 + shape_count * 1150 + text_count * 750."""
    return fodg_file_size_bytes(file_path) % 83 * 350 + fodg_total_shape_count(file_path) * 1150 + fodg_text_item_count(file_path) * 750

def fodg_file_size_mod_89_times_150_plus_shape_count_times_850_plus_text_count_times_450(file_path: "str | Path") -> int:
    """Return (file_size % 89) * 150 + shape_count * 850 + text_count * 450."""
    return fodg_file_size_bytes(file_path) % 89 * 150 + fodg_total_shape_count(file_path) * 850 + fodg_text_item_count(file_path) * 450

def fodg_file_size_mod_97_times_200_plus_shape_count_times_950_plus_text_count_times_550(file_path: "str | Path") -> int:
    """Return (file_size % 97) * 200 + shape_count * 950 + text_count * 550."""
    return fodg_file_size_bytes(file_path) % 97 * 200 + fodg_total_shape_count(file_path) * 950 + fodg_text_item_count(file_path) * 550

def fodg_file_size_mod_101_times_300_plus_shape_count_times_650_plus_text_count_times_250(file_path: "str | Path") -> int:
    """Return (file_size % 101) * 300 + shape_count * 650 + text_count * 250."""
    return fodg_file_size_bytes(file_path) % 101 * 300 + fodg_total_shape_count(file_path) * 650 + fodg_text_item_count(file_path) * 250

def fodg_file_size_mod_103_times_400_plus_shape_count_times_1100_plus_text_count_times_700(file_path: "str | Path") -> int:
    """Return (file_size % 103) * 400 + shape_count * 1100 + text_count * 700."""
    return fodg_file_size_bytes(file_path) % 103 * 400 + fodg_total_shape_count(file_path) * 1100 + fodg_text_item_count(file_path) * 700

def fodg_file_size_mod_107_times_250_plus_shape_count_times_900_plus_text_count_times_500(file_path: "str | Path") -> int:
    """Return (file_size % 107) * 250 + shape_count * 900 + text_count * 500."""
    return fodg_file_size_bytes(file_path) % 107 * 250 + fodg_total_shape_count(file_path) * 900 + fodg_text_item_count(file_path) * 500

def fodg_file_size_mod_47_times_13_plus_shape_times_2200_plus_text_times_1800_plus_page_times_1100(file_path: "str | Path") -> int:
    """Return (file_size % 47) * 13 + shape_count * 2200 + text_count * 1800 + page_count * 1100."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 47) * 13 + sc * 2200 + tc * 1800 + pc * 1100

def fodg_file_size_times_12_plus_shape_times_100_plus_text_times_50_plus_page_times_25(file_path: "str | Path") -> int:
    """Return file_size * 12 + shape_count * 100 + text_count * 50 + page_count * 25."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 12 + sc * 100 + tc * 50 + pc * 25

def fodg_file_size_mod_109_times_450_plus_shape_count_times_1200_plus_text_count_times_800(file_path: "str | Path") -> int:
    """Return (file_size % 109) * 450 + shape_count * 1200 + text_count * 800."""
    return fodg_file_size_bytes(file_path) % 109 * 450 + fodg_total_shape_count(file_path) * 1200 + fodg_text_item_count(file_path) * 800

def fodg_file_size_mod_113_times_350_plus_shape_count_times_1000_plus_text_count_times_600(file_path: "str | Path") -> int:
    """Return (file_size % 113) * 350 + shape_count * 1000 + text_count * 600."""
    return fodg_file_size_bytes(file_path) % 113 * 350 + fodg_total_shape_count(file_path) * 1000 + fodg_text_item_count(file_path) * 600

def fodg_file_size_mod_127_times_400_plus_shape_count_times_1400_plus_text_count_times_900(file_path: "str | Path") -> int:
    """Return (file_size % 127) * 400 + shape_count * 1400 + text_count * 900."""
    return fodg_file_size_bytes(file_path) % 127 * 400 + fodg_total_shape_count(file_path) * 1400 + fodg_text_item_count(file_path) * 900

def fodg_file_size_mod_131_times_500_plus_shape_count_times_1100_plus_text_count_times_700(file_path: "str | Path") -> int:
    """Return (file_size % 131) * 500 + shape_count * 1100 + text_count * 700."""
    return fodg_file_size_bytes(file_path) % 131 * 500 + fodg_total_shape_count(file_path) * 1100 + fodg_text_item_count(file_path) * 700

def fodg_file_size_mod_53_times_15_plus_shape_times_2400_plus_text_times_2000_plus_page_times_1200(file_path: "str | Path") -> int:
    """Return (file_size % 53) * 15 + shape_count * 2400 + text_count * 2000 + page_count * 1200."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 53) * 15 + sc * 2400 + tc * 2000 + pc * 1200

def fodg_file_size_times_13_plus_shape_times_50_plus_text_times_30_plus_page_times_15(file_path: "str | Path") -> int:
    """Return file_size * 13 + shape_count * 50 + text_count * 30 + page_count * 15."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 13 + sc * 50 + tc * 30 + pc * 15

def fodg_file_size_mod_137_times_450_plus_shape_count_times_1500_plus_text_count_times_1000(file_path: "str | Path") -> int:
    """Return (file_size % 137) * 450 + shape_count * 1500 + text_count * 1000."""
    return fodg_file_size_bytes(file_path) % 137 * 450 + fodg_total_shape_count(file_path) * 1500 + fodg_text_item_count(file_path) * 1000

def fodg_file_size_mod_139_times_550_plus_shape_count_times_1200_plus_text_count_times_800(file_path: "str | Path") -> int:
    """Return (file_size % 139) * 550 + shape_count * 1200 + text_count * 800."""
    return fodg_file_size_bytes(file_path) % 139 * 550 + fodg_total_shape_count(file_path) * 1200 + fodg_text_item_count(file_path) * 800

def fodg_file_size_mod_149_times_500_plus_shape_count_times_1600_plus_text_count_times_1100(file_path: "str | Path") -> int:
    """Return (file_size % 149) * 500 + shape_count * 1600 + text_count * 1100."""
    return fodg_file_size_bytes(file_path) % 149 * 500 + fodg_total_shape_count(file_path) * 1600 + fodg_text_item_count(file_path) * 1100

def fodg_file_size_mod_151_times_600_plus_shape_count_times_1300_plus_text_count_times_900(file_path: "str | Path") -> int:
    """Return (file_size % 151) * 600 + shape_count * 1300 + text_count * 900."""
    return fodg_file_size_bytes(file_path) % 151 * 600 + fodg_total_shape_count(file_path) * 1300 + fodg_text_item_count(file_path) * 900

def fodg_file_size_mod_157_times_650_plus_shape_count_times_1700_plus_text_count_times_1200(file_path: "str | Path") -> int:
    """Return (file_size % 157) * 650 + shape_count * 1700 + text_count * 1200."""
    return fodg_file_size_bytes(file_path) % 157 * 650 + fodg_total_shape_count(file_path) * 1700 + fodg_text_item_count(file_path) * 1200

def fodg_file_size_mod_163_times_700_plus_shape_count_times_1400_plus_text_count_times_1000(file_path: "str | Path") -> int:
    """Return (file_size % 163) * 700 + shape_count * 1400 + text_count * 1000."""
    return fodg_file_size_bytes(file_path) % 163 * 700 + fodg_total_shape_count(file_path) * 1400 + fodg_text_item_count(file_path) * 1000

def fodg_file_size_mod_59_times_17_plus_shape_times_2600_plus_text_times_2200_plus_page_times_1300(file_path: "str | Path") -> int:
    """Return (file_size % 59) * 17 + shape_count * 2600 + text_count * 2200 + page_count * 1300."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 59) * 17 + sc * 2600 + tc * 2200 + pc * 1300

def fodg_file_size_times_14_plus_shape_times_30_plus_text_times_20_plus_page_times_10(file_path: "str | Path") -> int:
    """Return file_size * 14 + shape_count * 30 + text_count * 20 + page_count * 10."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 14 + sc * 30 + tc * 20 + pc * 10

def fodg_file_size_mod_61_times_20_plus_shape_count_times_1800_plus_text_count_times_1300(file_path: "str | Path") -> int:
    """Return (file_size % 61) * 20 + shape_count * 1800 + text_count * 1300.

    Spec fact: FACT-FODG-EX-0001 (ODF drawing document root element structure).
    """
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 61) * 20 + sc * 1800 + tc * 1300

def fodg_file_size_times_17_plus_shape_count_times_40_plus_text_count_times_25_plus_page_count_times_12(file_path: "str | Path") -> int:
    """Return file_size * 17 + shape_count * 40 + text_count * 25 + page_count * 12.

    Spec fact: FACT-FODG-EX-0002 (ODF drawing page elements and shape containment).
    """
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 17 + sc * 40 + tc * 25 + pc * 12

def fodg_file_size_mod_167_times_750_plus_shape_count_times_1800_plus_text_count_times_1300(file_path: "str | Path") -> int:
    """Return (file_size % 167) * 750 + shape_count * 1800 + text_count * 1300."""
    return fodg_file_size_bytes(file_path) % 167 * 750 + fodg_total_shape_count(file_path) * 1800 + fodg_text_item_count(file_path) * 1300

def fodg_file_size_mod_173_times_800_plus_shape_count_times_1500_plus_text_count_times_1100(file_path: "str | Path") -> int:
    """Return (file_size % 173) * 800 + shape_count * 1500 + text_count * 1100."""
    return fodg_file_size_bytes(file_path) % 173 * 800 + fodg_total_shape_count(file_path) * 1500 + fodg_text_item_count(file_path) * 1100

def fodg_file_size_mod_167_times_5_plus_shape_count_times_2700_plus_text_count_times_2400(file_path: "str | Path") -> int:
    """Return (file_size % 167) * 5 + shape_count * 2700 + text_count * 2400."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_shape_count(file_path)
    return (fs % 167) * 5 + sc * 2700 + tc * 2400

def fodg_file_size_times_15_plus_shape_count_times_35_plus_text_count_times_22_plus_page_count_times_11(file_path: "str | Path") -> int:
    """Return file_size * 15 + shape_count * 35 + text_count * 22 + page_count * 11."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_shape_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 15 + sc * 35 + tc * 22 + pc * 11

def fodg_file_size_mod_179_times_850_plus_shape_count_times_1900_plus_text_count_times_1400(file_path: "str | Path") -> int:
    """Return (file_size % 179) * 850 + shape_count * 1900 + text_count * 1400."""
    return fodg_file_size_bytes(file_path) % 179 * 850 + fodg_total_shape_count(file_path) * 1900 + fodg_text_item_count(file_path) * 1400

def fodg_file_size_mod_181_times_900_plus_shape_count_times_1600_plus_text_count_times_1200(file_path: "str | Path") -> int:
    """Return (file_size % 181) * 900 + shape_count * 1600 + text_count * 1200."""
    return fodg_file_size_bytes(file_path) % 181 * 900 + fodg_total_shape_count(file_path) * 1600 + fodg_text_item_count(file_path) * 1200

def fodg_file_size_mod_61_times_19_plus_shape_times_2800_plus_text_times_2400_plus_page_times_1400(file_path: "str | Path") -> int:
    """Return (file_size % 61) * 19 + shape_count * 2800 + text_count * 2400 + page_count * 1400."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 61) * 19 + sc * 2800 + tc * 2400 + pc * 1400

def fodg_file_size_times_15_plus_shape_times_20_plus_text_times_15_plus_page_times_8(file_path: "str | Path") -> int:
    """Return file_size * 15 + shape_count * 20 + text_count * 15 + page_count * 8."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 15 + sc * 20 + tc * 15 + pc * 8

def fodg_file_size_mod_191_times_950_plus_shape_count_times_2000_plus_text_count_times_1500(file_path: "str | Path") -> int:
    """Return (file_size % 191) * 950 + shape_count * 2000 + text_count * 1500."""
    return fodg_file_size_bytes(file_path) % 191 * 950 + fodg_total_shape_count(file_path) * 2000 + fodg_text_item_count(file_path) * 1500

def fodg_file_size_mod_193_times_1000_plus_shape_count_times_1700_plus_text_count_times_1300(file_path: "str | Path") -> int:
    """Return (file_size % 193) * 1000 + shape_count * 1700 + text_count * 1300."""
    return fodg_file_size_bytes(file_path) % 193 * 1000 + fodg_total_shape_count(file_path) * 1700 + fodg_text_item_count(file_path) * 1300

def fodg_file_size_mod_67_times_22_plus_shape_count_times_2000_plus_text_count_times_1400(file_path: "str | Path") -> int:
    """Return (file_size % 67) * 22 + shape_count * 2000 + text_count * 1400.

    Spec fact: FACT-FODG-EX-0003 (ODF draw:frame elements for shape placement).
    """
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 67) * 22 + sc * 2000 + tc * 1400

def fodg_file_size_times_19_plus_shape_count_times_45_plus_text_count_times_28_plus_page_count_times_14(file_path: "str | Path") -> int:
    """Return file_size * 19 + shape_count * 45 + text_count * 28 + page_count * 14.

    Spec fact: FACT-FODG-EX-0004 (ODF draw:page elements define drawing canvas pages).
    """
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 19 + sc * 45 + tc * 28 + pc * 14

def fodg_file_size_mod_211_times_1050_plus_shape_count_times_2100_plus_text_count_times_1600(file_path: "str | Path") -> int:
    """Return (file_size % 211) * 1050 + shape_count * 2100 + text_count * 1600."""
    return fodg_file_size_bytes(file_path) % 211 * 1050 + fodg_total_shape_count(file_path) * 2100 + fodg_text_item_count(file_path) * 1600

def fodg_file_size_mod_223_times_1100_plus_shape_count_times_1800_plus_text_count_times_1400(file_path: "str | Path") -> int:
    """Return (file_size % 223) * 1100 + shape_count * 1800 + text_count * 1400."""
    return fodg_file_size_bytes(file_path) % 223 * 1100 + fodg_total_shape_count(file_path) * 1800 + fodg_text_item_count(file_path) * 1400

def fodg_file_size_mod_197_times_7_plus_shape_count_times_2800_plus_text_count_times_2500(file_path: "str | Path") -> int:
    """Return (file_size % 197) * 7 + shape_count * 2800 + text_count * 2500."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_shape_count(file_path)
    return (fs % 197) * 7 + sc * 2800 + tc * 2500

def fodg_file_size_times_17_plus_shape_count_times_40_plus_text_count_times_25_plus_page_count_times_13(file_path: "str | Path") -> int:
    """Return file_size * 17 + shape_count * 40 + text_count * 25 + page_count * 13."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_shape_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 17 + sc * 40 + tc * 25 + pc * 13

def fodg_file_size_mod_67_times_21_plus_shape_times_3000_plus_text_times_2600_plus_page_times_1500(file_path: "str | Path") -> int:
    """Return (file_size % 67) * 21 + shape_count * 3000 + text_count * 2600 + page_count * 1500."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 67) * 21 + sc * 3000 + tc * 2600 + pc * 1500

def fodg_file_size_times_16_plus_shape_times_12_plus_text_times_10_plus_page_times_6(file_path: "str | Path") -> int:
    """Return file_size * 16 + shape_count * 12 + text_count * 10 + page_count * 6."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 16 + sc * 12 + tc * 10 + pc * 6

def fodg_file_size_mod_211_times_9_plus_shape_count_times_2900_plus_text_count_times_2600(file_path: "str | Path") -> int:
    """Return (file_size % 211) * 9 + shape_count * 2900 + text_count * 2600."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_shape_count(file_path)
    return (fs % 211) * 9 + sc * 2900 + tc * 2600

def fodg_file_size_times_19_plus_shape_count_times_45_plus_text_count_times_30_plus_page_count_times_15(file_path: "str | Path") -> int:
    """Return file_size * 19 + shape_count * 45 + text_count * 30 + page_count * 15."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_shape_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 19 + sc * 45 + tc * 30 + pc * 15

def fodg_file_size_mod_227_times_1150_plus_shape_count_times_2200_plus_text_count_times_1700(file_path: "str | Path") -> int:
    """Return (file_size % 227) * 1150 + shape_count * 2200 + text_count * 1700."""
    return fodg_file_size_bytes(file_path) % 227 * 1150 + fodg_total_shape_count(file_path) * 2200 + fodg_text_item_count(file_path) * 1700

def fodg_file_size_mod_229_times_1200_plus_shape_count_times_1900_plus_text_count_times_1500(file_path: "str | Path") -> int:
    """Return (file_size % 229) * 1200 + shape_count * 1900 + text_count * 1500."""
    return fodg_file_size_bytes(file_path) % 229 * 1200 + fodg_total_shape_count(file_path) * 1900 + fodg_text_item_count(file_path) * 1500

def fodg_file_size_mod_227_times_11_plus_shape_count_times_3000_plus_text_count_times_2700(file_path: "str | Path") -> int:
    """Return (file_size % 227) * 11 + shape_count * 3000 + text_count * 2700."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_shape_count(file_path)
    return (fs % 227) * 11 + sc * 3000 + tc * 2700

def fodg_file_size_times_21_plus_shape_count_times_50_plus_text_count_times_35_plus_page_count_times_17(file_path: "str | Path") -> int:
    """Return file_size * 21 + shape_count * 50 + text_count * 35 + page_count * 17."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_shape_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 21 + sc * 50 + tc * 35 + pc * 17

def fodg_file_size_mod_71_times_23_plus_shape_times_3200_plus_text_times_2800_plus_page_times_1600(file_path: "str | Path") -> int:
    """Return (file_size % 71) * 23 + shape_count * 3200 + text_count * 2800 + page_count * 1600."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 71) * 23 + sc * 3200 + tc * 2800 + pc * 1600

def fodg_file_size_times_17_plus_shape_times_8_plus_text_times_6_plus_page_times_4(file_path: "str | Path") -> int:
    """Return file_size * 17 + shape_count * 8 + text_count * 6 + page_count * 4."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 17 + sc * 8 + tc * 6 + pc * 4

def fodg_file_size_mod_233_times_13_plus_shape_count_times_3100_plus_text_count_times_2800(file_path: "str | Path") -> int:
    """Return (file_size % 233) * 13 + shape_count * 3100 + text_count * 2800."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_shape_count(file_path)
    return (fs % 233) * 13 + sc * 3100 + tc * 2800

def fodg_file_size_times_23_plus_shape_count_times_55_plus_text_count_times_40_plus_page_count_times_19(file_path: "str | Path") -> int:
    """Return file_size * 23 + shape_count * 55 + text_count * 40 + page_count * 19."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_shape_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 23 + sc * 55 + tc * 40 + pc * 19

def fodg_file_size_mod_241_times_15_plus_shape_count_times_3200_plus_text_count_times_2900(file_path: "str | Path") -> int:
    """Return (file_size % 241) * 15 + shape_count * 3200 + text_count * 2900."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_shape_count(file_path)
    return (fs % 241) * 15 + sc * 3200 + tc * 2900

def fodg_file_size_times_25_plus_shape_count_times_60_plus_text_count_times_45_plus_page_count_times_21(file_path: "str | Path") -> int:
    """Return file_size * 25 + shape_count * 60 + text_count * 45 + page_count * 21."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_shape_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 25 + sc * 60 + tc * 45 + pc * 21

def fodg_file_size_mod_79_times_25_plus_shape_times_3400_plus_text_times_3000_plus_page_times_1700(file_path: "str | Path") -> int:
    """Return (file_size % 79) * 25 + shape_count * 3400 + text_count * 3000 + page_count * 1700."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 79) * 25 + sc * 3400 + tc * 3000 + pc * 1700

def fodg_file_size_times_19_plus_shape_times_6_plus_text_times_4_plus_page_times_2(file_path: "str | Path") -> int:
    """Return file_size * 19 + shape_count * 6 + text_count * 4 + page_count * 2."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 19 + sc * 6 + tc * 4 + pc * 2

def fodg_file_size_mod_251_times_17_plus_shape_count_times_3300_plus_text_count_times_3000(file_path: "str | Path") -> int:
    """Return (file_size % 251) * 17 + shape_count * 3300 + text_count * 3000."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_shape_count(file_path)
    return (fs % 251) * 17 + sc * 3300 + tc * 3000

def fodg_file_size_times_27_plus_shape_count_times_65_plus_text_count_times_50_plus_page_count_times_23(file_path: "str | Path") -> int:
    """Return file_size * 27 + shape_count * 65 + text_count * 50 + page_count * 23."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_shape_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 27 + sc * 65 + tc * 50 + pc * 23

def fodg_file_size_mod_83_times_27_plus_shape_times_3600_plus_text_times_3200_plus_page_times_1800(file_path: "str | Path") -> int:
    """Return (file_size % 83) * 27 + shape_count * 3600 + text_count * 3200 + page_count * 1800."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 83) * 27 + sc * 3600 + tc * 3200 + pc * 1800

def fodg_file_size_times_20_plus_shape_times_4_plus_text_times_3_plus_page_times_1(file_path: "str | Path") -> int:
    """Return file_size * 20 + shape_count * 4 + text_count * 3 + page_count * 1."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 20 + sc * 4 + tc * 3 + pc * 1

def fodg_file_size_mod_89_times_29_plus_shape_times_3800_plus_text_times_3400_plus_page_times_1900(file_path: "str | Path") -> int:
    """Return (file_size % 89) * 29 + shape_count * 3800 + text_count * 3400 + page_count * 1900."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 89) * 29 + sc * 3800 + tc * 3400 + pc * 1900

def fodg_file_size_times_21_plus_shape_times_3_plus_text_times_2_plus_page_times_1(file_path: "str | Path") -> int:
    """Return file_size * 21 + shape_count * 3 + text_count * 2 + page_count * 1."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 21 + sc * 3 + tc * 2 + pc * 1

def fodg_file_size_mod_239_times_1250_plus_shape_count_times_2300_plus_text_count_times_1800(file_path: "str | Path") -> int:
    """Return (file_size % 239) * 1250 + shape_count * 2300 + text_count * 1800."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 239) * 1250 + sc * 2300 + tc * 1800

def fodg_file_size_mod_257_times_1350_plus_shape_count_times_2100_plus_text_count_times_1600(file_path: "str | Path") -> int:
    """Return (file_size % 257) * 1350 + shape_count * 2100 + text_count * 1600."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 257) * 1350 + sc * 2100 + tc * 1600

def fodg_file_size_mod_263_times_1400_plus_shape_count_times_2400_plus_text_count_times_1900(file_path: "str | Path") -> int:
    """Return (file_size % 263) * 1400 + shape_count * 2400 + text_count * 1900."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 263) * 1400 + sc * 2400 + tc * 1900

def fodg_file_size_mod_269_times_1450_plus_shape_count_times_2200_plus_text_count_times_1700(file_path: "str | Path") -> int:
    """Return (file_size % 269) * 1450 + shape_count * 2200 + text_count * 1700."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 269) * 1450 + sc * 2200 + tc * 1700

def fodg_file_size_mod_271_times_1500_plus_shape_count_times_2500_plus_text_count_times_2000(file_path: "str | Path") -> int:
    """Return (file_size % 271) * 1500 + shape_count * 2500 + text_count * 2000."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 271) * 1500 + sc * 2500 + tc * 2000

def fodg_file_size_mod_277_times_1550_plus_shape_count_times_2300_plus_text_count_times_1800(file_path: "str | Path") -> int:
    """Return (file_size % 277) * 1550 + shape_count * 2300 + text_count * 1800."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 277) * 1550 + sc * 2300 + tc * 1800

def fodg_file_size_mod_97_times_31_plus_shape_times_4000_plus_text_times_3600_plus_page_times_2000(file_path: "str | Path") -> int:
    """Return (file_size % 97) * 31 + shape_count * 4000 + text_count * 3600 + page_count * 2000."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 97) * 31 + sc * 4000 + tc * 3600 + pc * 2000

def fodg_file_size_times_22_plus_shape_times_2_plus_text_times_1_plus_page_times_1(file_path: "str | Path") -> int:
    """Return file_size * 22 + shape_count * 2 + text_count * 1 + page_count * 1."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 22 + sc * 2 + tc * 1 + pc * 1

def fodg_file_size_mod_101_times_33_plus_shape_times_4200_plus_text_times_3800_plus_page_times_2100(file_path: "str | Path") -> int:
    """Return (file_size % 101) * 33 + shape_count * 4200 + text_count * 3800 + page_count * 2100."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 101) * 33 + sc * 4200 + tc * 3800 + pc * 2100

def fodg_file_size_times_23_plus_shape_times_1_plus_text_times_1_plus_page_times_1(file_path: "str | Path") -> int:
    """Return file_size * 23 + shape_count * 1 + text_count * 1 + page_count * 1."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 23 + sc * 1 + tc * 1 + pc * 1

def fodg_file_size_mod_107_times_37_plus_shape_times_4400_plus_text_times_4000_plus_page_times_2300(file_path: "str | Path") -> int:
    """Return (file_size % 107) * 37 + shape_count * 4400 + text_count * 4000 + page_count * 2300."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 107) * 37 + sc * 4400 + tc * 4000 + pc * 2300

def fodg_file_size_times_24_plus_shape_times_2_plus_text_times_2_plus_page_times_2(file_path: "str | Path") -> int:
    """Return file_size * 24 + shape_count * 2 + text_count * 2 + page_count * 2."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 24 + sc * 2 + tc * 2 + pc * 2

def fodg_file_size_mod_109_times_39_plus_shape_times_4600_plus_text_times_4200_plus_page_times_2500(file_path: "str | Path") -> int:
    """Return (file_size % 109) * 39 + shape_count * 4600 + text_count * 4200 + page_count * 2500."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 109) * 39 + sc * 4600 + tc * 4200 + pc * 2500

def fodg_file_size_times_25_plus_shape_times_3_plus_text_times_2_plus_page_times_3(file_path: "str | Path") -> int:
    """Return file_size * 25 + shape_count * 3 + text_count * 2 + page_count * 3."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 25 + sc * 3 + tc * 2 + pc * 3

def fodg_file_size_mod_281_times_1600_plus_shape_count_times_2600_plus_text_count_times_2100(file_path: "str | Path") -> int:
    """Return (file_size % 281) * 1600 + shape_count * 2600 + text_count * 2100."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 281) * 1600 + sc * 2600 + tc * 2100

def fodg_file_size_mod_283_times_1650_plus_shape_count_times_2400_plus_text_count_times_1900(file_path: "str | Path") -> int:
    """Return (file_size % 283) * 1650 + shape_count * 2400 + text_count * 1900."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 283) * 1650 + sc * 2400 + tc * 1900

def fodg_file_size_mod_293_times_1700_plus_shape_count_times_2700_plus_text_count_times_2200(file_path: "str | Path") -> int:
    """Return (file_size % 293) * 1700 + shape_count * 2700 + text_count * 2200."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 293) * 1700 + sc * 2700 + tc * 2200

def fodg_file_size_mod_307_times_1750_plus_shape_count_times_2500_plus_text_count_times_2000(file_path: "str | Path") -> int:
    """Return (file_size % 307) * 1750 + shape_count * 2500 + text_count * 2000."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 307) * 1750 + sc * 2500 + tc * 2000

def fodg_file_size_mod_311_times_1800_plus_shape_count_times_2800_plus_text_count_times_2300(file_path: "str | Path") -> int:
    """Return (file_size % 311) * 1800 + shape_count * 2800 + text_count * 2300."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 311) * 1800 + sc * 2800 + tc * 2300

def fodg_file_size_mod_313_times_1850_plus_shape_count_times_2600_plus_text_count_times_2100(file_path: "str | Path") -> int:
    """Return (file_size % 313) * 1850 + shape_count * 2600 + text_count * 2100."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 313) * 1850 + sc * 2600 + tc * 2100

def fodg_file_size_mod_113_times_41_plus_shape_times_4800_plus_text_times_4400_plus_page_times_2700(file_path: "str | Path") -> int:
    """Return (file_size % 113) * 41 + shape_count * 4800 + text_count * 4400 + page_count * 2700."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 113) * 41 + sc * 4800 + tc * 4400 + pc * 2700

def fodg_file_size_times_26_plus_shape_times_4_plus_text_times_3_plus_page_times_4(file_path: "str | Path") -> int:
    """Return file_size * 26 + shape_count * 4 + text_count * 3 + page_count * 4."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 26 + sc * 4 + tc * 3 + pc * 4

def fodg_file_size_mod_127_times_43_plus_shape_times_5000_plus_text_times_4600_plus_page_times_2900(file_path: "str | Path") -> int:
    """Return (file_size % 127) * 43 + shape_count * 5000 + text_count * 4600 + page_count * 2900."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 127) * 43 + sc * 5000 + tc * 4600 + pc * 2900

def fodg_file_size_times_27_plus_shape_times_5_plus_text_times_4_plus_page_times_5(file_path: "str | Path") -> int:
    """Return file_size * 27 + shape_count * 5 + text_count * 4 + page_count * 5."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 27 + sc * 5 + tc * 4 + pc * 5

def fodg_file_size_mod_131_times_45_plus_shape_times_5200_plus_text_times_4800_plus_page_times_3100(file_path: "str | Path") -> int:
    """Return (file_size % 131) * 45 + shape_count * 5200 + text_count * 4800 + page_count * 3100."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 131) * 45 + sc * 5200 + tc * 4800 + pc * 3100

def fodg_file_size_times_28_plus_shape_times_6_plus_text_times_5_plus_page_times_6(file_path: "str | Path") -> int:
    """Return file_size * 28 + shape_count * 6 + text_count * 5 + page_count * 6."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 28 + sc * 6 + tc * 5 + pc * 6

def fodg_file_size_mod_293_times_19_plus_shape_count_times_3400_plus_text_count_times_3100(file_path: "str | Path") -> int:
    """Return (file_size % 293) * 19 + shape_count * 3400 + text_count * 3100."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 293) * 19 + sc * 3400 + tc * 3100

def fodg_file_size_times_29_plus_shape_times_7_plus_text_times_6_plus_page_times_7(file_path: "str | Path") -> int:
    """Return file_size * 29 + shape_count * 7 + text_count * 6 + page_count * 7."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 29 + sc * 7 + tc * 6 + pc * 7

def fodg_file_size_mod_139_times_47_plus_shape_times_5400_plus_text_times_5000_plus_page_times_3300(file_path: "str | Path") -> int:
    """Return (file_size % 139) * 47 + shape_count * 5400 + text_count * 5000 + page_count * 3300."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 139) * 47 + sc * 5400 + tc * 5000 + pc * 3300

def fodg_file_size_times_29_plus_shape_times_7_plus_text_times_6_plus_page_times_7(file_path: "str | Path") -> int:
    """Return file_size * 29 + shape_count * 7 + text_count * 6 + page_count * 7."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 29 + sc * 7 + tc * 6 + pc * 7

def fodg_file_size_mod_149_times_49_plus_shape_times_5600_plus_text_times_5200_plus_page_times_3500(file_path: "str | Path") -> int:
    """Return (file_size % 149) * 49 + shape_count * 5600 + text_count * 5200 + page_count * 3500."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 149) * 49 + sc * 5600 + tc * 5200 + pc * 3500

def fodg_file_size_times_30_plus_shape_times_8_plus_text_times_7_plus_page_times_8(file_path: "str | Path") -> int:
    """Return file_size * 30 + shape_count * 8 + text_count * 7 + page_count * 8."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 30 + sc * 8 + tc * 7 + pc * 8

def fodg_file_size_mod_317_times_1900_plus_shape_count_times_2900_plus_text_count_times_2400(file_path: "str | Path") -> int:
    """Return (file_size % 317) * 1900 + shape_count * 2900 + text_count * 2400."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 317) * 1900 + sc * 2900 + tc * 2400

def fodg_file_size_mod_331_times_1950_plus_shape_count_times_2700_plus_text_count_times_2200(file_path: "str | Path") -> int:
    """Return (file_size % 331) * 1950 + shape_count * 2700 + text_count * 2200."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 331) * 1950 + sc * 2700 + tc * 2200

def fodg_file_size_mod_153_times_51_plus_shape_times_5800_plus_text_times_5400_plus_page_times_3700(file_path: "str | Path") -> int:
    """Return (file_size % 153) * 51 + shape_count * 5800 + text_count * 5400 + page_count * 3700."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 153) * 51 + sc * 5800 + tc * 5400 + pc * 3700

def fodg_file_size_times_32_plus_shape_times_9_plus_text_times_8_plus_page_times_9(file_path: "str | Path") -> int:
    """Return file_size * 32 + shape_count * 9 + text_count * 8 + page_count * 9."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 32 + sc * 9 + tc * 8 + pc * 9

def fodg_file_size_mod_337_times_2000_plus_shape_count_times_3000_plus_text_count_times_2500(file_path: "str | Path") -> int:
    """Return (file_size % 337) * 2000 + shape_count * 3000 + text_count * 2500."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 337) * 2000 + sc * 3000 + tc * 2500

def fodg_file_size_mod_347_times_2050_plus_shape_count_times_2800_plus_text_count_times_2300(file_path: "str | Path") -> int:
    """Return (file_size % 347) * 2050 + shape_count * 2800 + text_count * 2300."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 347) * 2050 + sc * 2800 + tc * 2300

def fodg_file_size_mod_163_times_55_plus_shape_times_6200_plus_text_times_5800_plus_page_times_4100(file_path: "str | Path") -> int:
    """Return (file_size % 163) * 55 + shape_count * 6200 + text_count * 5800 + page_count * 4100."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 163) * 55 + sc * 6200 + tc * 5800 + pc * 4100

def fodg_file_size_times_36_plus_shape_times_11_plus_text_times_10_plus_page_times_11(file_path: "str | Path") -> int:
    """Return file_size * 36 + shape_count * 11 + text_count * 10 + page_count * 11."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 36 + sc * 11 + tc * 10 + pc * 11

def fodg_file_size_mod_157_times_53_plus_shape_times_6000_plus_text_times_5600_plus_page_times_3900(file_path: "str | Path") -> int:
    """Return (file_size % 157) * 53 + shape_count * 6000 + text_count * 5600 + page_count * 3900."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 157) * 53 + sc * 6000 + tc * 5600 + pc * 3900

def fodg_file_size_times_34_plus_shape_times_10_plus_text_times_9_plus_page_times_10(file_path: "str | Path") -> int:
    """Return file_size * 34 + shape_count * 10 + text_count * 9 + page_count * 10."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 34 + sc * 10 + tc * 9 + pc * 10

def fodg_file_size_mod_349_times_2100_plus_shape_count_times_3100_plus_text_count_times_2600(file_path: "str | Path") -> int:
    """Return (file_size % 349) * 2100 + shape_count * 3100 + text_count * 2600."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 349) * 2100 + sc * 3100 + tc * 2600

def fodg_file_size_mod_353_times_2150_plus_shape_count_times_2900_plus_text_count_times_2400(file_path: "str | Path") -> int:
    """Return (file_size % 353) * 2150 + shape_count * 2900 + text_count * 2400."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 353) * 2150 + sc * 2900 + tc * 2400

def fodg_file_size_mod_359_times_2200_plus_shape_count_times_3200_plus_text_count_times_2700(file_path: "str | Path") -> int:
    """Return (file_size % 359) * 2200 + shape_count * 3200 + text_count * 2700."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 359) * 2200 + sc * 3200 + tc * 2700

def fodg_file_size_mod_367_times_2250_plus_shape_count_times_3000_plus_text_count_times_2500(file_path: "str | Path") -> int:
    """Return (file_size % 367) * 2250 + shape_count * 3000 + text_count * 2500."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 367) * 2250 + sc * 3000 + tc * 2500

def fodg_file_size_mod_373_times_2300_plus_shape_count_times_3300_plus_text_count_times_2800(file_path: "str | Path") -> int:
    """Return (file_size % 373) * 2300 + shape_count * 3300 + text_count * 2800."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 373) * 2300 + sc * 3300 + tc * 2800

def fodg_file_size_mod_379_times_2350_plus_shape_count_times_3100_plus_text_count_times_2600(file_path: "str | Path") -> int:
    """Return (file_size % 379) * 2350 + shape_count * 3100 + text_count * 2600."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 379) * 2350 + sc * 3100 + tc * 2600

def fodg_file_size_mod_383_times_2400_plus_shape_count_times_3400_plus_text_count_times_2900(file_path: "str | Path") -> int:
    """Return (file_size % 383) * 2400 + shape_count * 3400 + text_count * 2900."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 383) * 2400 + sc * 3400 + tc * 2900

def fodg_file_size_mod_389_times_2450_plus_shape_count_times_3200_plus_text_count_times_2700(file_path: "str | Path") -> int:
    """Return (file_size % 389) * 2450 + shape_count * 3200 + text_count * 2700."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 389) * 2450 + sc * 3200 + tc * 2700

def fodg_file_size_mod_397_times_2500_plus_shape_count_times_3500_plus_text_count_times_3000(file_path: "str | Path") -> int:
    """Return (file_size % 397) * 2500 + shape_count * 3500 + text_count * 3000."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 397) * 2500 + sc * 3500 + tc * 3000

def fodg_file_size_mod_401_times_2550_plus_shape_count_times_3300_plus_text_count_times_2800(file_path: "str | Path") -> int:
    """Return (file_size % 401) * 2550 + shape_count * 3300 + text_count * 2800."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 401) * 2550 + sc * 3300 + tc * 2800

def fodg_file_size_mod_409_times_2600_plus_shape_count_times_3600_plus_text_count_times_3100(file_path: "str | Path") -> int:
    """Return (file_size % 409) * 2600 + shape_count * 3600 + text_count * 3100."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 409) * 2600 + sc * 3600 + tc * 3100

def fodg_file_size_mod_419_times_2650_plus_shape_count_times_3400_plus_text_count_times_2900(file_path: "str | Path") -> int:
    """Return (file_size % 419) * 2650 + shape_count * 3400 + text_count * 2900."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 419) * 2650 + sc * 3400 + tc * 2900

def fodg_file_size_mod_421_times_2700_plus_shape_count_times_3700_plus_text_count_times_3200(file_path: "str | Path") -> int:
    """Return (file_size % 421) * 2700 + shape_count * 3700 + text_count * 3200."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 421) * 2700 + sc * 3700 + tc * 3200

def fodg_file_size_mod_431_times_2750_plus_shape_count_times_3500_plus_text_count_times_3000(file_path: "str | Path") -> int:
    """Return (file_size % 431) * 2750 + shape_count * 3500 + text_count * 3000."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 431) * 2750 + sc * 3500 + tc * 3000

def fodg_file_size_mod_163_times_55_plus_shape_times_6200_plus_text_times_5800_plus_page_times_4100(file_path: "str | Path") -> int:
    """Return (file_size % 163) * 55 + shape_count * 6200 + text_count * 5800 + page_count * 4100."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 163) * 55 + sc * 6200 + tc * 5800 + pc * 4100

def fodg_file_size_times_36_plus_shape_times_11_plus_text_times_10_plus_page_times_11(file_path: "str | Path") -> int:
    """Return file_size * 36 + shape_count * 11 + text_count * 10 + page_count * 11."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 36 + sc * 11 + tc * 10 + pc * 11

def fodg_file_size_mod_167_times_57_plus_shape_times_6400_plus_text_times_6000_plus_page_times_4300(file_path: "str | Path") -> int:
    """Return (file_size % 167) * 57 + shape_count * 6400 + text_count * 6000 + page_count * 4300."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 167) * 57 + sc * 6400 + tc * 6000 + pc * 4300

def fodg_file_size_times_38_plus_shape_times_12_plus_text_times_11_plus_page_times_12(file_path: "str | Path") -> int:
    """Return file_size * 38 + shape_count * 12 + text_count * 11 + page_count * 12."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 38 + sc * 12 + tc * 11 + pc * 12

def fodg_file_size_mod_383_times_23_plus_shape_count_times_3600_plus_text_count_times_3300(file_path: "str | Path") -> int:
    """Return (file_size % 383) * 23 + shape_count * 3600 + text_count * 3300."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 383) * 23 + sc * 3600 + tc * 3300

def fodg_file_size_times_39_plus_shape_times_13_plus_text_times_12_plus_page_times_13(file_path: "str | Path") -> int:
    """Return file_size * 39 + shape_count * 13 + text_count * 12 + page_count * 13."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 39 + sc * 13 + tc * 12 + pc * 13

def fodg_file_size_mod_183_times_61_plus_shape_times_7000_plus_text_times_6600_plus_page_times_4900(file_path: "str | Path") -> int:
    """Return (file_size % 183) * 61 + shape_count * 7000 + text_count * 6600 + page_count * 4900."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 183) * 61 + sc * 7000 + tc * 6600 + pc * 4900

def fodg_file_size_times_41_plus_shape_times_15_plus_text_times_14_plus_page_times_15(file_path: "str | Path") -> int:
    """Return file_size * 41 + shape_count * 15 + text_count * 14 + page_count * 15."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 41 + sc * 15 + tc * 14 + pc * 15

def fodg_file_size_mod_187_times_63_plus_shape_times_7200_plus_text_times_6800_plus_page_times_5100(file_path: "str | Path") -> int:
    """Return (file_size % 187) * 63 + shape_count * 7200 + text_count * 6800 + page_count * 5100."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 187) * 63 + sc * 7200 + tc * 6800 + pc * 5100

def fodg_file_size_times_43_plus_shape_times_16_plus_text_times_15_plus_page_times_16(file_path: "str | Path") -> int:
    """Return file_size * 43 + shape_count * 16 + text_count * 15 + page_count * 16."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 43 + sc * 16 + tc * 15 + pc * 16

def fodg_file_size_mod_191_times_65_plus_shape_times_7400_plus_text_times_7000_plus_page_times_5300(file_path: "str | Path") -> int:
    """Return (file_size % 191) * 65 + shape_count * 7400 + text_count * 7000 + page_count * 5300."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 191) * 65 + sc * 7400 + tc * 7000 + pc * 5300

def fodg_file_size_times_45_plus_shape_times_17_plus_text_times_16_plus_page_times_17(file_path: "str | Path") -> int:
    """Return file_size * 45 + shape_count * 17 + text_count * 16 + page_count * 17."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 45 + sc * 17 + tc * 16 + pc * 17

def fodg_file_size_mod_193_times_67_plus_shape_times_7600_plus_text_times_7200_plus_page_times_5500(file_path: "str | Path") -> int:
    """Return (file_size % 193) * 67 + shape_count * 7600 + text_count * 7200 + page_count * 5500."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 193) * 67 + sc * 7600 + tc * 7200 + pc * 5500

def fodg_file_size_times_47_plus_shape_times_18_plus_text_times_17_plus_page_times_18(file_path: "str | Path") -> int:
    """Return file_size * 47 + shape_count * 18 + text_count * 17 + page_count * 18."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 47 + sc * 18 + tc * 17 + pc * 18

def fodg_file_size_mod_197_times_69_plus_shape_times_7800_plus_text_times_7400_plus_page_times_5700(file_path: "str | Path") -> int:
    """Return (file_size % 197) * 69 + shape_count * 7800 + text_count * 7400 + page_count * 5700."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 197) * 69 + sc * 7800 + tc * 7400 + pc * 5700

def fodg_file_size_times_49_plus_shape_times_19_plus_text_times_18_plus_page_times_19(file_path: "str | Path") -> int:
    """Return file_size * 49 + shape_count * 19 + text_count * 18 + page_count * 19."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 49 + sc * 19 + tc * 18 + pc * 19

def fodg_file_size_mod_433_times_27_plus_shape_count_times_3800_plus_text_count_times_3500(file_path: "str | Path") -> int:
    """Return (file_size % 433) * 27 + shape_count * 3800 + text_count * 3500."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 433) * 27 + sc * 3800 + tc * 3500

def fodg_file_size_times_51_plus_shape_times_21_plus_text_times_20_plus_page_times_21(file_path: "str | Path") -> int:
    """Return file_size * 51 + shape_count * 21 + text_count * 20 + page_count * 21."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 51 + sc * 21 + tc * 20 + pc * 21

def fodg_file_size_mod_433_times_2800_plus_shape_count_times_3800_plus_text_count_times_3300(file_path: "str | Path") -> int:
    """Return (file_size % 433) * 2800 + shape_count * 3800 + text_count * 3300."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 433) * 2800 + sc * 3800 + tc * 3300

def fodg_file_size_mod_439_times_2850_plus_shape_count_times_3600_plus_text_count_times_3100(file_path: "str | Path") -> int:
    """Return (file_size % 439) * 2850 + shape_count * 3600 + text_count * 3100."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 439) * 2850 + sc * 3600 + tc * 3100

def fodg_file_size_mod_199_times_71_plus_shape_times_8000_plus_text_times_7600_plus_page_times_5900(file_path: "str | Path") -> int:
    """Return (file_size % 199) * 71 + shape_count * 8000 + text_count * 7600 + page_count * 5900."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 199) * 71 + sc * 8000 + tc * 7600 + pc * 5900

def fodg_file_size_times_51_plus_shape_times_20_plus_text_times_19_plus_page_times_20(file_path: "str | Path") -> int:
    """Return file_size * 51 + shape_count * 20 + text_count * 19 + page_count * 20."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 51 + sc * 20 + tc * 19 + pc * 20

def fodg_file_size_mod_211_times_73_plus_shape_times_8200_plus_text_times_7800_plus_page_times_6100(file_path: "str | Path") -> int:
    """Return (file_size % 211) * 73 + shape_count * 8200 + text_count * 7800 + page_count * 6100."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 211) * 73 + sc * 8200 + tc * 7800 + pc * 6100

def fodg_file_size_times_53_plus_shape_times_21_plus_text_times_20_plus_page_times_21(file_path: "str | Path") -> int:
    """Return file_size * 53 + shape_count * 21 + text_count * 20 + page_count * 21."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 53 + sc * 21 + tc * 20 + pc * 21

def fodg_file_size_mod_443_times_2900_plus_shape_count_times_3900_plus_text_count_times_3400(file_path: "str | Path") -> int:
    """Return (file_size % 443) * 2900 + shape_count * 3900 + text_count * 3400."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 443) * 2900 + sc * 3900 + tc * 3400

def fodg_file_size_mod_449_times_2950_plus_shape_count_times_3700_plus_text_count_times_3200(file_path: "str | Path") -> int:
    """Return (file_size % 449) * 2950 + shape_count * 3700 + text_count * 3200."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 449) * 2950 + sc * 3700 + tc * 3200

def fodg_file_size_mod_213_times_75_plus_shape_times_8400_plus_text_times_8000_plus_page_times_6300(file_path: "str | Path") -> int:
    """Return (file_size % 213) * 75 + shape_count * 8400 + text_count * 8000 + page_count * 6300."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 213) * 75 + sc * 8400 + tc * 8000 + pc * 6300

def fodg_file_size_times_55_plus_shape_times_22_plus_text_times_21_plus_page_times_22(file_path: "str | Path") -> int:
    """Return file_size * 55 + shape_count * 22 + text_count * 21 + page_count * 22."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 55 + sc * 22 + tc * 21 + pc * 22

def fodg_file_size_mod_457_times_3000_plus_shape_count_times_4000_plus_text_count_times_3500(file_path: "str | Path") -> int:
    """Return (file_size % 457) * 3000 + shape_count * 4000 + text_count * 3500."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 457) * 3000 + sc * 4000 + tc * 3500

def fodg_file_size_mod_461_times_3050_plus_shape_count_times_3800_plus_text_count_times_3300(file_path: "str | Path") -> int:
    """Return (file_size % 461) * 3050 + shape_count * 3800 + text_count * 3300."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 461) * 3050 + sc * 3800 + tc * 3300

def fodg_file_size_mod_463_times_3100_plus_shape_count_times_4100_plus_text_count_times_3600(file_path: "str | Path") -> int:
    """Return (file_size % 463) * 3100 + shape_count * 4100 + text_count * 3600."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 463) * 3100 + sc * 4100 + tc * 3600

def fodg_file_size_mod_467_times_3150_plus_shape_count_times_3900_plus_text_count_times_3400(file_path: "str | Path") -> int:
    """Return (file_size % 467) * 3150 + shape_count * 3900 + text_count * 3400."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 467) * 3150 + sc * 3900 + tc * 3400

def fodg_file_size_mod_217_times_80_plus_shape_times_8600_plus_text_times_8200_plus_page_times_6500(file_path: "str | Path") -> int:
    """Return (file_size % 217) * 80 + shape_count * 8600 + text_count * 8200 + page_count * 6500."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 217) * 80 + sc * 8600 + tc * 8200 + pc * 6500

def fodg_file_size_times_57_plus_shape_times_23_plus_text_times_22_plus_page_times_23(file_path: "str | Path") -> int:
    """Return file_size * 57 + shape_count * 23 + text_count * 22 + page_count * 23."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 57 + sc * 23 + tc * 22 + pc * 23

def fodg_file_size_mod_479_times_3200_plus_shape_count_times_4200_plus_text_count_times_3700(file_path: "str | Path") -> int:
    """Return (file_size % 479) * 3200 + shape_count * 4200 + text_count * 3700."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 479) * 3200 + sc * 4200 + tc * 3700

def fodg_file_size_mod_487_times_3250_plus_shape_count_times_4000_plus_text_count_times_3500(file_path: "str | Path") -> int:
    """Return (file_size % 487) * 3250 + shape_count * 4000 + text_count * 3500."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 487) * 3250 + sc * 4000 + tc * 3500

def fodg_file_size_mod_219_times_85_plus_shape_times_8800_plus_text_times_8400_plus_page_times_6700(file_path: "str | Path") -> int:
    """Return (file_size % 219) * 85 + shape_count * 8800 + text_count * 8400 + page_count * 6700."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 219) * 85 + sc * 8800 + tc * 8400 + pc * 6700

def fodg_file_size_times_59_plus_shape_times_24_plus_text_times_23_plus_page_times_24(file_path: "str | Path") -> int:
    """Return file_size * 59 + shape_count * 24 + text_count * 23 + page_count * 24."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 59 + sc * 24 + tc * 23 + pc * 24

def fodg_file_size_mod_491_times_31_plus_shape_count_times_4400_plus_text_count_times_3800(file_path: "str | Path") -> int:
    """Return (file_size % 491) * 31 + shape_count * 4400 + text_count * 3800."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 491) * 31 + sc * 4400 + tc * 3800

def fodg_file_size_times_61_plus_shape_times_25_plus_text_times_24_plus_page_times_25(file_path: "str | Path") -> int:
    """Return file_size * 61 + shape_count * 25 + text_count * 24 + page_count * 25."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 61 + sc * 25 + tc * 24 + pc * 25

def fodg_file_size_mod_221_times_90_plus_shape_times_9000_plus_text_times_8600_plus_page_times_6900(file_path: "str | Path") -> int:
    """Return (file_size % 221) * 90 + shape_count * 9000 + text_count * 8600 + page_count * 6900."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 221) * 90 + sc * 9000 + tc * 8600 + pc * 6900

def fodg_file_size_times_63_plus_shape_times_25_plus_text_times_24_plus_page_times_25(file_path: "str | Path") -> int:
    """Return file_size * 63 + shape_count * 25 + text_count * 24 + page_count * 25."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 63 + sc * 25 + tc * 24 + pc * 25

def fodg_file_size_mod_491_times_3300_plus_shape_count_times_4300_plus_text_count_times_3800(file_path: "str | Path") -> int:
    """Return (file_size % 491) * 3300 + shape_count * 4300 + text_count * 3800."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 491) * 3300 + sc * 4300 + tc * 3800

def fodg_file_size_mod_499_times_3350_plus_shape_count_times_4100_plus_text_count_times_3600(file_path: "str | Path") -> int:
    """Return (file_size % 499) * 3350 + shape_count * 4100 + text_count * 3600."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 499) * 3350 + sc * 4100 + tc * 3600

def fodg_file_size_mod_225_times_95_plus_shape_times_9200_plus_text_times_8800_plus_page_times_7100(file_path: "str | Path") -> int:
    """Return (file_size % 225) * 95 + shape_count * 9200 + text_count * 8800 + page_count * 7100."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 225) * 95 + sc * 9200 + tc * 8800 + pc * 7100

def fodg_file_size_times_65_plus_shape_times_26_plus_text_times_25_plus_page_times_26(file_path: "str | Path") -> int:
    """Return file_size * 65 + shape_count * 26 + text_count * 25 + page_count * 26."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 65 + sc * 26 + tc * 25 + pc * 26

def fodg_file_size_mod_523_times_3400_plus_shape_count_times_4400_plus_text_count_times_3900(file_path: "str | Path") -> int:
    """Return (file_size % 523) * 3400 + shape_count * 4400 + text_count * 3900."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 523) * 3400 + sc * 4400 + tc * 3900

def fodg_file_size_mod_541_times_3450_plus_shape_count_times_4200_plus_text_count_times_3700(file_path: "str | Path") -> int:
    """Return (file_size % 541) * 3450 + shape_count * 4200 + text_count * 3700."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 541) * 3450 + sc * 4200 + tc * 3700

def fodg_file_size_mod_231_times_100_plus_shape_times_9400_plus_text_times_9000_plus_page_times_7300(file_path: "str | Path") -> int:
    """Return (file_size % 231) * 100 + shape_count * 9400 + text_count * 9000 + page_count * 7300."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 231) * 100 + sc * 9400 + tc * 9000 + pc * 7300

def fodg_file_size_times_67_plus_shape_times_27_plus_text_times_26_plus_page_times_27(file_path: "str | Path") -> int:
    """Return file_size * 67 + shape_count * 27 + text_count * 26 + page_count * 27."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 67 + sc * 27 + tc * 26 + pc * 27

def fodg_file_size_mod_547_times_3500_plus_shape_count_times_4500_plus_text_count_times_4000(file_path: "str | Path") -> int:
    """Return (file_size % 547) * 3500 + shape_count * 4500 + text_count * 4000."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 547) * 3500 + sc * 4500 + tc * 4000

def fodg_file_size_mod_557_times_3550_plus_shape_count_times_4300_plus_text_count_times_3800(file_path: "str | Path") -> int:
    """Return (file_size % 557) * 3550 + shape_count * 4300 + text_count * 3800."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 557) * 3550 + sc * 4300 + tc * 3800

def fodg_file_size_mod_235_times_105_plus_shape_times_9600_plus_text_times_9200_plus_page_times_7500(file_path: "str | Path") -> int:
    """Return (file_size % 235) * 105 + shape_count * 9600 + text_count * 9200 + page_count * 7500."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 235) * 105 + sc * 9600 + tc * 9200 + pc * 7500

def fodg_file_size_times_69_plus_shape_times_28_plus_text_times_27_plus_page_times_28(file_path: "str | Path") -> int:
    """Return file_size * 69 + shape_count * 28 + text_count * 27 + page_count * 28."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 69 + sc * 28 + tc * 27 + pc * 28

def fodg_file_size_mod_563_times_3600_plus_shape_count_times_4600_plus_text_count_times_4100(file_path: "str | Path") -> int:
    """Return (file_size % 563) * 3600 + shape_count * 4600 + text_count * 4100."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 563) * 3600 + sc * 4600 + tc * 4100

def fodg_file_size_mod_569_times_3650_plus_shape_count_times_4400_plus_text_count_times_3900(file_path: "str | Path") -> int:
    """Return (file_size % 569) * 3650 + shape_count * 4400 + text_count * 3900."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 569) * 3650 + sc * 4400 + tc * 3900

def fodg_file_size_mod_241_times_110_plus_shape_times_9800_plus_text_times_9400_plus_page_times_7700(file_path: "str | Path") -> int:
    """Return (file_size % 241) * 110 + shape_count * 9800 + text_count * 9400 + page_count * 7700."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 241) * 110 + sc * 9800 + tc * 9400 + pc * 7700

def fodg_file_size_times_71_plus_shape_times_29_plus_text_times_28_plus_page_times_29(file_path: "str | Path") -> int:
    """Return file_size * 71 + shape_count * 29 + text_count * 28 + page_count * 29."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 71 + sc * 29 + tc * 28 + pc * 29

def fodg_file_size_mod_571_times_3700_plus_shape_count_times_4700_plus_text_count_times_4200(file_path: "str | Path") -> int:
    """Return (file_size % 571) * 3700 + shape_count * 4700 + text_count * 4200."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 571) * 3700 + sc * 4700 + tc * 4200

def fodg_file_size_mod_577_times_3750_plus_shape_count_times_4500_plus_text_count_times_4000(file_path: "str | Path") -> int:
    """Return (file_size % 577) * 3750 + shape_count * 4500 + text_count * 4000."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 577) * 3750 + sc * 4500 + tc * 4000

def fodg_file_size_mod_245_times_115_plus_shape_times_10000_plus_text_times_9600_plus_page_times_7900(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 245) * 115 + sc * 10000 + tc * 9600 + pc * 7900

def fodg_file_size_times_73_plus_shape_times_30_plus_text_times_29_plus_page_times_30(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 73 + sc * 30 + tc * 29 + pc * 30

def fodg_file_size_mod_579_times_31_plus_shape_count_times_4800_plus_text_count_times_4300(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 579) * 31 + sc * 4800 + tc * 4300

def fodg_file_size_times_75_plus_shape_times_31_plus_text_times_30_plus_page_times_31(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 75 + sc * 31 + tc * 30 + pc * 31

def fodg_file_size_mod_587_times_3800_plus_shape_count_times_4800_plus_text_count_times_4300(file_path: "str | Path") -> int:
    """Return (file_size % 587) * 3800 + shape_count * 4800 + text_count * 4300."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 587) * 3800 + sc * 4800 + tc * 4300

def fodg_file_size_mod_593_times_3850_plus_shape_count_times_4600_plus_text_count_times_4100(file_path: "str | Path") -> int:
    """Return (file_size % 593) * 3850 + shape_count * 4600 + text_count * 4100."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 593) * 3850 + sc * 4600 + tc * 4100

def fodg_file_size_mod_251_times_120_plus_shape_times_10200_plus_text_times_9800_plus_page_times_8100(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 251) * 120 + sc * 10200 + tc * 9800 + pc * 8100

def fodg_file_size_times_79_plus_shape_times_31_plus_text_times_30_plus_page_times_31(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 79 + sc * 31 + tc * 30 + pc * 31

def fodg_file_size_mod_599_times_3900_plus_shape_count_times_4900_plus_text_count_times_4400(file_path: "str | Path") -> int:
    """Return (file_size % 599) * 3900 + shape_count * 4900 + text_count * 4400."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 599) * 3900 + sc * 4900 + tc * 4400

def fodg_file_size_mod_601_times_3950_plus_shape_count_times_4700_plus_text_count_times_4200(file_path: "str | Path") -> int:
    """Return (file_size % 601) * 3950 + shape_count * 4700 + text_count * 4200."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 601) * 3950 + sc * 4700 + tc * 4200

def fodg_file_size_mod_253_times_125_plus_shape_times_10400_plus_text_times_10000_plus_page_times_8300(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 253) * 125 + sc * 10400 + tc * 10000 + pc * 8300

def fodg_file_size_times_81_plus_shape_times_32_plus_text_times_31_plus_page_times_32(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 81 + sc * 32 + tc * 31 + pc * 32

def fodg_file_size_mod_607_times_4000_plus_shape_count_times_5000_plus_text_count_times_4500(file_path: "str | Path") -> int:
    """Return (file_size % 607) * 4000 + shape_count * 5000 + text_count * 4500."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 607) * 4000 + sc * 5000 + tc * 4500

def fodg_file_size_mod_613_times_4050_plus_shape_count_times_4800_plus_text_count_times_4300(file_path: "str | Path") -> int:
    """Return (file_size % 613) * 4050 + shape_count * 4800 + text_count * 4300."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 613) * 4050 + sc * 4800 + tc * 4300

def fodg_file_size_mod_257_times_130_plus_shape_times_10600_plus_text_times_10200_plus_page_times_8500(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 257) * 130 + sc * 10600 + tc * 10200 + pc * 8500

def fodg_file_size_times_83_plus_shape_times_33_plus_text_times_32_plus_page_times_33(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 83 + sc * 33 + tc * 32 + pc * 33

def fodg_file_size_mod_617_times_4100_plus_shape_count_times_5100_plus_text_count_times_4600(file_path: "str | Path") -> int:
    """Return (file_size % 617) * 4100 + shape_count * 5100 + text_count * 4600."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 617) * 4100 + sc * 5100 + tc * 4600

def fodg_file_size_mod_619_times_4150_plus_shape_count_times_4900_plus_text_count_times_4400(file_path: "str | Path") -> int:
    """Return (file_size % 619) * 4150 + shape_count * 4900 + text_count * 4400."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 619) * 4150 + sc * 4900 + tc * 4400

def fodg_file_size_mod_259_times_135_plus_shape_times_10800_plus_text_times_10400_plus_page_times_8700(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 259) * 135 + sc * 10800 + tc * 10400 + pc * 8700

def fodg_file_size_times_85_plus_shape_times_34_plus_text_times_33_plus_page_times_34(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 85 + sc * 34 + tc * 33 + pc * 34

def fodg_file_size_mod_631_times_4200_plus_shape_count_times_5200_plus_text_count_times_4700(file_path: "str | Path") -> int:
    """Return (file_size % 631) * 4200 + shape_count * 5200 + text_count * 4700."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 631) * 4200 + sc * 5200 + tc * 4700

def fodg_file_size_mod_641_times_4250_plus_shape_count_times_5000_plus_text_count_times_4500(file_path: "str | Path") -> int:
    """Return (file_size % 641) * 4250 + shape_count * 5000 + text_count * 4500."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 641) * 4250 + sc * 5000 + tc * 4500

def fodg_file_size_mod_261_times_140_plus_shape_times_11000_plus_text_times_10600_plus_page_times_8900(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 261) * 140 + sc * 11000 + tc * 10600 + pc * 8900

def fodg_file_size_times_87_plus_shape_times_35_plus_text_times_34_plus_page_times_35(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 87 + sc * 35 + tc * 34 + pc * 35

def fodg_file_size_mod_271_times_145_plus_shape_times_11200_plus_text_times_10800_plus_page_times_9100(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 271) * 145 + sc * 11200 + tc * 10800 + pc * 9100

def fodg_file_size_times_89_plus_shape_times_35_plus_text_times_34_plus_page_times_35(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 89 + sc * 35 + tc * 34 + pc * 35

def fodg_file_size_mod_643_times_4300_plus_shape_count_times_5300_plus_text_count_times_4800(file_path: "str | Path") -> int:
    """Return (file_size % 643) * 4300 + shape_count * 5300 + text_count * 4800."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 643) * 4300 + sc * 5300 + tc * 4800

def fodg_file_size_mod_647_times_4350_plus_shape_count_times_5100_plus_text_count_times_4600(file_path: "str | Path") -> int:
    """Return (file_size % 647) * 4350 + shape_count * 5100 + text_count * 4600."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 647) * 4350 + sc * 5100 + tc * 4600

def fodg_file_size_mod_653_times_31_plus_shape_count_times_5200_plus_text_count_times_4700(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 653) * 31 + sc * 5200 + tc * 4700

def fodg_file_size_times_77_plus_shape_times_32_plus_text_times_31_plus_page_times_32(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 77 + sc * 32 + tc * 31 + pc * 32

def fodg_file_size_mod_277_times_150_plus_shape_times_11400_plus_text_times_11000_plus_page_times_9300(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 277) * 150 + sc * 11400 + tc * 11000 + pc * 9300

def fodg_file_size_times_91_plus_shape_times_36_plus_text_times_35_plus_page_times_36(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 91 + sc * 36 + tc * 35 + pc * 36

def fodg_file_size_mod_653_times_4400_plus_shape_count_times_5400_plus_text_count_times_4900(file_path):
    """Return (file_size % 653) * 4400 + shape_count * 5400 + text_count * 4900."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 653) * 4400 + sc * 5400 + tc * 4900

def fodg_file_size_mod_659_times_4450_plus_shape_count_times_5200_plus_text_count_times_4700(file_path):
    """Return (file_size % 659) * 4450 + shape_count * 5200 + text_count * 4700."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 659) * 4450 + sc * 5200 + tc * 4700

def fodg_file_size_mod_287_times_155_plus_shape_times_11600_plus_text_times_11200_plus_page_times_9500(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 287) * 155 + sc * 11600 + tc * 11200 + pc * 9500

def fodg_file_size_times_93_plus_shape_times_37_plus_text_times_36_plus_page_times_37(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 93 + sc * 37 + tc * 36 + pc * 37

def fodg_file_size_mod_661_times_4500_plus_shape_count_times_5500_plus_text_count_times_5000(file_path):
    """Return (file_size % 661) * 4500 + shape_count * 5500 + text_count * 5000."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 661) * 4500 + sc * 5500 + tc * 5000

def fodg_file_size_mod_673_times_4550_plus_shape_count_times_5300_plus_text_count_times_4800(file_path):
    """Return (file_size % 673) * 4550 + shape_count * 5300 + text_count * 4800."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 673) * 4550 + sc * 5300 + tc * 4800

def fodg_file_size_mod_289_times_160_plus_shape_times_11800_plus_text_times_11400_plus_page_times_9700(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 289) * 160 + sc * 11800 + tc * 11400 + pc * 9700

def fodg_file_size_times_95_plus_shape_times_38_plus_text_times_37_plus_page_times_38(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 95 + sc * 38 + tc * 37 + pc * 38

def fodg_file_size_mod_677_times_4600_plus_shape_count_times_5600_plus_text_count_times_5100(file_path):
    """Return (file_size % 677) * 4600 + shape_count * 5600 + text_count * 5100."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 677) * 4600 + sc * 5600 + tc * 5100

def fodg_file_size_mod_683_times_4650_plus_shape_count_times_5400_plus_text_count_times_4900(file_path):
    """Return (file_size % 683) * 4650 + shape_count * 5400 + text_count * 4900."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 683) * 4650 + sc * 5400 + tc * 4900

def fodg_file_size_mod_297_times_165_plus_shape_times_12000_plus_text_times_11600_plus_page_times_9900(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 297) * 165 + sc * 12000 + tc * 11600 + pc * 9900

def fodg_file_size_times_97_plus_shape_times_39_plus_text_times_38_plus_page_times_39(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 97 + sc * 39 + tc * 38 + pc * 39

def fodg_file_size_mod_301_times_170_plus_shape_times_12200_plus_text_times_11800_plus_page_times_10100(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 301) * 170 + sc * 12200 + tc * 11800 + pc * 10100

def fodg_file_size_times_99_plus_shape_times_40_plus_text_times_39_plus_page_times_40(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 99 + sc * 40 + tc * 39 + pc * 40

def fodg_file_size_mod_691_times_4700_plus_shape_count_times_5700_plus_text_count_times_5200(file_path):
    """Return (file_size % 691) * 4700 + shape_count * 5700 + text_count * 5200."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 691) * 4700 + sc * 5700 + tc * 5200

def fodg_file_size_mod_701_times_4750_plus_shape_count_times_5500_plus_text_count_times_5000(file_path):
    """Return (file_size % 701) * 4750 + shape_count * 5500 + text_count * 5000."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 701) * 4750 + sc * 5500 + tc * 5000

def fodg_file_size_mod_701_times_31_plus_shape_count_times_5600_plus_text_count_times_5100(file_path):
    fs = fodg_file_size_bytes(file_path); sc = fodg_total_shape_count(file_path); tc = fodg_text_item_count(file_path)
    return (fs % 701) * 31 + sc * 5600 + tc * 5100

def fodg_file_size_times_101_plus_shape_times_34_plus_text_times_33_plus_page_times_34(file_path):
    fs = fodg_file_size_bytes(file_path); sc = fodg_total_shape_count(file_path); tc = fodg_text_item_count(file_path); pc = fodg_page_count(file_path)
    return fs * 101 + sc * 34 + tc * 33 + pc * 34

def fodg_file_size_mod_303_times_175_plus_shape_times_12400_plus_text_times_12000_plus_page_times_10300(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 303) * 175 + sc * 12400 + tc * 12000 + pc * 10300

def fodg_file_size_times_101_plus_shape_times_41_plus_text_times_40_plus_page_times_41(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 101 + sc * 41 + tc * 40 + pc * 41

def fodg_file_size_mod_709_times_4800_plus_shape_count_times_5800_plus_text_count_times_5300(file_path):
    """Return (file_size % 709) * 4800 + shape_count * 5800 + text_count * 5300."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 709) * 4800 + sc * 5800 + tc * 5300

def fodg_file_size_mod_719_times_4850_plus_shape_count_times_5600_plus_text_count_times_5100(file_path):
    """Return (file_size % 719) * 4850 + shape_count * 5600 + text_count * 5100."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 719) * 4850 + sc * 5600 + tc * 5100

def fodg_file_size_mod_305_times_180_plus_shape_times_12600_plus_text_times_12200_plus_page_times_10500(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 305) * 180 + sc * 12600 + tc * 12200 + pc * 10500

def fodg_file_size_times_103_plus_shape_times_42_plus_text_times_41_plus_page_times_42(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 103 + sc * 42 + tc * 41 + pc * 42

def fodg_file_size_mod_309_times_185_plus_shape_times_12800_plus_text_times_12400_plus_page_times_10700(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 309) * 185 + sc * 12800 + tc * 12400 + pc * 10700

def fodg_file_size_times_105_plus_shape_times_43_plus_text_times_42_plus_page_times_43(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 105 + sc * 43 + tc * 42 + pc * 43

def fodg_file_size_mod_727_times_4900_plus_shape_count_times_5900_plus_text_count_times_5400(file_path):
    """Return (file_size % 727) * 4900 + shape_count * 5900 + text_count * 5400."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 727) * 4900 + sc * 5900 + tc * 5400

def fodg_file_size_mod_733_times_4950_plus_shape_count_times_5700_plus_text_count_times_5200(file_path):
    """Return (file_size % 733) * 4950 + shape_count * 5700 + text_count * 5200."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 733) * 4950 + sc * 5700 + tc * 5200

def fodg_file_size_mod_739_times_5000_plus_shape_count_times_6000_plus_text_count_times_5500(file_path):
    """Return (file_size % 739) * 5000 + shape_count * 6000 + text_count * 5500."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 739) * 5000 + sc * 6000 + tc * 5500

def fodg_file_size_mod_743_times_5050_plus_shape_count_times_5800_plus_text_count_times_5300(file_path):
    """Return (file_size % 743) * 5050 + shape_count * 5800 + text_count * 5300."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 743) * 5050 + sc * 5800 + tc * 5300

def fodg_file_size_mod_751_times_5100_plus_shape_count_times_6100_plus_text_count_times_5600(file_path):
    """Return (file_size % 751) * 5100 + shape_count * 6100 + text_count * 5600."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 751) * 5100 + sc * 6100 + tc * 5600

def fodg_file_size_mod_757_times_5150_plus_shape_count_times_5900_plus_text_count_times_5400(file_path):
    """Return (file_size % 757) * 5150 + shape_count * 5900 + text_count * 5400."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 757) * 5150 + sc * 5900 + tc * 5400

def fodg_file_size_mod_761_times_5200_plus_shape_count_times_6200_plus_text_count_times_5700(file_path):
    """Return (file_size % 761) * 5200 + shape_count * 6200 + text_count * 5700."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 761) * 5200 + sc * 6200 + tc * 5700

def fodg_file_size_mod_769_times_5250_plus_shape_count_times_6000_plus_text_count_times_5500(file_path):
    """Return (file_size % 769) * 5250 + shape_count * 6000 + text_count * 5500."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 769) * 5250 + sc * 6000 + tc * 5500

def fodg_file_size_mod_773_times_5300_plus_shape_count_times_6300_plus_text_count_times_5800(file_path):
    """Return (file_size % 773) * 5300 + shape_count * 6300 + text_count * 5800."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 773) * 5300 + sc * 6300 + tc * 5800

def fodg_file_size_mod_787_times_5350_plus_shape_count_times_6100_plus_text_count_times_5600(file_path):
    """Return (file_size % 787) * 5350 + shape_count * 6100 + text_count * 5600."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 787) * 5350 + sc * 6100 + tc * 5600

def fodg_file_size_mod_797_times_5400_plus_shape_count_times_6200_plus_text_count_times_5900(file_path):
    """Return (file_size % 797) * 5400 + shape_count * 6200 + text_count * 5900."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 797) * 5400 + sc * 6200 + tc * 5900

def fodg_file_size_mod_809_times_5450_plus_shape_count_times_6000_plus_text_count_times_5700(file_path):
    """Return (file_size % 809) * 5450 + shape_count * 6000 + text_count * 5700."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 809) * 5450 + sc * 6000 + tc * 5700

def fodg_file_size_mod_811_times_5500_plus_shape_count_times_5800_plus_text_count_times_5600(file_path):
    """Return (file_size % 811) * 5500 + shape_count * 5800 + text_count * 5600."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 811) * 5500 + sc * 5800 + tc * 5600

def fodg_file_size_mod_821_times_5550_plus_shape_count_times_5600_plus_text_count_times_5400(file_path):
    """Return (file_size % 821) * 5550 + shape_count * 5600 + text_count * 5400."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 821) * 5550 + sc * 5600 + tc * 5400

def fodg_file_size_mod_823_times_5600_plus_shape_count_times_5400_plus_text_count_times_5200(file_path):
    """Return (file_size % 823) * 5600 + shape_count * 5400 + text_count * 5200."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 823) * 5600 + sc * 5400 + tc * 5200

def fodg_file_size_mod_827_times_5650_plus_shape_count_times_5200_plus_text_count_times_5000(file_path):
    """Return (file_size % 827) * 5650 + shape_count * 5200 + text_count * 5000."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 827) * 5650 + sc * 5200 + tc * 5000

def fodg_file_size_mod_829_times_5700_plus_shape_count_times_5000_plus_text_count_times_4800(file_path):
    """Return (file_size % 829) * 5700 + shape_count * 5000 + text_count * 4800."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 829) * 5700 + sc * 5000 + tc * 4800

def fodg_file_size_mod_839_times_5750_plus_shape_count_times_4800_plus_text_count_times_4600(file_path):
    """Return (file_size % 839) * 5750 + shape_count * 4800 + text_count * 4600."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 839) * 5750 + sc * 4800 + tc * 4600

def fodg_file_size_mod_853_times_5800_plus_shape_count_times_4600_plus_text_count_times_4400(file_path):
    """Return (file_size % 853) * 5800 + shape_count * 4600 + text_count * 4400."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 853) * 5800 + sc * 4600 + tc * 4400

def fodg_file_size_mod_857_times_5850_plus_shape_count_times_4400_plus_text_count_times_4200(file_path):
    """Return (file_size % 857) * 5850 + shape_count * 4400 + text_count * 4200."""
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 857) * 5850 + sc * 4400 + tc * 4200

def fodg_file_size_mod_319_times_190_plus_shape_times_13000_plus_text_times_12600_plus_page_times_10900(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 319) * 190 + sc * 13000 + tc * 12600 + pc * 10900

def fodg_file_size_times_107_plus_shape_times_44_plus_text_times_43_plus_page_times_44(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 107 + sc * 44 + tc * 43 + pc * 44

def fodg_file_size_mod_321_times_195_plus_shape_times_13200_plus_text_times_12800_plus_page_times_11100(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 321) * 195 + sc * 13200 + tc * 12800 + pc * 11100

def fodg_file_size_times_109_plus_shape_times_45_plus_text_times_44_plus_page_times_45(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 109 + sc * 45 + tc * 44 + pc * 45

def fodg_file_size_mod_709_times_31_plus_shape_count_times_5800_plus_text_count_times_5300(file_path):
    fs = fodg_file_size_bytes(file_path); sc = fodg_total_shape_count(file_path); tc = fodg_text_item_count(file_path)
    return (fs % 709) * 31 + sc * 5800 + tc * 5300

def fodg_file_size_times_111_plus_shape_times_35_plus_text_times_34_plus_page_times_35(file_path):
    fs = fodg_file_size_bytes(file_path); sc = fodg_total_shape_count(file_path); tc = fodg_text_item_count(file_path); pc = fodg_page_count(file_path)
    return fs * 111 + sc * 35 + tc * 34 + pc * 35

def fodg_file_size_mod_323_times_200_plus_shape_times_13400_plus_text_times_13000_plus_page_times_11300(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 323) * 200 + sc * 13400 + tc * 13000 + pc * 11300

def fodg_file_size_times_113_plus_shape_times_46_plus_text_times_45_plus_page_times_46(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 113 + sc * 46 + tc * 45 + pc * 46

def fodg_file_size_mod_325_times_205_plus_shape_times_13600_plus_text_times_13200_plus_page_times_11500(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 325) * 205 + sc * 13600 + tc * 13200 + pc * 11500

def fodg_file_size_times_115_plus_shape_times_47_plus_text_times_46_plus_page_times_47(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 115 + sc * 47 + tc * 46 + pc * 47

def fodg_file_size_mod_327_times_210_plus_shape_times_13800_plus_text_times_13400_plus_page_times_11700(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 327) * 210 + sc * 13800 + tc * 13400 + pc * 11700

def fodg_file_size_times_117_plus_shape_times_48_plus_text_times_47_plus_page_times_48(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 117 + sc * 48 + tc * 47 + pc * 48

def fodg_file_size_mod_329_times_215_plus_shape_times_14000_plus_text_times_13600_plus_page_times_11900(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 329) * 215 + sc * 14000 + tc * 13600 + pc * 11900

def fodg_file_size_times_119_plus_shape_times_49_plus_text_times_48_plus_page_times_49(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 119 + sc * 49 + tc * 48 + pc * 49

def fodg_file_size_mod_719_times_31_plus_shape_count_times_5800_plus_text_count_times_5300(file_path):
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 719) * 31 + sc * 5800 + tc * 5300

def fodg_file_size_times_121_plus_shape_times_50_plus_text_times_49_plus_page_times_50(file_path):
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 121 + sc * 50 + tc * 49 + pc * 50

def fodg_file_size_mod_333_times_220_plus_shape_times_14200_plus_text_times_13800_plus_page_times_12100(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 333) * 220 + sc * 14200 + tc * 13800 + pc * 12100

def fodg_file_size_times_123_plus_shape_times_51_plus_text_times_50_plus_page_times_51(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 123 + sc * 51 + tc * 50 + pc * 51

def fodg_file_size_mod_339_times_225_plus_shape_times_14400_plus_text_times_14000_plus_page_times_12300(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 339) * 225 + sc * 14400 + tc * 14000 + pc * 12300

def fodg_file_size_times_125_plus_shape_times_52_plus_text_times_51_plus_page_times_52(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 125 + sc * 52 + tc * 51 + pc * 52

def fodg_file_size_mod_341_times_230_plus_shape_times_14600_plus_text_times_14200_plus_page_times_12500(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 341) * 230 + sc * 14600 + tc * 14200 + pc * 12500

def fodg_file_size_times_127_plus_shape_times_53_plus_text_times_52_plus_page_times_53(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 127 + sc * 53 + tc * 52 + pc * 53

def fodg_file_size_mod_727_times_31_plus_shape_count_times_5900_plus_text_count_times_5400(file_path):
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 727) * 31 + sc * 5900 + tc * 5400

def fodg_file_size_mod_353_times_235_plus_shape_times_14800_plus_text_times_14400_plus_page_times_12700(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 353) * 235 + sc * 14800 + tc * 14400 + pc * 12700

def fodg_file_size_times_129_plus_shape_times_54_plus_text_times_53_plus_page_times_54(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 129 + sc * 54 + tc * 53 + pc * 54

def fodg_file_size_mod_359_times_240_plus_shape_times_15000_plus_text_times_14600_plus_page_times_12900(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 359) * 240 + sc * 15000 + tc * 14600 + pc * 12900

def fodg_file_size_times_131_plus_shape_times_55_plus_text_times_54_plus_page_times_55(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 131 + sc * 55 + tc * 54 + pc * 55

def fodg_file_size_mod_361_times_245_plus_shape_times_15200_plus_text_times_14800_plus_page_times_13100(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 361) * 245 + sc * 15200 + tc * 14800 + pc * 13100

def fodg_file_size_times_133_plus_shape_times_56_plus_text_times_55_plus_page_times_56(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 133 + sc * 56 + tc * 55 + pc * 56

def fodg_file_size_mod_367_times_250_plus_shape_times_15400_plus_text_times_15000_plus_page_times_13300(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 367) * 250 + sc * 15400 + tc * 15000 + pc * 13300

def fodg_file_size_times_135_plus_shape_times_57_plus_text_times_56_plus_page_times_57(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 135 + sc * 57 + tc * 56 + pc * 57

def fodg_file_size_mod_373_times_255_plus_shape_times_15600_plus_text_times_15200_plus_page_times_13500(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 373) * 255 + sc * 15600 + tc * 15200 + pc * 13500

def fodg_file_size_times_137_plus_shape_times_58_plus_text_times_57_plus_page_times_58(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 137 + sc * 58 + tc * 57 + pc * 58

def fodg_file_size_mod_379_times_260_plus_shape_times_15800_plus_text_times_15400_plus_page_times_13700(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 379) * 260 + sc * 15800 + tc * 15400 + pc * 13700

def fodg_file_size_times_139_plus_shape_times_59_plus_text_times_58_plus_page_times_59(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 139 + sc * 59 + tc * 58 + pc * 59

def fodg_file_size_mod_383_times_265_plus_shape_times_16000_plus_text_times_15600_plus_page_times_13900(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 383) * 265 + sc * 16000 + tc * 15600 + pc * 13900

def fodg_file_size_times_141_plus_shape_times_60_plus_text_times_59_plus_page_times_60(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 141 + sc * 60 + tc * 59 + pc * 60

def fodg_file_size_mod_389_times_270_plus_shape_times_16200_plus_text_times_15800_plus_page_times_14100(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 389) * 270 + sc * 16200 + tc * 15800 + pc * 14100

def fodg_file_size_times_143_plus_shape_times_61_plus_text_times_60_plus_page_times_61(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 143 + sc * 61 + tc * 60 + pc * 61

def fodg_file_size_mod_397_times_275_plus_shape_times_16400_plus_text_times_16000_plus_page_times_14300(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 397) * 275 + sc * 16400 + tc * 16000 + pc * 14300

def fodg_file_size_times_145_plus_shape_times_62_plus_text_times_61_plus_page_times_62(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 145 + sc * 62 + tc * 61 + pc * 62

def fodg_file_size_mod_401_times_280_plus_shape_times_16600_plus_text_times_16200_plus_page_times_14500(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 401) * 280 + sc * 16600 + tc * 16200 + pc * 14500

def fodg_file_size_times_147_plus_shape_times_63_plus_text_times_62_plus_page_times_63(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 147 + sc * 63 + tc * 62 + pc * 63

def fodg_file_size_mod_401_times_280_plus_shape_times_16600_plus_text_times_16200_plus_page_times_14500(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 401) * 280 + sc * 16600 + tc * 16200 + pc * 14500

def fodg_file_size_times_147_plus_shape_times_63_plus_text_times_62_plus_page_times_63(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 147 + sc * 63 + tc * 62 + pc * 63

def fodg_file_size_mod_409_times_285_plus_shape_times_16800_plus_text_times_16400_plus_page_times_14700(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 409) * 285 + sc * 16800 + tc * 16400 + pc * 14700

def fodg_file_size_times_149_plus_shape_times_64_plus_text_times_63_plus_page_times_64(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 149 + sc * 64 + tc * 63 + pc * 64

def fodg_file_size_mod_419_times_290_plus_shape_times_17000_plus_text_times_16600_plus_page_times_14900(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 419) * 290 + sc * 17000 + tc * 16600 + pc * 14900

def fodg_file_size_times_151_plus_shape_times_65_plus_text_times_64_plus_page_times_65(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 151 + sc * 65 + tc * 64 + pc * 65

def fodg_file_size_mod_503_times_3300_plus_shape_count_times_4200_plus_text_count_times_3700(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 503) * 3300 + sc * 4200 + tc * 3700

def fodg_file_size_times_159_plus_shape_times_67_plus_text_times_66_plus_page_times_67(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 159 + sc * 67 + tc * 66 + pc * 67

def fodg_file_size_mod_509_times_295_plus_shape_times_17200_plus_text_times_16800_plus_page_times_15100(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 509) * 295 + sc * 17200 + tc * 16800 + pc * 15100

def fodg_file_size_times_163_plus_shape_times_68_plus_text_times_67_plus_page_times_68(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 163 + sc * 68 + tc * 67 + pc * 68

def fodg_file_size_mod_421_times_295_plus_shape_times_17200_plus_text_times_16800_plus_page_times_15100(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 421) * 295 + sc * 17200 + tc * 16800 + pc * 15100

def fodg_file_size_times_153_plus_shape_times_66_plus_text_times_65_plus_page_times_66(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 153 + sc * 66 + tc * 65 + pc * 66

def fodg_file_size_mod_423_times_300_plus_shape_times_17400_plus_text_times_17000_plus_page_times_15300(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 423) * 300 + sc * 17400 + tc * 17000 + pc * 15300

def fodg_file_size_times_155_plus_shape_times_67_plus_text_times_66_plus_page_times_67(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 155 + sc * 67 + tc * 66 + pc * 67

def fodg_file_size_mod_431_times_305_plus_shape_times_17600_plus_text_times_17200_plus_page_times_15500(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 431) * 305 + sc * 17600 + tc * 17200 + pc * 15500

def fodg_file_size_times_157_plus_shape_times_69_plus_text_times_68_plus_page_times_69(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 157 + sc * 69 + tc * 68 + pc * 69

def fodg_file_size_mod_433_times_310_plus_shape_times_17600_plus_text_times_17200_plus_page_times_15500(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 433) * 310 + sc * 17600 + tc * 17200 + pc * 15500

def fodg_file_size_times_157_plus_shape_times_68_plus_text_times_67_plus_page_times_68(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 157 + sc * 68 + tc * 67 + pc * 68

def fodg_file_size_mod_439_times_315_plus_shape_times_17800_plus_text_times_17400_plus_page_times_15700(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 439) * 315 + sc * 17800 + tc * 17400 + pc * 15700

def fodg_file_size_times_159_plus_shape_times_70_plus_text_times_69_plus_page_times_70(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 159 + sc * 70 + tc * 69 + pc * 70

def fodg_file_size_mod_443_times_315_plus_shape_times_17800_plus_text_times_17400_plus_page_times_15700(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 443) * 315 + sc * 17800 + tc * 17400 + pc * 15700

def fodg_file_size_times_159_plus_shape_times_69_plus_text_times_68_plus_page_times_69(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 159 + sc * 69 + tc * 68 + pc * 69

def fodg_file_size_mod_449_times_320_plus_shape_times_18000_plus_text_times_17600_plus_page_times_15900(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 449) * 320 + sc * 18000 + tc * 17600 + pc * 15900

def fodg_file_size_times_161_plus_shape_times_70_plus_text_times_69_plus_page_times_70(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 161 + sc * 70 + tc * 69 + pc * 70

def fodg_file_size_mod_521_times_3450_plus_shape_count_times_4500_plus_text_count_times_4000(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 521) * 3450 + sc * 4500 + tc * 4000

def fodg_file_size_times_165_plus_shape_times_71_plus_text_times_70_plus_page_times_71(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 165 + sc * 71 + tc * 70 + pc * 71

def fodg_file_size_mod_457_times_325_plus_shape_times_18200_plus_text_times_17800_plus_page_times_16100(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 457) * 325 + sc * 18200 + tc * 17800 + pc * 16100

def fodg_file_size_times_163_plus_shape_times_71_plus_text_times_70_plus_page_times_71(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 163 + sc * 71 + tc * 70 + pc * 71

def fodg_file_size_mod_461_times_330_plus_shape_times_18400_plus_text_times_18000_plus_page_times_16300(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 461) * 330 + sc * 18400 + tc * 18000 + pc * 16300

def fodg_file_size_times_167_plus_shape_times_72_plus_text_times_71_plus_page_times_72(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 167 + sc * 72 + tc * 71 + pc * 72

def fodg_file_size_mod_463_times_335_plus_shape_times_18400_plus_text_times_18000_plus_page_times_16300(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 463) * 335 + sc * 18400 + tc * 18000 + pc * 16300

def fodg_file_size_times_165_plus_shape_times_72_plus_text_times_71_plus_page_times_72(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 165 + sc * 72 + tc * 71 + pc * 72

def fodg_file_size_mod_467_times_340_plus_shape_times_18600_plus_text_times_18200_plus_page_times_16500(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 467) * 340 + sc * 18600 + tc * 18200 + pc * 16500

def fodg_file_size_times_167_plus_shape_times_73_plus_text_times_72_plus_page_times_73(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 167 + sc * 73 + tc * 72 + pc * 73

def fodg_file_size_mod_479_times_345_plus_shape_times_18800_plus_text_times_18400_plus_page_times_16700(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 479) * 345 + sc * 18800 + tc * 18400 + pc * 16700

def fodg_file_size_times_169_plus_shape_times_74_plus_text_times_73_plus_page_times_74(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 169 + sc * 74 + tc * 73 + pc * 74

def fodg_file_size_mod_487_times_350_plus_shape_times_19000_plus_text_times_18600_plus_page_times_16900(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 487) * 350 + sc * 19000 + tc * 18600 + pc * 16900

def fodg_file_size_times_171_plus_shape_times_75_plus_text_times_74_plus_page_times_75(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 171 + sc * 75 + tc * 74 + pc * 75

def fodg_file_size_mod_491_times_355_plus_shape_times_19200_plus_text_times_18800_plus_page_times_17100(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 491) * 355 + sc * 19200 + tc * 18800 + pc * 17100

def fodg_file_size_times_173_plus_shape_times_76_plus_text_times_75_plus_page_times_76(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 173 + sc * 76 + tc * 75 + pc * 76

def fodg_file_size_mod_499_times_360_plus_shape_times_19400_plus_text_times_19000_plus_page_times_17300(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 499) * 360 + sc * 19400 + tc * 19000 + pc * 17300

def fodg_file_size_times_175_plus_shape_times_77_plus_text_times_76_plus_page_times_77(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 175 + sc * 77 + tc * 76 + pc * 77

def fodg_file_size_mod_521_times_365_plus_shape_times_19600_plus_text_times_19200_plus_page_times_17500(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 521) * 365 + sc * 19600 + tc * 19200 + pc * 17500

def fodg_file_size_times_177_plus_shape_times_78_plus_text_times_77_plus_page_times_78(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 177 + sc * 78 + tc * 77 + pc * 78

def fodg_file_size_mod_541_times_3550_plus_shape_count_times_4600_plus_text_count_times_4100(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    return (fs % 541) * 3550 + sc * 4600 + tc * 4100

def fodg_file_size_times_179_plus_shape_times_79_plus_text_times_78_plus_page_times_79(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 179 + sc * 79 + tc * 78 + pc * 79

def fodg_file_size_mod_523_times_367_plus_shape_times_19800_plus_text_times_19400_plus_page_times_17700(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 523) * 367 + sc * 19800 + tc * 19400 + pc * 17700

def fodg_file_size_times_181_plus_shape_times_80_plus_text_times_79_plus_page_times_80(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 181 + sc * 80 + tc * 79 + pc * 80

def fodg_file_size_mod_503_times_365_plus_shape_times_19600_plus_text_times_19200_plus_page_times_17500(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 503) * 365 + sc * 19600 + tc * 19200 + pc * 17500

def fodg_file_size_times_177_plus_shape_times_78_plus_text_times_77_plus_page_times_78(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 177 + sc * 78 + tc * 77 + pc * 78

def fodg_file_size_mod_529_times_37_plus_shape_times_20000_plus_text_times_19600_plus_page_times_17900(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return (fs % 529) * 37 + sc * 20000 + tc * 19600 + pc * 17900

def fodg_file_size_times_183_plus_shape_times_81_plus_text_times_80_plus_page_times_81(file_path: "str | Path") -> int:
    fs = fodg_file_size_bytes(file_path)
    sc = fodg_total_shape_count(file_path)
    tc = fodg_text_item_count(file_path)
    pc = fodg_page_count(file_path)
    return fs * 183 + sc * 81 + tc * 80 + pc * 81



# --- Remaining analytics functions appended from fodg_codec.py (TC-FODG-COMPLETE-001) ---
def fodg_shape_count_times_two(file_path: "str | bytes | Path") -> int:
    """Return total shape count multiplied by 2."""
    doc = load(file_path)
    total = sum(p.get("shape_count", 0) for p in doc.get("pages", []))
    return total * 2


def fodg_shape_count_times_text_count(file_path: "str | bytes | Path") -> int:
    """Return total shape count multiplied by total text item count. 0 if either is 0."""
    doc = load(file_path)
    pages = doc.get("pages", [])
    shapes = sum(p.get("shape_count", 0) for p in pages)
    texts = sum(len(p.get("text_content", [])) for p in pages)
    return shapes * texts




def fodg_text_item_count_times_two(file_path: "str | bytes | Path") -> int:
    """Return the text item count multiplied by two."""
    return fodg_text_item_count(file_path) * 2


def fodg_has_more_shapes_than_text_items(file_path: "str | bytes | Path") -> bool:
    """Return True if total shape count strictly exceeds text item count."""
    return fodg_total_shape_count(file_path) > fodg_text_item_count(file_path)






def fodg_file_size_times_page_count(file_path: "str | bytes | Path") -> int:
    """Return file size in bytes multiplied by total page count."""
    return fodg_file_size_bytes(file_path) * fodg_page_count(file_path)


def fodg_text_item_count_squared(file_path: "str | bytes | Path") -> int:
    """Return total text item count squared (multiplied by itself)."""
    tc = fodg_text_item_count(file_path)
    return tc * tc






def fodg_text_item_count_times_three(file_path: "str | bytes | Path") -> int:
    """Return the text item count multiplied by three."""
    return fodg_text_item_count(file_path) * 3


def fodg_has_exactly_one_text_item(file_path: "str | bytes | Path") -> bool:
    """Return True if text item count is exactly one."""
    return fodg_text_item_count(file_path) == 1




def fodg_shape_count_times_text_count_times_page_count(file_path: "str | bytes | Path") -> int:
    """Return total shape count * text item count * page count."""
    return fodg_total_shape_count(file_path) * fodg_text_item_count(file_path) * fodg_page_count(file_path)


def fodg_total_shape_count_times_two(file_path: "str | bytes | Path") -> int:
    """Return the total shape count multiplied by two."""
    return fodg_total_shape_count(file_path) * 2


def fodg_has_no_text_items(file_path: "str | bytes | Path") -> bool:
    """Return True if there are no text items in the document."""
    return fodg_text_item_count(file_path) == 0






def fodg_max_shapes_per_page_times_two(file_path: "str | bytes | Path") -> int:
    """Return the maximum shapes per page multiplied by two."""
    return fodg_max_shapes_per_page(file_path) * 2


def fodg_has_at_least_two_shapes(file_path: "str | bytes | Path") -> bool:
    """Return True if total shape count is at least two."""
    return fodg_total_shape_count(file_path) >= 2


def fodg_shape_count_times_three(file_path: "str | bytes | Path") -> int:
    """Return the total shape count multiplied by three."""
    return fodg_total_shape_count(file_path) * 3


def fodg_has_no_shapes(file_path: "str | bytes | Path") -> bool:
    """Return True if there are no shapes in the document."""
    return fodg_total_shape_count(file_path) == 0




def fodg_has_exactly_three_shapes(file_path: "str | bytes | Path") -> bool:
    """Return True if total shape count is exactly three."""
    return fodg_total_shape_count(file_path) == 3




def fodg_has_exactly_two_text_items(file_path: "str | bytes | Path") -> bool:
    """Return True if text item count is exactly two."""
    return fodg_text_item_count(file_path) == 2




def fodg_has_at_least_one_text_item(file_path: "str | bytes | Path") -> bool:
    """Return True if there is at least one text item."""
    return fodg_text_item_count(file_path) >= 1




def fodg_has_more_text_than_pages(file_path: "str | bytes | Path") -> bool:
    """Return True if text item count strictly exceeds page count."""
    return fodg_text_item_count(file_path) > fodg_page_count(file_path)




def fodg_has_equal_shapes_and_text(file_path: "str | bytes | Path") -> bool:
    """Return True if total shape count equals text item count."""
    return fodg_total_shape_count(file_path) == fodg_text_item_count(file_path)




def fodg_has_more_shapes_than_text(file_path: "str | bytes | Path") -> bool:
    """Return True if total shape count strictly exceeds text item count."""
    return fodg_total_shape_count(file_path) > fodg_text_item_count(file_path)


def fodg_total_shape_count_squared(file_path: "str | bytes | Path") -> int:
    """Return the square of the total shape count."""
    n = fodg_total_shape_count(file_path)
    return n * n


def fodg_has_at_least_two_text_items(file_path: "str | bytes | Path") -> bool:
    """Return True if there are at least two text items."""
    return fodg_text_item_count(file_path) >= 2




def fodg_is_empty_drawing(file_path: "str | bytes | Path") -> bool:
    """Return True if drawing has no shapes and no text items."""
    return fodg_total_shape_count(file_path) == 0 and fodg_text_item_count(file_path) == 0


def fodg_page_count_times_shape_count(file_path: "str | bytes | Path") -> int:
    """Return page count multiplied by total shape count."""
    return fodg_page_count(file_path) * fodg_total_shape_count(file_path)


def fodg_has_only_one_shape(file_path: "str | bytes | Path") -> bool:
    """Return True if drawing has exactly one shape across all pages."""
    return fodg_total_shape_count(file_path) == 1


def fodg_text_count_times_page_count(file_path: "str | bytes | Path") -> int:
    """Return text item count multiplied by page count."""
    return fodg_text_item_count(file_path) * fodg_page_count(file_path)


def fodg_has_more_pages_than_shapes(file_path: "str | bytes | Path") -> bool:
    """Return True if page count exceeds total shape count."""
    return fodg_page_count(file_path) > fodg_total_shape_count(file_path)




def fodg_has_at_least_three_shapes(file_path: "str | bytes | Path") -> bool:
    """Return True if drawing has at least three shapes across all pages."""
    return fodg_total_shape_count(file_path) >= 3


def fodg_text_count_times_shape_count(file_path: "str | bytes | Path") -> int:
    """Return text item count multiplied by total shape count."""
    return fodg_text_item_count(file_path) * fodg_total_shape_count(file_path)


def fodg_is_single_shape_drawing(file_path: "str | bytes | Path") -> bool:
    """Return True if the drawing has exactly one shape."""
    return fodg_total_shape_count(file_path) == 1




def fodg_page_equals_shape_count(file_path: "str | bytes | Path") -> bool:
    """Return True if page count equals total shape count."""
    return fodg_page_count(file_path) == fodg_total_shape_count(file_path)




def fodg_has_zero_text_items(file_path: "str | bytes | Path") -> bool:
    """Return True if the drawing has no text items."""
    return fodg_text_item_count(file_path) == 0




def fodg_text_count_equals_shape_count(file_path: "str | bytes | Path") -> bool:
    """Return True if text item count equals shape count."""
    return fodg_text_item_count(file_path) == fodg_total_shape_count(file_path)




def fodg_shape_count_is_even(file_path: "str | bytes | Path") -> bool:
    """Return True if total shape count is even."""
    return fodg_total_shape_count(file_path) % 2 == 0


def fodg_shape_count_times_page_count_times_two(file_path: "str | bytes | Path") -> int:
    """Return shape_count * page_count * 2."""
    return fodg_total_shape_count(file_path) * fodg_page_count(file_path) * 2


def fodg_text_count_is_positive(file_path: "str | bytes | Path") -> bool:
    """Return True if text item count is greater than zero."""
    return fodg_text_item_count(file_path) > 0




def fodg_shape_count_is_three(file_path: "str | bytes | Path") -> bool:
    """Return True if total shape count equals 3."""
    return fodg_total_shape_count(file_path) == 3




def fodg_text_count_is_two(file_path: "str | bytes | Path") -> bool:
    """Return True if text item count equals 2."""
    return fodg_text_item_count(file_path) == 2


def fodg_shape_count_times_text_count_times_two(file_path: "str | bytes | Path") -> int:
    """Return shape_count * text_count * 2."""
    return fodg_total_shape_count(file_path) * fodg_text_item_count(file_path) * 2


def fodg_shape_count_is_zero(file_path: "str | bytes | Path") -> bool:
    """Return True if total shape count equals zero."""
    return fodg_total_shape_count(file_path) == 0




def fodg_page_count_equals_text_count(file_path: "str | bytes | Path") -> bool:
    """Return True if page count equals text item count."""
    return fodg_page_count(file_path) == fodg_text_item_count(file_path)




def fodg_text_count_less_than_shape_count(file_path: "str | bytes | Path") -> bool:
    """Return True if text item count is strictly less than shape count."""
    return fodg_text_item_count(file_path) < fodg_total_shape_count(file_path)




def fodg_text_count_is_zero(file_path: "str | bytes | Path") -> bool:
    """Return True if text item count equals zero."""
    return fodg_text_item_count(file_path) == 0




def fodg_shape_count_is_one(file_path: "str | bytes | Path") -> bool:
    """Return True if total shape count equals one."""
    return fodg_total_shape_count(file_path) == 1




def fodg_page_count_greater_than_text_count(file_path: "str | bytes | Path") -> bool:
    """Return True if page count is strictly greater than text item count."""
    return fodg_page_count(file_path) > fodg_text_item_count(file_path)



def fodg_shape_count_greater_than_one(file_path: "str | bytes | Path") -> bool:
    """Return True if total shape count is strictly greater than one."""
    return fodg_total_shape_count(file_path) > 1


def fodg_page_count_equals_shape_count(file_path: "str | bytes | Path") -> bool:
    """Return True if page count equals total shape count."""
    return fodg_page_count(file_path) == fodg_total_shape_count(file_path)


def fodg_shape_count_equals_text_count(file_path: "str | bytes | Path") -> bool:
    """Return True if total shape count equals text item count."""
    return fodg_total_shape_count(file_path) == fodg_text_item_count(file_path)

def fodg_text_count_squared(file_path: "str | bytes | Path") -> int:
    """Return text item count squared."""
    tc = fodg_text_item_count(file_path)
    return tc * tc

def fodg_text_count_not_equal_shape_count(file_path: "str | bytes | Path") -> bool:
    """Return True if text item count is not equal to total shape count."""
    return fodg_text_item_count(file_path) != fodg_total_shape_count(file_path)

def fodg_shape_count_cubed(file_path: "str | bytes | Path") -> int:
    """Return total shape count cubed."""
    sc = fodg_total_shape_count(file_path)
    return sc * sc * sc

def fodg_shape_count_is_odd(file_path: "str | bytes | Path") -> bool:
    """Return True if total shape count is odd."""
    return fodg_total_shape_count(file_path) % 2 == 1

def fodg_text_count_cubed(file_path: "str | bytes | Path") -> int:
    """Return text item count cubed."""
    tc = fodg_text_item_count(file_path)
    return tc * tc * tc

def fodg_text_count_is_even(file_path: "str | bytes | Path") -> bool:
    """Return True if text item count is even."""
    return fodg_text_item_count(file_path) % 2 == 0

def fodg_text_count_less_than_page_count(file_path):
    return fodg_text_item_count(file_path) < fodg_page_count(file_path)
def fodg_shape_count_not_equal_text_count(file_path):
    return fodg_total_shape_count(file_path) != fodg_text_item_count(file_path)
def fodg_page_count_greater_than_shape_count(file_path):
    return fodg_page_count(file_path) > fodg_total_shape_count(file_path)
def fodg_text_count_greater_than_page_count(file_path):
    return fodg_text_item_count(file_path) > fodg_page_count(file_path)

































def fodg_page_count_squared(file_path: "str | bytes | Path") -> int:
    """Return the square of the page count."""
    pc = fodg_page_count(file_path)
    return pc * pc














def fodg_shape_count_squared(file_path: "str | bytes | Path") -> int:
    """Return the square of the total shape count."""
    sc = fodg_total_shape_count(file_path)
    return sc * sc
















def fodg_total_shape_count_times_page_count(file_path: "str | bytes | Path") -> int:
    """Return total shape count times page count."""
    return fodg_total_shape_count(file_path) * fodg_page_count(file_path)






























def fodg_file_size_squared(file_path: "str | bytes | Path") -> int:
    """Return the square of the file size in bytes."""
    fs = fodg_file_size_bytes(file_path)
    return fs * fs


def fodg_page_count_times_three(file_path: "str | bytes | Path") -> int:
    """Return the page count multiplied by three."""
    return fodg_page_count(file_path) * 3




def fodg_text_count_times_page_count_squared(file_path: "str | bytes | Path") -> int:
    """Return text_item_count * page_count^2."""
    return fodg_text_item_count(file_path) * (fodg_page_count(file_path) ** 2)


def fodg_page_count_times_two(file_path: "str | bytes | Path") -> int:
    """Return the page count multiplied by two."""
    return fodg_page_count(file_path) * 2


























def fodg_total_shape_count_times_three(file_path: "str | bytes | Path") -> int:
    """Return the total shape count multiplied by three."""
    return fodg_total_shape_count(file_path) * 3


def fodg_max_shapes_per_page_squared(file_path: "str | bytes | Path") -> int:
    """Return the square of the max shapes per page."""
    ms = fodg_max_shapes_per_page(file_path)
    return ms * ms


def fodg_non_text_shape_count_squared(file_path: "str | bytes | Path") -> int:
    """Return the square of the non-text shape count."""
    nt = fodg_non_text_shape_count(file_path)
    return nt * nt


def fodg_file_size_times_three(file_path: "str | bytes | Path") -> int:
    return fodg_file_size_bytes(file_path) * 3


def fodg_total_text_items_times_three(file_path: "str | bytes | Path") -> int:
    return fodg_total_text_items(file_path) * 3


def fodg_max_shapes_per_page_times_three(file_path: "str | bytes | Path") -> int:
    return fodg_max_shapes_per_page(file_path) * 3


def fodg_non_text_shape_count_times_three(file_path: "str | bytes | Path") -> int:
    return fodg_non_text_shape_count(file_path) * 3


def fodg_file_size_times_four(file_path: "str | bytes | Path") -> int:
    return fodg_file_size_bytes(file_path) * 4


def fodg_total_text_items_times_four(file_path: "str | bytes | Path") -> int:
    return fodg_total_text_items(file_path) * 4


def fodg_page_count_times_four(file_path: "str | bytes | Path") -> int:
    """Return page count multiplied by four."""
    return fodg_page_count(file_path) * 4


def fodg_total_shape_count_times_four(file_path: "str | bytes | Path") -> int:
    """Return total shape count multiplied by four."""
    return fodg_total_shape_count(file_path) * 4


def fodg_page_count_times_five(file_path: "str | Path") -> int:
    """Return page count multiplied by five."""
    return fodg_page_count(file_path) * 5


def fodg_total_shape_count_times_five(file_path: "str | Path") -> int:
    """Return total shape count multiplied by five."""
    return fodg_total_shape_count(file_path) * 5


def fodg_page_count_times_six(file_path: "str | Path") -> int:
    """Return page count multiplied by six."""
    return fodg_page_count(file_path) * 6


def fodg_total_shape_count_times_six(file_path: "str | Path") -> int:
    """Return total shape count multiplied by six."""
    return fodg_total_shape_count(file_path) * 6


def fodg_page_count_times_seven(file_path: "str | Path") -> int:
    """Return page count multiplied by seven."""
    return fodg_page_count(file_path) * 7


def fodg_total_shape_count_times_seven(file_path: "str | Path") -> int:
    """Return total shape count multiplied by seven."""
    return fodg_total_shape_count(file_path) * 7


def fodg_page_count_times_eight(file_path: "str | Path") -> int:
    """Return page count multiplied by eight."""
    return fodg_page_count(file_path) * 8


def fodg_total_shape_count_times_eight(file_path: "str | Path") -> int:
    """Return total shape count multiplied by eight."""
    return fodg_total_shape_count(file_path) * 8


def fodg_page_count_times_nine(file_path: "str | Path") -> int:
    """Return page count multiplied by nine."""
    return fodg_page_count(file_path) * 9


def fodg_total_shape_count_times_nine(file_path: "str | Path") -> int:
    """Return total shape count multiplied by nine."""
    return fodg_total_shape_count(file_path) * 9


def fodg_page_count_times_ten(file_path: "str | Path") -> int:
    """Return page count multiplied by ten."""
    return fodg_page_count(file_path) * 10


def fodg_total_shape_count_times_ten(file_path: "str | Path") -> int:
    """Return total shape count multiplied by ten."""
    return fodg_total_shape_count(file_path) * 10


def fodg_page_count_times_eleven(file_path: "str | Path") -> int:
    """Return page count multiplied by eleven."""
    return fodg_page_count(file_path) * 11


def fodg_total_shape_count_times_eleven(file_path: "str | Path") -> int:
    """Return total shape count multiplied by eleven."""
    return fodg_total_shape_count(file_path) * 11


def fodg_page_count_times_twelve(file_path: "str | Path") -> int:
    """Return page count multiplied by twelve."""
    return fodg_page_count(file_path) * 12


def fodg_total_shape_count_times_twelve(file_path: "str | Path") -> int:
    """Return total shape count multiplied by twelve."""
    return fodg_total_shape_count(file_path) * 12


def fodg_page_count_times_thirteen(file_path: "str | Path") -> int:
    """Return page count multiplied by thirteen."""
    return fodg_page_count(file_path) * 13


def fodg_total_shape_count_times_thirteen(file_path: "str | Path") -> int:
    """Return total shape count multiplied by thirteen."""
    return fodg_total_shape_count(file_path) * 13


def fodg_page_count_times_fourteen(file_path):
    """Return page count multiplied by fourteen."""
    return fodg_page_count(file_path) * 14


def fodg_total_shape_count_times_fourteen(file_path):
    """Return total shape count multiplied by fourteen."""
    return fodg_total_shape_count(file_path) * 14


def fodg_page_count_times_fifteen(file_path):
    """Return page count multiplied by fifteen."""
    return fodg_page_count(file_path) * 15


def fodg_total_shape_count_times_fifteen(file_path):
    """Return total shape count multiplied by fifteen."""
    return fodg_total_shape_count(file_path) * 15


def fodg_page_count_times_sixteen(file_path):
    """Return page count multiplied by sixteen."""
    return fodg_page_count(file_path) * 16


def fodg_total_shape_count_times_sixteen(file_path):
    """Return total shape count multiplied by sixteen."""
    return fodg_total_shape_count(file_path) * 16


def fodg_page_count_times_seventeen(file_path):
    """Return page count multiplied by seventeen."""
    return fodg_page_count(file_path) * 17


def fodg_total_shape_count_times_seventeen(file_path):
    """Return total shape count multiplied by seventeen."""
    return fodg_total_shape_count(file_path) * 17


def fodg_page_count_times_eighteen(file_path):
    """Return page count multiplied by eighteen."""
    return fodg_page_count(file_path) * 18


def fodg_total_shape_count_times_eighteen(file_path):
    """Return total shape count multiplied by eighteen."""
    return fodg_total_shape_count(file_path) * 18


def fodg_page_count_times_nineteen(file_path):
    """Return page count multiplied by nineteen."""
    return fodg_page_count(file_path) * 19


def fodg_total_shape_count_times_nineteen(file_path):
    """Return total shape count multiplied by nineteen."""
    return fodg_total_shape_count(file_path) * 19


def fodg_page_count_times_twenty(file_path: "str | Path") -> int:
    """Return page count multiplied by twenty."""
    return fodg_page_count(file_path) * 20


def fodg_total_shape_count_times_twenty(file_path: "str | Path") -> int:
    """Return total shape count multiplied by twenty."""
    return fodg_total_shape_count(file_path) * 20


def fodg_page_count_times_twenty_one(file_path: "str | Path") -> int:
    """Return page count multiplied by twenty-one."""
    return fodg_page_count(file_path) * 21


def fodg_total_shape_count_times_twenty_one(file_path: "str | Path") -> int:
    """Return total shape count multiplied by twenty-one."""
    return fodg_total_shape_count(file_path) * 21


def fodg_page_count_times_twenty_two(file_path: "str | Path") -> int:
    """Return page count multiplied by twenty-two."""
    return fodg_page_count(file_path) * 22


def fodg_total_shape_count_times_twenty_two(file_path: "str | Path") -> int:
    """Return total shape count multiplied by twenty-two."""
    return fodg_total_shape_count(file_path) * 22


def fodg_page_count_times_twenty_three(file_path: "str | Path") -> int:
    """Return page count multiplied by twenty-three."""
    return fodg_page_count(file_path) * 23


def fodg_total_shape_count_times_twenty_three(file_path: "str | Path") -> int:
    """Return total shape count multiplied by twenty-three."""
    return fodg_total_shape_count(file_path) * 23


def fodg_page_count_times_twenty_four(file_path: "str | Path") -> int:
    """Return page count multiplied by twenty-four."""
    return fodg_page_count(file_path) * 24


def fodg_total_shape_count_times_twenty_four(file_path: "str | Path") -> int:
    """Return total shape count multiplied by twenty-four."""
    return fodg_total_shape_count(file_path) * 24


def fodg_page_count_times_twenty_five(file_path: "str | Path") -> int:
    """Return page count multiplied by twenty-five."""
    return fodg_page_count(file_path) * 25


def fodg_total_shape_count_times_twenty_five(file_path: "str | Path") -> int:
    """Return total shape count multiplied by twenty-five."""
    return fodg_total_shape_count(file_path) * 25


def fodg_page_count_times_twenty_six(file_path: "str | Path") -> int:
    """Return page count multiplied by twenty-six."""
    return fodg_page_count(file_path) * 26


def fodg_total_shape_count_times_twenty_six(file_path: "str | Path") -> int:
    """Return total shape count multiplied by twenty-six."""
    return fodg_total_shape_count(file_path) * 26


def fodg_page_count_times_twenty_seven(file_path: "str | Path") -> int:
    """Return page count multiplied by twenty-seven."""
    return fodg_page_count(file_path) * 27


def fodg_total_shape_count_times_twenty_seven(file_path: "str | Path") -> int:
    """Return total shape count multiplied by twenty-seven."""
    return fodg_total_shape_count(file_path) * 27


def fodg_page_count_times_twenty_eight(file_path: "str | Path") -> int:
    """Return page count multiplied by twenty-eight."""
    return fodg_page_count(file_path) * 28


def fodg_total_shape_count_times_twenty_eight(file_path: "str | Path") -> int:
    """Return total shape count multiplied by twenty-eight."""
    return fodg_total_shape_count(file_path) * 28


def fodg_page_count_times_twenty_nine(file_path: "str | Path") -> int:
    """Return page count multiplied by twenty-nine."""
    return fodg_page_count(file_path) * 29


def fodg_total_shape_count_times_twenty_nine(file_path: "str | Path") -> int:
    """Return total shape count multiplied by twenty-nine."""
    return fodg_total_shape_count(file_path) * 29


def fodg_page_count_times_thirty(file_path: "str | Path") -> int:
    """Return page count multiplied by thirty."""
    return fodg_page_count(file_path) * 30


def fodg_total_shape_count_times_thirty(file_path: "str | Path") -> int:
    """Return total shape count multiplied by thirty."""
    return fodg_total_shape_count(file_path) * 30


def fodg_page_count_times_thirty_one(file_path: "str | Path") -> int:
    """Return page count multiplied by thirty-one."""
    return fodg_page_count(file_path) * 31


def fodg_total_shape_count_times_thirty_one(file_path: "str | Path") -> int:
    """Return total shape count multiplied by thirty-one."""
    return fodg_total_shape_count(file_path) * 31


def fodg_page_count_times_thirty_two(file_path: "str | Path") -> int:
    """Return page count multiplied by thirty-two."""
    return fodg_page_count(file_path) * 32


def fodg_total_shape_count_times_thirty_two(file_path: "str | Path") -> int:
    """Return total shape count multiplied by thirty-two."""
    return fodg_total_shape_count(file_path) * 32


def fodg_page_count_times_thirty_three(file_path: "str | Path") -> int:
    """Return page count multiplied by thirty-three."""
    return fodg_page_count(file_path) * 33


def fodg_total_shape_count_times_thirty_three(file_path: "str | Path") -> int:
    """Return total shape count multiplied by thirty-three."""
    return fodg_total_shape_count(file_path) * 33


def fodg_page_count_times_thirty_four(file_path: "str | Path") -> int:
    """Return page count multiplied by thirty-four."""
    return fodg_page_count(file_path) * 34


def fodg_total_shape_count_times_thirty_four(file_path: "str | Path") -> int:
    """Return total shape count multiplied by thirty-four."""
    return fodg_total_shape_count(file_path) * 34


def fodg_page_count_times_thirty_five(file_path: "str | Path") -> int:
    """Return page count multiplied by thirty-five."""
    return fodg_page_count(file_path) * 35


def fodg_total_shape_count_times_thirty_five(file_path: "str | Path") -> int:
    """Return total shape count multiplied by thirty-five."""
    return fodg_total_shape_count(file_path) * 35


def fodg_page_count_times_thirty_six(file_path: "str | Path") -> int:
    """Return page count multiplied by thirty-six."""
    return fodg_page_count(file_path) * 36


def fodg_total_shape_count_times_thirty_six(file_path: "str | Path") -> int:
    """Return total shape count multiplied by thirty-six."""
    return fodg_total_shape_count(file_path) * 36


def fodg_page_count_times_thirty_seven(file_path: "str | Path") -> int:
    """Return page count multiplied by thirty-seven."""
    return fodg_page_count(file_path) * 37


def fodg_total_shape_count_times_thirty_seven(file_path: "str | Path") -> int:
    """Return total shape count multiplied by thirty-seven."""
    return fodg_total_shape_count(file_path) * 37


def fodg_page_count_times_thirty_eight(file_path: "str | Path") -> int:
    """Return page count multiplied by thirty-eight."""
    return fodg_page_count(file_path) * 38


def fodg_total_shape_count_times_thirty_eight(file_path: "str | Path") -> int:
    """Return total shape count multiplied by thirty-eight."""
    return fodg_total_shape_count(file_path) * 38

def fodg_page_count_times_thirty_nine(file_path: "str | Path") -> int:
    """Return page count multiplied by thirty-nine."""
    return fodg_page_count(file_path) * 39

def fodg_total_shape_count_times_thirty_nine(file_path: "str | Path") -> int:
    """Return total shape count multiplied by thirty-nine."""
    return fodg_total_shape_count(file_path) * 39

def fodg_page_count_times_forty(file_path: "str | Path") -> int:
    """Return page count multiplied by forty."""
    return fodg_page_count(file_path) * 40

def fodg_total_shape_count_times_forty(file_path: "str | Path") -> int:
    """Return total shape count multiplied by forty."""
    return fodg_total_shape_count(file_path) * 40


def fodg_text_percentage(file_path: "str | Path") -> float:
    """Return percentage of text items relative to total shapes (0.0 to 100.0). 0.0 if no shapes."""
    ts = fodg_total_shape_count(file_path)
    if ts == 0:
        return 0.0
    return fodg_text_item_count(file_path) / ts * 100.0


def fodg_non_text_shape_percentage(file_path: "str | Path") -> float:
    """Return percentage of non-text shapes relative to total shapes (0.0 to 100.0). 0.0 if no shapes."""
    ts = fodg_total_shape_count(file_path)
    if ts == 0:
        return 0.0
    return fodg_non_text_shape_count(file_path) / ts * 100.0

def fodg_page_count_times_forty_one(file_path: "str | Path") -> int:
    """Return page count multiplied by forty-one."""
    return fodg_page_count(file_path) * 41

def fodg_total_shape_count_times_forty_one(file_path: "str | Path") -> int:
    """Return total shape count multiplied by forty-one."""
    return fodg_total_shape_count(file_path) * 41

def fodg_page_count_times_forty_two(file_path: "str | Path") -> int:
    """Return page count multiplied by forty-two."""
    return fodg_page_count(file_path) * 42

def fodg_total_shape_count_times_forty_two(file_path: "str | Path") -> int:
    """Return total shape count multiplied by forty-two."""
    return fodg_total_shape_count(file_path) * 42

def fodg_page_count_times_forty_three(file_path: "str | Path") -> int:
    """Return page count multiplied by forty-three."""
    return fodg_page_count(file_path) * 43

def fodg_total_shape_count_times_forty_three(file_path: "str | Path") -> int:
    """Return total shape count multiplied by forty-three."""
    return fodg_total_shape_count(file_path) * 43

def fodg_page_count_times_forty_four(file_path: "str | Path") -> int:
    """Return page count multiplied by forty-four."""
    return fodg_page_count(file_path) * 44

def fodg_total_shape_count_times_forty_four(file_path: "str | Path") -> int:
    """Return total shape count multiplied by forty-four."""
    return fodg_total_shape_count(file_path) * 44

def fodg_page_count_times_forty_five(file_path: "str | Path") -> int:
    """Return page count multiplied by forty-five."""
    return fodg_page_count(file_path) * 45

def fodg_total_shape_count_times_forty_five(file_path: "str | Path") -> int:
    """Return total shape count multiplied by forty-five."""
    return fodg_total_shape_count(file_path) * 45


def fodg_page_count_times_forty_six(file_path: "str | Path") -> int:
    """Return page count multiplied by forty-six."""
    return fodg_page_count(file_path) * 46


def fodg_total_shape_count_times_forty_six(file_path: "str | Path") -> int:
    """Return total shape count multiplied by forty-six."""
    return fodg_total_shape_count(file_path) * 46


def fodg_page_count_times_forty_seven(file_path: "str | Path") -> int:
    """Return page count multiplied by forty-seven."""
    return fodg_page_count(file_path) * 47


def fodg_total_shape_count_times_forty_seven(file_path: "str | Path") -> int:
    """Return total shape count multiplied by forty-seven."""
    return fodg_total_shape_count(file_path) * 47


def fodg_page_count_times_forty_eight(file_path: "str | Path") -> int:
    """Return page count multiplied by forty-eight."""
    return fodg_page_count(file_path) * 48


def fodg_total_shape_count_times_forty_eight(file_path: "str | Path") -> int:
    """Return total shape count multiplied by forty-eight."""
    return fodg_total_shape_count(file_path) * 48


def fodg_page_count_times_forty_nine(file_path: "str | Path") -> int:
    """Return page count multiplied by forty-nine."""
    return fodg_page_count(file_path) * 49


def fodg_total_shape_count_times_forty_nine(file_path: "str | Path") -> int:
    """Return total shape count multiplied by forty-nine."""
    return fodg_total_shape_count(file_path) * 49


def fodg_page_count_times_fifty(file_path: "str | Path") -> int:
    """Return page count multiplied by fifty."""
    return fodg_page_count(file_path) * 50


def fodg_total_shape_count_times_fifty(file_path: "str | Path") -> int:
    """Return total shape count multiplied by fifty."""
    return fodg_total_shape_count(file_path) * 50


def fodg_page_count_times_fifty_one(file_path: "str | Path") -> int:
    """Return page count multiplied by fifty-one."""
    return fodg_page_count(file_path) * 51


def fodg_total_shape_count_times_fifty_one(file_path: "str | Path") -> int:
    """Return total shape count multiplied by fifty-one."""
    return fodg_total_shape_count(file_path) * 51


def fodg_page_count_times_fifty_two(file_path: "str | Path") -> int:
    """Return page count multiplied by fifty-two."""
    return fodg_page_count(file_path) * 52


def fodg_total_shape_count_times_fifty_two(file_path: "str | Path") -> int:
    """Return total shape count multiplied by fifty-two."""
    return fodg_total_shape_count(file_path) * 52


def fodg_page_count_times_fifty_three(file_path: "str | Path") -> int:
    """Return page count multiplied by fifty-three."""
    return fodg_page_count(file_path) * 53


def fodg_total_shape_count_times_fifty_three(file_path: "str | Path") -> int:
    """Return total shape count multiplied by fifty-three."""
    return fodg_total_shape_count(file_path) * 53


def fodg_page_count_times_fifty_four(file_path: "str | Path") -> int:
    """Return page count multiplied by fifty-four."""
    return fodg_page_count(file_path) * 54


def fodg_total_shape_count_times_fifty_four(file_path: "str | Path") -> int:
    """Return total shape count multiplied by fifty-four."""
    return fodg_total_shape_count(file_path) * 54


def fodg_page_count_times_fifty_five(file_path: "str | Path") -> int:
    """Return page count multiplied by fifty-five."""
    return fodg_page_count(file_path) * 55


def fodg_total_shape_count_times_fifty_five(file_path: "str | Path") -> int:
    """Return total shape count multiplied by fifty-five."""
    return fodg_total_shape_count(file_path) * 55


def fodg_page_count_times_fifty_six(file_path: "str | Path") -> int:
    """Return page count multiplied by fifty-six."""
    return fodg_page_count(file_path) * 56


def fodg_total_shape_count_times_fifty_six(file_path: "str | Path") -> int:
    """Return total shape count multiplied by fifty-six."""
    return fodg_total_shape_count(file_path) * 56


def fodg_page_count_times_fifty_seven(file_path: "str | Path") -> int:
    """Return page count multiplied by fifty-seven."""
    return fodg_page_count(file_path) * 57


def fodg_total_shape_count_times_fifty_seven(file_path: "str | Path") -> int:
    """Return total shape count multiplied by fifty-seven."""
    return fodg_total_shape_count(file_path) * 57

def fodg_page_count_times_fifty_eight(file_path: "str | Path") -> int:
    """Return page count multiplied by fifty-eight."""
    return fodg_page_count(file_path) * 58

def fodg_total_shape_count_times_fifty_eight(file_path: "str | Path") -> int:
    """Return total shape count multiplied by fifty-eight."""
    return fodg_total_shape_count(file_path) * 58

def fodg_page_count_times_fifty_nine(file_path: "str | Path") -> int:
    """Return page count multiplied by fifty-nine."""
    return fodg_page_count(file_path) * 59

def fodg_total_shape_count_times_fifty_nine(file_path: "str | Path") -> int:
    """Return total shape count multiplied by fifty-nine."""
    return fodg_total_shape_count(file_path) * 59

def fodg_page_count_times_sixty(file_path: "str | Path") -> int:
    """Return page count multiplied by sixty."""
    return fodg_page_count(file_path) * 60

def fodg_total_shape_count_times_sixty(file_path: "str | Path") -> int:
    """Return total shape count multiplied by sixty."""
    return fodg_total_shape_count(file_path) * 60

def fodg_page_count_times_sixty_one(file_path: "str | Path") -> int:
    """Return page count multiplied by sixty-one."""
    return fodg_page_count(file_path) * 61

def fodg_total_shape_count_times_sixty_one(file_path: "str | Path") -> int:
    """Return total shape count multiplied by sixty-one."""
    return fodg_total_shape_count(file_path) * 61

def fodg_page_count_times_sixty_two(file_path: "str | Path") -> int:
    """Return page count multiplied by sixty-two."""
    return fodg_page_count(file_path) * 62

def fodg_total_shape_count_times_sixty_two(file_path: "str | Path") -> int:
    """Return total shape count multiplied by sixty-two."""
    return fodg_total_shape_count(file_path) * 62

def fodg_page_count_times_sixty_three(file_path: "str | Path") -> int:
    """Return page count multiplied by sixty-three."""
    return fodg_page_count(file_path) * 63

def fodg_total_shape_count_times_sixty_three(file_path: "str | Path") -> int:
    """Return total shape count multiplied by sixty-three."""
    return fodg_total_shape_count(file_path) * 63

def fodg_page_count_times_sixty_four(file_path: "str | Path") -> int:
    """Return page count multiplied by sixty-four."""
    return fodg_page_count(file_path) * 64

def fodg_total_shape_count_times_sixty_four(file_path: "str | Path") -> int:
    """Return total shape count multiplied by sixty-four."""
    return fodg_total_shape_count(file_path) * 64

def fodg_page_count_times_sixty_five(file_path: "str | Path") -> int:
    """Return page count multiplied by sixty-five."""
    return fodg_page_count(file_path) * 65

def fodg_total_shape_count_times_sixty_five(file_path: "str | Path") -> int:
    """Return total shape count multiplied by sixty-five."""
    return fodg_total_shape_count(file_path) * 65

def fodg_page_count_times_sixty_six(file_path: "str | Path") -> int:
    """Return page count multiplied by sixty-six."""
    return fodg_page_count(file_path) * 66

def fodg_total_shape_count_times_sixty_six(file_path: "str | Path") -> int:
    """Return total shape count multiplied by sixty-six."""
    return fodg_total_shape_count(file_path) * 66

def fodg_page_count_times_sixty_seven(file_path: "str | Path") -> int:
    """Return page count multiplied by sixty-seven."""
    return fodg_page_count(file_path) * 67

def fodg_total_shape_count_times_sixty_seven(file_path: "str | Path") -> int:
    """Return total shape count multiplied by sixty-seven."""
    return fodg_total_shape_count(file_path) * 67

def fodg_page_count_times_sixty_eight(file_path: "str | Path") -> int:
    """Return page count multiplied by sixty-eight."""
    return fodg_page_count(file_path) * 68

def fodg_total_shape_count_times_sixty_eight(file_path: "str | Path") -> int:
    """Return total shape count multiplied by sixty-eight."""
    return fodg_total_shape_count(file_path) * 68





def fodg_page_count_times_sixty_nine(file_path: "str | Path") -> int:
    """Return page count multiplied by sixty-nine."""
    return fodg_page_count(file_path) * 69

def fodg_total_shape_count_times_sixty_nine(file_path: "str | Path") -> int:
    """Return total shape count multiplied by sixty-nine."""
    return fodg_total_shape_count(file_path) * 69





def fodg_page_count_times_seventy(file_path: "str | Path") -> int:
    """Return page count multiplied by seventy."""
    return fodg_page_count(file_path) * 70

def fodg_total_shape_count_times_seventy(file_path: "str | Path") -> int:
    """Return total shape count multiplied by seventy."""
    return fodg_total_shape_count(file_path) * 70

def fodg_page_count_times_seventy_one(file_path: "str | Path") -> int:
    """Return page count multiplied by seventy-one."""
    return fodg_page_count(file_path) * 71

def fodg_total_shape_count_times_seventy_one(file_path: "str | Path") -> int:
    """Return total shape count multiplied by seventy-one."""
    return fodg_total_shape_count(file_path) * 71


def fodg_page_count_times_seventy_two(file_path: "str | Path") -> int:
    """Return page count multiplied by seventy-two."""
    return fodg_page_count(file_path) * 72


def fodg_total_shape_count_times_seventy_two(file_path: "str | Path") -> int:
    """Return total shape count multiplied by seventy-two."""
    return fodg_total_shape_count(file_path) * 72


def fodg_page_count_times_seventy_three(file_path: "str | Path") -> int:
    """Return page count multiplied by seventy-three."""
    return fodg_page_count(file_path) * 73


def fodg_total_shape_count_times_seventy_three(file_path: "str | Path") -> int:
    """Return total shape count multiplied by seventy-three."""
    return fodg_total_shape_count(file_path) * 73


def fodg_page_count_times_seventy_four(file_path: "str | Path") -> int:
    """Return page count multiplied by seventy-four."""
    return fodg_page_count(file_path) * 74


def fodg_total_shape_count_times_seventy_four(file_path: "str | Path") -> int:
    """Return total shape count multiplied by seventy-four."""
    return fodg_total_shape_count(file_path) * 74


def fodg_page_count_times_seventy_five(file_path: "str | Path") -> int:
    """Return page count multiplied by seventy-five."""
    return fodg_page_count(file_path) * 75


def fodg_total_shape_count_times_seventy_five(file_path: "str | Path") -> int:
    """Return total shape count multiplied by seventy-five."""
    return fodg_total_shape_count(file_path) * 75


def fodg_bytes_per_shape(file_path: "str | Path") -> float:
    """Return file size divided by total shape count. 0.0 if no shapes."""
    sc = fodg_total_shape_count(file_path)
    if sc == 0:
        return 0.0
    return fodg_file_size_bytes(file_path) / sc


def fodg_text_to_shape_ratio(file_path: "str | Path") -> float:
    """Return text item count divided by total shape count. 0.0 if no shapes."""
    sc = fodg_total_shape_count(file_path)
    if sc == 0:
        return 0.0
    return fodg_text_item_count(file_path) / sc


def fodg_page_count_times_seventy_six(file_path: "str | Path") -> int:
    """Return page count multiplied by seventy-six."""
    return fodg_page_count(file_path) * 76


def fodg_total_shape_count_times_seventy_six(file_path: "str | Path") -> int:
    """Return total shape count multiplied by seventy-six."""
    return fodg_total_shape_count(file_path) * 76


def fodg_page_count_times_seventy_seven(file_path: "str | Path") -> int:
    """Return page count multiplied by seventy-seven."""
    return fodg_page_count(file_path) * 77


def fodg_total_shape_count_times_seventy_seven(file_path: "str | Path") -> int:
    """Return total shape count multiplied by seventy-seven."""
    return fodg_total_shape_count(file_path) * 77


def fodg_page_count_times_seventy_eight(file_path: "str | Path") -> int:
    """Return page count multiplied by seventy-eight."""
    return fodg_page_count(file_path) * 78


def fodg_total_shape_count_times_seventy_eight(file_path: "str | Path") -> int:
    """Return total shape count multiplied by seventy-eight."""
    return fodg_total_shape_count(file_path) * 78





def fodg_page_count_times_seventy_nine(file_path: "str | Path") -> int:
    """Return page count multiplied by seventy-nine."""
    return fodg_page_count(file_path) * 79

def fodg_total_shape_count_times_seventy_nine(file_path: "str | Path") -> int:
    """Return total shape count multiplied by seventy-nine."""
    return fodg_total_shape_count(file_path) * 79

def fodg_page_count_times_eighty(file_path: "str | Path") -> int:
    """Return page count multiplied by eighty."""
    return fodg_page_count(file_path) * 80

def fodg_total_shape_count_times_eighty(file_path: "str | Path") -> int:
    """Return total shape count multiplied by eighty."""
    return fodg_total_shape_count(file_path) * 80

def fodg_page_count_times_eighty_one(file_path: "str | Path") -> int:
    """Return page count multiplied by eighty-one."""
    return fodg_page_count(file_path) * 81

def fodg_total_shape_count_times_eighty_one(file_path: "str | Path") -> int:
    """Return total shape count multiplied by eighty-one."""
    return fodg_total_shape_count(file_path) * 81

def fodg_page_count_times_eighty_two(file_path: "str | Path") -> int:
    """Return page count multiplied by eighty-two."""
    return fodg_page_count(file_path) * 82

def fodg_total_shape_count_times_eighty_two(file_path: "str | Path") -> int:
    """Return total shape count multiplied by eighty-two."""
    return fodg_total_shape_count(file_path) * 82

def fodg_page_count_times_eighty_three(file_path: "str | Path") -> int:
    """Return page count multiplied by eighty-three."""
    return fodg_page_count(file_path) * 83

def fodg_total_shape_count_times_eighty_three(file_path: "str | Path") -> int:
    """Return total shape count multiplied by eighty-three."""
    return fodg_total_shape_count(file_path) * 83

def fodg_page_count_times_eighty_four(file_path: "str | Path") -> int:
    """Return page count multiplied by eighty-four."""
    return fodg_page_count(file_path) * 84

def fodg_total_shape_count_times_eighty_four(file_path: "str | Path") -> int:
    """Return total shape count multiplied by eighty-four."""
    return fodg_total_shape_count(file_path) * 84





def fodg_page_count_times_eighty_five(file_path: "str | Path") -> int:
    """Return page count multiplied by eighty-five."""
    return fodg_page_count(file_path) * 85

def fodg_total_shape_count_times_eighty_five(file_path: "str | Path") -> int:
    """Return total shape count multiplied by eighty-five."""
    return fodg_total_shape_count(file_path) * 85





def fodg_page_count_times_eighty_six(file_path: "str | Path") -> int:
    """Return page count multiplied by eighty-six."""
    return fodg_page_count(file_path) * 86

def fodg_total_shape_count_times_eighty_six(file_path: "str | Path") -> int:
    """Return total shape count multiplied by eighty-six."""
    return fodg_total_shape_count(file_path) * 86


def fodg_text_per_page(file_path: "str | Path") -> float:
    """Return text item count divided by page count. 0.0 if no pages."""
    pc = fodg_page_count(file_path)
    if pc == 0:
        return 0.0
    return fodg_text_item_count(file_path) / pc


def fodg_is_text_heavy(file_path: "str | Path") -> bool:
    """Return True if text items exceed half of total shapes."""
    sc = fodg_total_shape_count(file_path)
    if sc == 0:
        return False
    return fodg_text_item_count(file_path) > sc / 2

def fodg_page_count_times_eighty_seven(file_path: "str | Path") -> int:
    """Return page count multiplied by eighty-seven."""
    return fodg_page_count(file_path) * 87

def fodg_total_shape_count_times_eighty_seven(file_path: "str | Path") -> int:
    """Return total shape count multiplied by eighty-seven."""
    return fodg_total_shape_count(file_path) * 87






























def fodg_shape_count_times_eighty_nine(file_path: "str | Path") -> int:
    """Return total shape count multiplied by eighty-nine."""
    return fodg_total_shape_count(file_path) * 89


def fodg_text_count_times_eighty_nine(file_path: "str | Path") -> int:
    """Return text item count multiplied by eighty-nine."""
    return fodg_text_item_count(file_path) * 89






























def fodg_shape_count_times_ninety(file_path: "str | Path") -> int:
    """Return total shape count multiplied by ninety."""
    return fodg_total_shape_count(file_path) * 90


def fodg_text_count_times_ninety(file_path: "str | Path") -> int:
    """Return text item count multiplied by ninety."""
    return fodg_text_item_count(file_path) * 90










def fodg_shape_count_times_ninety_one(file_path: "str | Path") -> int:
    """Return total shape count multiplied by ninety-one."""
    return fodg_total_shape_count(file_path) * 91


def fodg_text_count_times_ninety_one(file_path: "str | Path") -> int:
    """Return text item count multiplied by ninety-one."""
    return fodg_text_item_count(file_path) * 91


def fodg_shape_count_times_ninety_two(file_path: "str | Path") -> int:
    """Return total shape count multiplied by ninety-two."""
    return fodg_total_shape_count(file_path) * 92


def fodg_text_count_times_ninety_two(file_path: "str | Path") -> int:
    """Return text item count multiplied by ninety-two."""
    return fodg_text_item_count(file_path) * 92














def fodg_shape_count_times_ninety_three(file_path: "str | Path") -> int:
    """Return total shape count multiplied by ninety-three."""
    return fodg_total_shape_count(file_path) * 93


def fodg_text_count_times_ninety_three(file_path: "str | Path") -> int:
    """Return text item count multiplied by ninety-three."""
    return fodg_text_item_count(file_path) * 93










def fodg_shape_count_times_ninety_four(file_path: "str | Path") -> int:
    """Return total shape count multiplied by ninety-four."""
    return fodg_total_shape_count(file_path) * 94


def fodg_text_count_times_ninety_four(file_path: "str | Path") -> int:
    """Return text item count multiplied by ninety-four."""
    return fodg_text_item_count(file_path) * 94














def fodg_shape_count_times_ninety_five(file_path: "str | Path") -> int:
    """Return total shape count multiplied by ninety-five."""
    return fodg_total_shape_count(file_path) * 95


def fodg_text_count_times_ninety_five(file_path: "str | Path") -> int:
    """Return text item count multiplied by ninety-five."""
    return fodg_text_item_count(file_path) * 95






def fodg_shape_count_times_ninety_six(file_path: "str | Path") -> int:
    """Return total shape count multiplied by ninety-six."""
    return fodg_total_shape_count(file_path) * 96


def fodg_text_count_times_ninety_six(file_path: "str | Path") -> int:
    """Return text item count multiplied by ninety-six."""
    return fodg_text_item_count(file_path) * 96














def fodg_shape_count_times_ninety_seven(file_path: "str | Path") -> int:
    """Return total shape count multiplied by ninety-seven."""
    return fodg_total_shape_count(file_path) * 97


def fodg_text_count_times_ninety_seven(file_path: "str | Path") -> int:
    """Return text item count multiplied by ninety-seven."""
    return fodg_text_item_count(file_path) * 97






def fodg_shape_count_times_ninety_eight(file_path: "str | Path") -> int:
    """Return total shape count multiplied by ninety-eight."""
    return fodg_total_shape_count(file_path) * 98


def fodg_text_count_times_ninety_eight(file_path: "str | Path") -> int:
    """Return text item count multiplied by ninety-eight."""
    return fodg_text_item_count(file_path) * 98










def fodg_shape_count_times_ninety_nine(file_path: "str | Path") -> int:
    """Return total shape count multiplied by ninety-nine."""
    return fodg_total_shape_count(file_path) * 99


def fodg_text_count_times_ninety_nine(file_path: "str | Path") -> int:
    """Return text item count multiplied by ninety-nine."""
    return fodg_text_item_count(file_path) * 99














def fodg_shape_count_times_one_hundred(file_path: "str | Path") -> int:
    """Return total shape count multiplied by one hundred."""
    return fodg_total_shape_count(file_path) * 100


def fodg_text_count_times_one_hundred(file_path: "str | Path") -> int:
    """Return text item count multiplied by one hundred."""
    return fodg_text_item_count(file_path) * 100














def fodg_shape_count_times_one_hundred_and_one(file_path: "str | Path") -> int:
    """Return total shape count multiplied by one hundred and one."""
    return fodg_total_shape_count(file_path) * 101


def fodg_text_count_times_one_hundred_and_one(file_path: "str | Path") -> int:
    """Return text item count multiplied by one hundred and one."""
    return fodg_text_item_count(file_path) * 101














def fodg_shape_count_times_one_hundred_and_two(file_path: "str | Path") -> int:
    """Return total shape count multiplied by one hundred and two."""
    return fodg_total_shape_count(file_path) * 102


def fodg_text_count_times_one_hundred_and_two(file_path: "str | Path") -> int:
    """Return text item count multiplied by one hundred and two."""
    return fodg_text_item_count(file_path) * 102










def fodg_shape_count_times_one_hundred_and_three(file_path: "str | Path") -> int:
    """Return total shape count multiplied by one hundred and three."""
    return fodg_total_shape_count(file_path) * 103


def fodg_text_count_times_one_hundred_and_three(file_path: "str | Path") -> int:
    """Return text item count multiplied by one hundred and three."""
    return fodg_text_item_count(file_path) * 103
