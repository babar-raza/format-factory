"""
PPM analytics functions extracted from ppm_parser.py (TC-HEAL-FORMATS-BATCH2).
"""
from __future__ import annotations


spec_qname = "ppm:image"
spec_fact_ref = "FACT-PPM-001"
namespace_uri = "urn:netpbm:portable-pixmap"

from pathlib import Path

from .ppm_parser import (
    PpmError,
    parse_ppm_strict,
)


def ppm_red_channel_average(file_path: str | Path) -> float:
    """Return the average value of the red channel across all pixels.

    Args:
        file_path: Path to a PPM file.

    Returns:
        Float average red channel value. Returns 0.0 for empty images.

    Raises:
        PpmError: If the file cannot be parsed.
    """
    img = parse_ppm_strict(file_path)
    if not img.pixels:
        return 0.0
    return sum(p[0] for p in img.pixels) / len(img.pixels)


def ppm_green_channel_average(file_path: str | Path) -> float:
    """Return the average value of the green channel across all pixels.

    Args:
        file_path: Path to a PPM file.

    Returns:
        Float average green channel value. Returns 0.0 for empty images.

    Raises:
        PpmError: If the file cannot be parsed.
    """
    img = parse_ppm_strict(file_path)
    if not img.pixels:
        return 0.0
    return sum(p[1] for p in img.pixels) / len(img.pixels)


def ppm_unique_color_count(file_path: str | Path) -> int:
    """Return the number of unique RGB color tuples in the image.

    Args:
        file_path: Path to a PPM file.

    Returns:
        Integer count of distinct (R, G, B) color tuples. Returns 0 for empty images.

    Raises:
        PpmError: If the file cannot be parsed.
    """
    img = parse_ppm_strict(file_path)
    return len(set(img.pixels))


def ppm_pixel_count(file_path: str | Path) -> int:
    """Return the total number of pixels in a PPM image (width * height).

    Args:
        file_path: Path to a PPM file.

    Returns:
        Integer pixel count. Returns 0 for empty images.

    Raises:
        PpmError: If the file cannot be parsed.
    """
    img = parse_ppm_strict(file_path)
    return len(img.pixels)


def ppm_brightness_variance(file_path: str | Path) -> float:
    """Return the variance of per-pixel brightness (mean of R, G, B) across the image.

    Args:
        file_path: Path to a PPM file.

    Returns:
        Float variance of brightness values. Returns 0.0 for single-pixel or empty images.

    Raises:
        PpmError: If the file cannot be parsed.
    """
    img = parse_ppm_strict(file_path)
    if not img.pixels:
        return 0.0
    brightnesses = [sum(p) / 3.0 for p in img.pixels]
    avg = sum(brightnesses) / len(brightnesses)
    return sum((b - avg) ** 2 for b in brightnesses) / len(brightnesses)


def ppm_is_binary(file_path: str | Path) -> bool:
    """Return True if the PPM file uses binary P6 format, False if ASCII P3.

    Args:
        file_path: Path to a PPM file.

    Returns:
        True for P6 (binary), False for P3 (ASCII).

    Raises:
        PpmError: If the file cannot be parsed or has an unrecognized magic.
    """
    p = Path(file_path)
    data = p.read_bytes()
    magic = data[:2]
    if magic == b"P6":
        return True
    if magic == b"P3":
        return False
    raise PpmError(f"Unrecognized PPM magic: {magic!r}")


def ppm_aspect_ratio(file_path: str | Path) -> float:
    """Return the aspect ratio (width / height) of a PPM image.

    Args:
        file_path: Path to a PPM file.

    Returns:
        Float aspect ratio. Returns 0.0 if height is 0.

    Raises:
        PpmError: If the file cannot be parsed.
    """
    img = parse_ppm_strict(file_path)
    if img.height == 0:
        return 0.0
    return img.width / img.height


def ppm_dominant_channel(file_path: str | Path) -> str:
    """Return the dominant color channel ('red', 'green', or 'blue') of a PPM image.

    The dominant channel is the one with the highest sum of pixel values.

    Args:
        file_path: Path to a PPM file.

    Returns:
        String 'red', 'green', or 'blue'. Returns 'red' for empty images (tie-break).

    Raises:
        PpmError: If the file cannot be parsed.
    """
    img = parse_ppm_strict(file_path)
    if not img.pixels:
        return "red"
    r_sum = sum(p[0] for p in img.pixels)
    g_sum = sum(p[1] for p in img.pixels)
    b_sum = sum(p[2] for p in img.pixels)
    if r_sum >= g_sum and r_sum >= b_sum:
        return "red"
    if g_sum >= b_sum:
        return "green"
    return "blue"


