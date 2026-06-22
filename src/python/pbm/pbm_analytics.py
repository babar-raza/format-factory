"""
PBM analytics functions extracted from pbm_parser.py (TC-HEAL-FORMATS-BATCH2).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .pbm_parser import (
    PbmError,
    parse_pbm_strict,
    black_pixel_ratio,
    image_pixel_stats,
    pixel_count,
    get_dimensions,
)


def pbm_white_pixel_ratio(file_path: "str | Path") -> float:
    """Return the fraction of white pixels (0-values) in a PBM image.

    In PBM format, 0 = white and 1 = black.

    Args:
        file_path: Path to a PBM image file.

    Returns:
        Float in [0.0, 1.0] representing fraction of white pixels.
        Returns 0.0 for empty images.

    Raises:
        PbmError: If the file cannot be parsed.
    """
    return 1.0 - black_pixel_ratio(file_path)


def pbm_aspect_ratio(file_path: "str | Path") -> float:
    """Return the aspect ratio (width / height) of a PBM image.

    Args:
        file_path: Path to a PBM image file.

    Returns:
        Float representing width divided by height.
        Returns 0.0 for images with zero height.

    Raises:
        PbmError: If the file cannot be parsed.
    """
    img = parse_pbm_strict(file_path)
    if img.height == 0:
        return 0.0
    return img.width / img.height


def pbm_white_pixel_count(file_path: "str | Path") -> int:
    """Return the count of white pixels (value 0) in a PBM image.

    In PBM format, 0 = white and 1 = black.

    Args:
        file_path: Path to a PBM file.

    Returns:
        Integer count of white pixels. Returns 0 for all-black images.

    Raises:
        PbmError: If the file cannot be parsed.
    """
    img = parse_pbm_strict(file_path)
    return sum(1 for p in img.pixels if p == 0)


def pbm_row_black_counts(file_path: "str | Path") -> list[int]:
    """Return a list of per-row black pixel counts for a PBM image.

    For a PBM image with height H, returns a list of H integers where each
    element is the count of black pixels (value 1) in that row. Useful for
    detecting horizontal patterns, text lines, or image structure.

    Args:
        file_path: Path to a PBM file.

    Returns:
        List of integers, one per row, each being the black pixel count.

    Raises:
        PbmError: If the file cannot be parsed.
    """
    img = parse_pbm_strict(file_path)
    counts: list[int] = []
    for row in range(img.height):
        start = row * img.width
        end = start + img.width
        counts.append(sum(1 for p in img.pixels[start:end] if p == 1))
    return counts


def pbm_total_pixel_count(file_path: "str | Path") -> int:
    """Return the total number of pixels in a PBM image (width * height).

    Args:
        file_path: Path to a PBM file.

    Returns:
        Integer total pixel count.

    Raises:
        PbmError: If the file cannot be parsed.
    """
    img = parse_pbm_strict(file_path)
    return img.width * img.height


def pbm_is_binary(file_path: "str | Path") -> bool:
    """Return True if the PBM file uses binary P4 format, False if ASCII P1.

    Args:
        file_path: Path to a PBM file.

    Returns:
        True for P4 (binary), False for P1 (ASCII).

    Raises:
        PbmError: If the file cannot be parsed or has an unrecognized magic.
    """
    p = Path(file_path)
    data = p.read_bytes()
    magic = data[:2]
    if magic == b"P4":
        return True
    if magic == b"P1":
        return False
    raise PbmError(f"Unrecognized PBM magic: {magic!r}")


def pbm_black_pixel_ratio(file_path: "str | Path") -> float:
    """Return the ratio of black pixels to total pixels. 0.0 if no pixels."""
    img = parse_pbm_strict(file_path)
    total = img.width * img.height
    if total == 0:
        return 0.0
    stats = image_pixel_stats(file_path)
    return stats["black_count"] / total


def pbm_dimensions(file_path: "str | Path") -> dict:
    """Return width and height of the PBM image as a dict."""
    img = parse_pbm_strict(file_path)
    return {"width": img.width, "height": img.height}


def pbm_column_black_counts(file_path: "str | Path") -> list[int]:
    """Return the number of black pixels in each column."""
    img = parse_pbm_strict(file_path)
    if not img.pixels or img.width == 0:
        return []
    counts = [0] * img.width
    for y in range(img.height):
        for x in range(img.width):
            if img.pixels[y * img.width + x] == 1:
                counts[x] += 1
    return counts


def pbm_white_density(file_path: "str | Path") -> float:
    """Return the ratio of white pixels to total pixels. 0.0 if no pixels."""
    img = parse_pbm_strict(file_path)
    if not img.pixels:
        return 0.0
    white = sum(1 for p in img.pixels if p == 0)
    return white / len(img.pixels)


def pbm_all_white(file_path: "str | Path") -> bool:
    """Return True if all pixels are white (value 0).

    Args:
        file_path: Path to a PBM file.

    Returns:
        True if image has pixels and all are white, False otherwise.
    """
    img = parse_pbm_strict(file_path)
    if not img.pixels:
        return False
    return all(p == 0 for p in img.pixels)


def pbm_all_black(file_path: "str | Path") -> bool:
    """Return True if all pixels are black (value 1).

    Args:
        file_path: Path to a PBM file.

    Returns:
        True if image has pixels and all are black, False otherwise.
    """
    img = parse_pbm_strict(file_path)
    if not img.pixels:
        return False
    return all(p == 1 for p in img.pixels)


def pbm_row_count(file_path: "str | Path") -> int:
    """Return the number of rows (height) in the PBM image."""
    img = parse_pbm_strict(file_path)
    return img.height


def pbm_has_any_black(file_path: "str | Path") -> bool:
    """Return True if at least one pixel is black (value 1)."""
    img = parse_pbm_strict(file_path)
    return any(p == 1 for p in img.pixels)


def pbm_black_pixel_count(file_path: "str | Path") -> int:
    """Return the count of black pixels (value 1) in a PBM image.

    Args:
        file_path: Path to a PBM file.

    Returns:
        Integer count of black (value 1) pixels.
    """
    img = parse_pbm_strict(file_path)
    return sum(1 for p in img.pixels if p == 1)


def pbm_is_uniform(file_path: "str | Path") -> bool:
    """Return True if all pixels have the same value.

    Args:
        file_path: Path to a PBM file.

    Returns:
        True if all pixels are the same (all black or all white).
        Returns True for empty images (vacuously uniform).
    """
    img = parse_pbm_strict(file_path)
    if not img.pixels:
        return True
    first = img.pixels[0]
    return all(p == first for p in img.pixels)




def pbm_perimeter(file_path: "str | Path") -> int:
    """Return the image perimeter in pixels: 2 * (width + height)."""
    img = parse_pbm_strict(file_path)
    return 2 * (img.width + img.height)


def pbm_is_square(file_path: "str | Path") -> bool:
    """Return True if the PBM image width equals its height."""
    img = parse_pbm_strict(file_path)
    return img.width == img.height


def pbm_is_landscape(file_path: "str | Path") -> bool:
    """Return True if the PBM image is wider than it is tall."""
    img = parse_pbm_strict(file_path)
    return img.width > img.height


def pbm_has_any_white(file_path: "str | Path") -> bool:
    """Return True if at least one pixel is white (value 0)."""
    img = parse_pbm_strict(file_path)
    return any(p == 0 for p in img.pixels)


def pbm_max_row_black_count(file_path: "str | Path") -> int:
    """Return the maximum number of black pixels in any single row."""
    img = parse_pbm_strict(file_path)
    if not img.pixels or img.height == 0:
        return 0
    max_count = 0
    for row in range(img.height):
        start = row * img.width
        end = start + img.width
        count = sum(1 for p in img.pixels[start:end] if p == 1)
        if count > max_count:
            max_count = count
    return max_count


def pbm_max_dimension(file_path: "str | Path") -> int:
    """Return the larger of width and height."""
    img = parse_pbm_strict(file_path)
    return max(img.width, img.height)


def pbm_diagonal(file_path: "str | Path") -> float:
    """Return the diagonal length of the image."""
    import math
    img = parse_pbm_strict(file_path)
    return math.sqrt(img.width ** 2 + img.height ** 2)


def pbm_min_dimension(file_path: "str | Path") -> int:
    """Return the smaller of width and height."""
    img = parse_pbm_strict(file_path)
    return min(img.width, img.height)


def pbm_black_density(file_path: "str | Path") -> float:
    """Return the ratio of black pixels to total pixels. 0.0 if no pixels."""
    img = parse_pbm_strict(file_path)
    total = len(img.pixels)
    if total == 0:
        return 0.0
    black = sum(1 for p in img.pixels if p == 1)
    return black / total


def pbm_area(file_path: "str | Path") -> int:
    """Return the area of the image: width * height."""
    img = parse_pbm_strict(file_path)
    return img.width * img.height




def pbm_column_count(file_path: "str | Path") -> int:
    """Return the number of columns (width) in the image."""
    img = parse_pbm_strict(file_path)
    return img.width


def pbm_min_row_black_count(file_path: "str | Path") -> int:
    """Return the minimum number of black pixels in any row. 0 if no rows."""
    img = parse_pbm_strict(file_path)
    if img.height == 0 or img.width == 0:
        return 0
    rows = [img.pixels[i * img.width:(i + 1) * img.width] for i in range(img.height)]
    return min(sum(row) for row in rows)


def pbm_dimension_ratio(file_path: "str | Path") -> float:
    """Return width / height. 0.0 if height is 0."""
    img = parse_pbm_strict(file_path)
    if img.height == 0:
        return 0.0
    return img.width / img.height


def pbm_megapixels(file_path: "str | Path") -> float:
    """Return image size in megapixels."""
    img = parse_pbm_strict(file_path)
    return (img.width * img.height) / 1_000_000


def pbm_is_tall(file_path: "str | Path") -> bool:
    """Return True if height > 2 * width."""
    img = parse_pbm_strict(file_path)
    return img.height > 2 * img.width


def pbm_is_wide(file_path: "str | Path") -> bool:
    """Return True if width > 2 * height."""
    img = parse_pbm_strict(file_path)
    return img.width > 2 * img.height


def pbm_is_portrait(file_path: "str | Path") -> bool:
    """Return True if height > width."""
    img = parse_pbm_strict(file_path)
    return img.height > img.width


def pbm_pixel_density(file_path: "str | Path") -> float:
    """Return pixels per byte of file size. 0.0 if file_size is 0."""
    img = parse_pbm_strict(file_path)
    fsize = Path(file_path).stat().st_size
    if fsize == 0:
        return 0.0
    return (img.width * img.height) / fsize




def pbm_is_binary_balanced(file_path: "str | Path") -> bool:
    """Return True if black pixel count equals white pixel count."""
    img = parse_pbm_strict(file_path)
    black = sum(1 for p in img.pixels if p == 1)
    white = sum(1 for p in img.pixels if p == 0)
    return black == white


def pbm_avg_row_density(file_path: "str | Path") -> float:
    """Return average black-pixel density per row. 0.0 if no pixels."""
    img = parse_pbm_strict(file_path)
    if img.width == 0 or img.height == 0:
        return 0.0
    total_density = 0.0
    for r in range(img.height):
        row_start = r * img.width
        row_pixels = img.pixels[row_start:row_start + img.width]
        total_density += sum(1 for p in row_pixels if p == 1) / img.width
    return total_density / img.height


def pbm_border_black_count(file_path: "str | Path") -> int:
    """Return the number of black pixels on the image border (edges)."""
    img = parse_pbm_strict(file_path)
    if img.width == 0 or img.height == 0:
        return 0
    border = set()
    for x in range(img.width):
        border.add(x)
        border.add((img.height - 1) * img.width + x)
    for y in range(img.height):
        border.add(y * img.width)
        border.add(y * img.width + img.width - 1)
    return sum(1 for idx in border if img.pixels[idx] == 1)


def pbm_row_density_variance(file_path: "str | Path") -> float:
    """Return variance of black-pixel density across rows. 0.0 if fewer than 2 rows."""
    img = parse_pbm_strict(file_path)
    if img.width == 0 or img.height < 2:
        return 0.0
    densities = []
    for r in range(img.height):
        row_start = r * img.width
        row_pixels = img.pixels[row_start:row_start + img.width]
        densities.append(sum(1 for p in row_pixels if p == 1) / img.width)
    mean = sum(densities) / len(densities)
    return sum((d - mean) ** 2 for d in densities) / len(densities)


def pbm_is_checkerboard(file_path: "str | Path") -> bool:
    """Return True if the image follows a checkerboard pattern (alternating 0/1)."""
    img = parse_pbm_strict(file_path)
    if img.width == 0 or img.height == 0:
        return False
    for r in range(img.height):
        for c in range(img.width):
            expected = (r + c) % 2
            if img.pixels[r * img.width + c] != expected:
                return False
    return True


def pbm_column_density_variance(file_path: "str | Path") -> float:
    """Return variance of black-pixel density across columns. 0.0 if fewer than 2 columns."""
    img = parse_pbm_strict(file_path)
    if img.height == 0 or img.width < 2:
        return 0.0
    densities = []
    for c in range(img.width):
        col_black = sum(1 for r in range(img.height) if img.pixels[r * img.width + c] == 1)
        densities.append(col_black / img.height)
    mean = sum(densities) / len(densities)
    return sum((d - mean) ** 2 for d in densities) / len(densities)


def pbm_diagonal_pixel_count(file_path: "str | Path") -> int:
    """Return count of black pixels on the main diagonal. 0 if empty."""
    img = parse_pbm_strict(file_path)
    if img.width == 0 or img.height == 0:
        return 0
    diag_len = min(img.width, img.height)
    return sum(1 for i in range(diag_len) if img.pixels[i * img.width + i] == 1)


def pbm_total_pixels(file_path: "str | Path") -> int:
    """Return total pixel count (width * height)."""
    img = parse_pbm_strict(file_path)
    return img.width * img.height








def pbm_is_all_black(file_path: "str | Path") -> bool:
    """Return True if all pixels are black (1)."""
    img = parse_pbm_strict(file_path)
    return all(p == 1 for p in img.pixels)


def pbm_total_black_in_border(file_path: "str | Path") -> int:
    """Return count of black pixels on the border (first/last row/column)."""
    img = parse_pbm_strict(file_path)
    if img.width == 0 or img.height == 0:
        return 0
    count = 0
    for i, p in enumerate(img.pixels):
        r = i // img.width
        c = i % img.width
        if (r == 0 or r == img.height - 1 or c == 0 or c == img.width - 1) and p == 1:
            count += 1
    return count


def pbm_center_black_ratio(file_path: "str | Path") -> float:
    """Return ratio of black pixels in the center quarter to total center pixels. 0.0 if too small."""
    img = parse_pbm_strict(file_path)
    if img.width < 4 or img.height < 4:
        return 0.0
    r1, r2 = img.height // 4, 3 * img.height // 4
    c1, c2 = img.width // 4, 3 * img.width // 4
    total = 0
    black = 0
    for r in range(r1, r2):
        for c in range(c1, c2):
            total += 1
            if img.pixels[r * img.width + c] == 1:
                black += 1
    if total == 0:
        return 0.0
    return black / total