def ppm_min_max_brightness(file_path: str | Path) -> dict[str, float]:
    """Return the min and max pixel brightness of a PPM image.

    Brightness is computed as 0.299*R + 0.587*G + 0.114*B (ITU-R BT.601).

    Args:
        file_path: Path to a PPM file.

    Returns:
        Dict with 'min' and 'max' float values. Returns {'min': 0.0, 'max': 0.0}
        for empty images.

    Raises:
        PpmError: If the file cannot be parsed.
    """
    img = parse_ppm_strict(file_path)
    if not img.pixels:
        return {"min": 0.0, "max": 0.0}
    brightnesses = [0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2] for p in img.pixels]
    return {"min": min(brightnesses), "max": max(brightnesses)}


def ppm_blue_channel_average(file_path: str | Path) -> float:
    """Return the average blue channel value across all pixels."""
    img = parse_ppm_strict(file_path)
    if not img.pixels:
        return 0.0
    return sum(p[2] for p in img.pixels) / len(img.pixels)


def ppm_is_grayscale(file_path: str | Path) -> bool:
    """Return True if all pixels have equal R, G, B values."""
    img = parse_ppm_strict(file_path)
    if not img.pixels:
        return True
    return all(p[0] == p[1] == p[2] for p in img.pixels)


def ppm_channel_range(file_path: str | Path) -> dict[str, int]:
    """Return the range (max - min) for each RGB channel."""
    img = parse_ppm_strict(file_path)
    if not img.pixels:
        return {"red": 0, "green": 0, "blue": 0}
    reds = [p[0] for p in img.pixels]
    greens = [p[1] for p in img.pixels]
    blues = [p[2] for p in img.pixels]
    return {
        "red": max(reds) - min(reds),
        "green": max(greens) - min(greens),
        "blue": max(blues) - min(blues),
    }


def ppm_saturation_estimate(file_path: str | Path) -> float:
    """Return the average per-pixel saturation estimate (max_channel - min_channel)."""
    img = parse_ppm_strict(file_path)
    if not img.pixels:
        return 0.0
    total = sum(max(p[0], p[1], p[2]) - min(p[0], p[1], p[2]) for p in img.pixels)
    return total / len(img.pixels)


def ppm_is_dark(file_path: str | Path) -> bool:
    """Return True if the average pixel brightness is below 128.

    Args:
        file_path: Path to a PPM file.

    Returns:
        True if average brightness < 128, False otherwise or if no pixels.
    """
    img = parse_ppm_strict(file_path)
    if not img.pixels:
        return False
    avg = sum((p[0] + p[1] + p[2]) / 3.0 for p in img.pixels) / len(img.pixels)
    return avg < 128.0


def ppm_red_channel_sum(file_path: str | Path) -> int:
    """Return the sum of all red channel pixel values.

    Args:
        file_path: Path to a PPM file.

    Returns:
        Integer sum of all red channel values.
    """
    img = parse_ppm_strict(file_path)
    return sum(p[0] for p in img.pixels)


def ppm_luminance_average(file_path: str | Path) -> float:
    """Return the average luminance using ITU-R BT.601 formula.

    Y = 0.299*R + 0.587*G + 0.114*B

    Args:
        file_path: Path to a PPM file.

    Returns:
        Float average luminance in [0.0, maxval]. Returns 0.0 for empty images.
    """
    img = parse_ppm_strict(file_path)
    if not img.pixels:
        return 0.0
    total = sum(0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2] for p in img.pixels)
    return total / len(img.pixels)


def ppm_green_channel_sum(file_path: str | Path) -> int:
    """Return the sum of all green channel pixel values.

    Args:
        file_path: Path to a PPM file.

    Returns:
        Integer sum of all green channel values.
    """
    img = parse_ppm_strict(file_path)
    return sum(p[1] for p in img.pixels)


def ppm_row_count(file_path: str | Path) -> int:
    """Return the number of rows (height) in the PPM image."""
    img = parse_ppm_strict(file_path)
    return img.height


def ppm_blue_channel_sum(file_path: str | Path) -> int:
    """Return the sum of all blue channel pixel values."""
    img = parse_ppm_strict(file_path)
    return sum(p[2] for p in img.pixels)




def ppm_perimeter(file_path: str | Path) -> int:
    """Return the image perimeter in pixels: 2 * (width + height).

    Args:
        file_path: Path to a PPM file.

    Returns:
        Integer perimeter.
    """
    img = parse_ppm_strict(file_path)
    return 2 * (img.width + img.height)


def ppm_dimension_ratio(file_path: str | Path) -> float:
    """Return width / height ratio. 0.0 if height is 0."""
    img = parse_ppm_strict(file_path)
    if img.height == 0:
        return 0.0
    return img.width / img.height


def ppm_is_square(file_path: str | Path) -> bool:
    """Return True if the PPM image width equals its height."""
    img = parse_ppm_strict(file_path)
    return img.width == img.height


def ppm_is_landscape(file_path: str | Path) -> bool:
    """Return True if the PPM image is wider than it is tall."""
    img = parse_ppm_strict(file_path)
    return img.width > img.height


def ppm_max_dimension(file_path: str | Path) -> int:
    """Return the larger of width and height."""
    img = parse_ppm_strict(file_path)
    return max(img.width, img.height)


def ppm_has_pure_black(file_path: str | Path) -> bool:
    """Return True if any pixel is pure black (R=0, G=0, B=0)."""
    img = parse_ppm_strict(file_path)
    return any(r == 0 and g == 0 and b == 0 for r, g, b in img.pixels)


def ppm_max_channel_sum(file_path: str | Path) -> int:
    """Return the maximum R+G+B sum across all pixels."""
    img = parse_ppm_strict(file_path)
    if not img.pixels:
        return 0
    return max(r + g + b for r, g, b in img.pixels)


def ppm_min_channel_sum(file_path: str | Path) -> int:
    """Return the minimum R+G+B sum across all pixels."""
    img = parse_ppm_strict(file_path)
    if not img.pixels:
        return 0
    return min(r + g + b for r, g, b in img.pixels)


def ppm_has_pure_white(file_path: str | Path) -> bool:
    """Return True if any pixel has R=maxval, G=maxval, B=maxval."""
    img = parse_ppm_strict(file_path)
    mv = img.maxval
    return any(r == mv and g == mv and b == mv for r, g, b in img.pixels)


def ppm_megapixels(file_path: str | Path) -> float:
    """Return image size in megapixels."""
    img = parse_ppm_strict(file_path)
    return (img.width * img.height) / 1_000_000


def ppm_channel_balance(file_path: str | Path) -> float:
    """Return 1.0 - (max_avg - min_avg)/maxval. Higher = more balanced."""
    img = parse_ppm_strict(file_path)
    if not img.pixels or img.maxval == 0:
        return 1.0
    r_avg = sum(p[0] for p in img.pixels) / len(img.pixels)
    g_avg = sum(p[1] for p in img.pixels) / len(img.pixels)
    b_avg = sum(p[2] for p in img.pixels) / len(img.pixels)
    spread = max(r_avg, g_avg, b_avg) - min(r_avg, g_avg, b_avg)
    return 1.0 - (spread / img.maxval)


def ppm_column_count(file_path: str | Path) -> int:
    """Return the number of columns (width) in the image."""
    img = parse_ppm_strict(file_path)
    return img.width


def ppm_min_dimension(file_path: str | Path) -> int:
    """Return the minimum of width and height."""
    img = parse_ppm_strict(file_path)
    return min(img.width, img.height)


def ppm_is_tall(file_path: str | Path) -> bool:
    """Return True if height > 2 * width."""
    img = parse_ppm_strict(file_path)
    return img.height > 2 * img.width


def ppm_pixel_density(file_path: str | Path) -> float:
    """Return pixels per byte of file size. 0.0 if file_size is 0."""
    img = parse_ppm_strict(file_path)
    fsize = Path(file_path).stat().st_size
    if fsize == 0:
        return 0.0
    return (img.width * img.height) / fsize


def ppm_is_portrait(file_path: str | Path) -> bool:
    """Return True if height > width."""
    img = parse_ppm_strict(file_path)
    return img.height > img.width


def ppm_diagonal(file_path: str | Path) -> float:
    """Return diagonal length: sqrt(width^2 + height^2)."""
    import math
    img = parse_ppm_strict(file_path)
    return math.sqrt(img.width ** 2 + img.height ** 2)


def ppm_is_monochrome(file_path: str | Path) -> bool:
    """Return True if all pixels share the same RGB values."""
    img = parse_ppm_strict(file_path)
    if not img.pixels:
        return True
    first = (img.pixels[0][0], img.pixels[0][1], img.pixels[0][2])
    return all((p[0], p[1], p[2]) == first for p in img.pixels)


def ppm_total_channel_sum(file_path: str | Path) -> int:
    """Return the sum of all R+G+B values across all pixels."""
    img = parse_ppm_strict(file_path)
    return sum(p[0] + p[1] + p[2] for p in img.pixels)


def ppm_avg_brightness(file_path: str | Path) -> float:
    """Return average brightness (mean of R+G+B / 3) across all pixels. 0.0 if none."""
    img = parse_ppm_strict(file_path)
    if not img.pixels:
        return 0.0
    total = sum((p[0] + p[1] + p[2]) / 3.0 for p in img.pixels)
    return total / len(img.pixels)


def ppm_color_variance(file_path: str | Path) -> float:
    """Return variance of pixel brightness values. 0.0 if fewer than 2 pixels."""
    img = parse_ppm_strict(file_path)
    if len(img.pixels) < 2:
        return 0.0
    brightnesses = [(p[0] + p[1] + p[2]) / 3.0 for p in img.pixels]
    mean = sum(brightnesses) / len(brightnesses)
    return sum((b - mean) ** 2 for b in brightnesses) / len(brightnesses)


def ppm_distinct_pixel_count(file_path: str | Path) -> int:
    """Return the count of distinct (R, G, B) pixel tuples."""
    img = parse_ppm_strict(file_path)
    return len(set(img.pixels))




def ppm_red_ratio(file_path: str | Path) -> float:
    """Return ratio of red channel sum to total channel sum. 0.0 if no pixels."""
    img = parse_ppm_strict(file_path)
    if not img.pixels:
        return 0.0
    red = sum(p[0] for p in img.pixels)
    total = sum(p[0] + p[1] + p[2] for p in img.pixels)
    if total == 0:
        return 0.0
    return red / total


def ppm_border_brightness(file_path: str | Path) -> float:
    """Return average brightness of border pixels. 0.0 if no pixels."""
    img = parse_ppm_strict(file_path)
    if img.width == 0 or img.height == 0:
        return 0.0
    border = []
    for i, p in enumerate(img.pixels):
        r = i // img.width
        c = i % img.width
        if r == 0 or r == img.height - 1 or c == 0 or c == img.width - 1:
            border.append((p[0] + p[1] + p[2]) / 3.0)
    if not border:
        return 0.0
    return sum(border) / len(border)


def ppm_green_ratio(file_path: str | Path) -> float:
    """Return ratio of green channel sum to total channel sum. 0.0 if no pixels."""
    img = parse_ppm_strict(file_path)
    if not img.pixels:
        return 0.0
    green = sum(p[1] for p in img.pixels)
    total = sum(p[0] + p[1] + p[2] for p in img.pixels)
    if total == 0:
        return 0.0
    return green / total


def ppm_pixel_brightness_range(file_path: str | Path) -> float:
    """Return brightness range (max - min) as ratio of maxval. 0.0 if no pixels."""
    img = parse_ppm_strict(file_path)
    if not img.pixels:
        return 0.0
    brightnesses = [(p[0] + p[1] + p[2]) / 3.0 for p in img.pixels]
    return (max(brightnesses) - min(brightnesses)) / max(img.maxval, 1)


def ppm_blue_ratio(file_path: str | Path) -> float:
    """Return blue channel sum as ratio of total channel sum. 0.0 if no pixels."""
    img = parse_ppm_strict(file_path)
    if not img.pixels:
        return 0.0
    total = sum(p[0] + p[1] + p[2] for p in img.pixels)
    if total == 0:
        return 0.0
    blue = sum(p[2] for p in img.pixels)
    return blue / total


def ppm_is_bright(file_path: str | Path) -> bool:
    """Return True if mean brightness exceeds 66% of maxval."""
    img = parse_ppm_strict(file_path)
    if not img.pixels or img.maxval == 0:
        return False
    mean = sum((p[0] + p[1] + p[2]) / 3.0 for p in img.pixels) / len(img.pixels)
    return mean > (img.maxval * 0.66)


def ppm_maxval(file_path: str | Path) -> int:
    """Return the maxval field from the PPM header."""
    img = parse_ppm_strict(file_path)
    return img.maxval


def ppm_normalized_brightness(file_path: str | Path) -> float:
    """Return mean brightness normalized to [0.0, 1.0] by maxval. 0.0 if no pixels."""
    img = parse_ppm_strict(file_path)
    if not img.pixels or img.maxval == 0:
        return 0.0
    mean = sum((p[0] + p[1] + p[2]) / 3.0 for p in img.pixels) / len(img.pixels)
    return mean / img.maxval


def ppm_area(file_path: str | Path) -> int:
    """Return image area in pixels: width * height."""
    img = parse_ppm_strict(file_path)
    return img.width * img.height


def ppm_min_channel_avg(file_path: str | Path) -> float:
    """Return the minimum of the average R, G, B channel values. 0.0 if no pixels."""
    img = parse_ppm_strict(file_path)
    if not img.pixels:
        return 0.0
    n = len(img.pixels)
    avg_r = sum(p[0] for p in img.pixels) / n
    avg_g = sum(p[1] for p in img.pixels) / n
    avg_b = sum(p[2] for p in img.pixels) / n
    return min(avg_r, avg_g, avg_b)


def ppm_max_pixel_brightness(file_path: str | Path) -> float:
    """Return the maximum per-pixel brightness ((R+G+B)/3). 0.0 if no pixels."""
    img = parse_ppm_strict(file_path)
    if not img.pixels:
        return 0.0
    return max((p[0] + p[1] + p[2]) / 3.0 for p in img.pixels)



# ---------------------------------------------------------------------------
# Analytics functions for deepening tests (TC-F-012)
# ---------------------------------------------------------------------------

def ppm_max_channel_value(file_path: "str | Path") -> int:
    """Return max value across all channels (R, G, B) in all pixels. 0 if no pixels."""
    img = parse_ppm_strict(file_path)
    if not img.pixels:
        return 0
    return max(max(p[0], p[1], p[2]) for p in img.pixels)


def ppm_min_channel_value(file_path: "str | Path") -> int:
    """Return min value across all channels (R, G, B) in all pixels. 0 if no pixels."""
    img = parse_ppm_strict(file_path)
    if not img.pixels:
        return 0
    return min(min(p[0], p[1], p[2]) for p in img.pixels)


def ppm_pixel_value_sum(file_path: "str | Path") -> int:
    """Return sum of all channel values (R+G+B) across all pixels."""
    img = parse_ppm_strict(file_path)
    return sum(p[0] + p[1] + p[2] for p in img.pixels)


def ppm_channel_contrast_sum(file_path: "str | Path") -> int:
    """Return sum of |R-G| + |G-B| + |R-B| for each pixel across all pixels."""
    img = parse_ppm_strict(file_path)
    return sum(abs(p[0] - p[1]) + abs(p[1] - p[2]) + abs(p[0] - p[2]) for p in img.pixels)


def ppm_red_channel_ratio(file_path: "str | Path") -> float:
    """Return fraction of total channel energy carried by the red channel."""
    img = parse_ppm_strict(file_path)
    if not img.pixels:
        return 0.0
    total = sum(p[0] + p[1] + p[2] for p in img.pixels)
    if total == 0:
        return 0.0
    return sum(p[0] for p in img.pixels) / total


def ppm_green_channel_ratio(file_path: "str | Path") -> float:
    """Return fraction of total channel energy carried by the green channel."""
    img = parse_ppm_strict(file_path)
    if not img.pixels:
        return 0.0
    total = sum(p[0] + p[1] + p[2] for p in img.pixels)
    if total == 0:
        return 0.0
    return sum(p[1] for p in img.pixels) / total


def ppm_blue_channel_ratio(file_path: "str | Path") -> float:
    """Return fraction of total channel energy carried by the blue channel."""
    img = parse_ppm_strict(file_path)
    if not img.pixels:
        return 0.0
    total = sum(p[0] + p[1] + p[2] for p in img.pixels)
    if total == 0:
        return 0.0
    return sum(p[2] for p in img.pixels) / total
