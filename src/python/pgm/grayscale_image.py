"""
PGM analytics functions extracted from pgm_parser.py (TC-HEAL-FORMATS-BATCH2).
"""
from __future__ import annotations


spec_qname = "pgm:image"
spec_fact_ref = "FACT-PGM-001"
namespace_uri = "urn:netpbm:portable-graymap"

from pathlib import Path

from .pgm_parser import (
    parse_pgm_strict,
)


def pgm_bright_pixel_ratio(file_path: str | Path, threshold: int = 128) -> float:
    """Return the fraction of pixels with value strictly above the threshold.

    Args:
        file_path: Path to a PGM file.
        threshold: Brightness threshold (default 128). Pixels > threshold are "bright".

    Returns:
        Float in [0.0, 1.0]. Returns 0.0 for empty images.

    Raises:
        PgmError: If the file cannot be parsed.
    """
    img = parse_pgm_strict(file_path)
    total = len(img.pixels)
    if total == 0:
        return 0.0
    bright = sum(1 for p in img.pixels if p > threshold)
    return bright / total


def pgm_dark_pixel_count(file_path: str | Path, threshold: int = 64) -> int:
    """Return the count of pixels with value at or below the threshold (dark pixels).

    Args:
        file_path: Path to a PGM file.
        threshold: Darkness threshold (default 64). Pixels <= threshold are "dark".

    Returns:
        Integer count of dark pixels. Returns 0 for empty images.

    Raises:
        PgmError: If the file cannot be parsed.
    """
    img = parse_pgm_strict(file_path)
    return sum(1 for p in img.pixels if p <= threshold)


def pgm_max_pixel_value(file_path: str | Path) -> int:
    """Return the maximum pixel value in a PGM image.

    Args:
        file_path: Path to a PGM file.

    Returns:
        Integer maximum pixel value in [0, maxval]. Returns 0 for empty images.

    Raises:
        PgmError: If the file cannot be parsed.
    """
    img = parse_pgm_strict(file_path)
    if not img.pixels:
        return 0
    return max(img.pixels)


def pgm_min_pixel_value(file_path: str | Path) -> int:
    """Return the minimum pixel value in a PGM image.

    Args:
        file_path: Path to a PGM file.

    Returns:
        Integer minimum pixel value in [0, maxval]. Returns 0 for empty images.

    Raises:
        PgmError: If the file cannot be parsed.
    """
    img = parse_pgm_strict(file_path)
    if not img.pixels:
        return 0
    return min(img.pixels)


def pgm_average_brightness(file_path: str | Path) -> float:
    """Return the average pixel brightness (mean gray value) of a PGM image.

    Args:
        file_path: Path to a PGM file.

    Returns:
        Float mean pixel value in [0.0, maxval]. Returns 0.0 for empty images.

    Raises:
        PgmError: If the file cannot be parsed.
    """
    img = parse_pgm_strict(file_path)
    if not img.pixels:
        return 0.0
    return sum(img.pixels) / len(img.pixels)


def pgm_contrast_range(file_path: str | Path) -> int:
    """Return the contrast range (dynamic range) of a PGM image.

    The contrast range is defined as ``max_gray - min_gray``, giving the span
    of gray values present in the image. A value of 0 means the image is
    perfectly uniform (all pixels the same shade).

    Args:
        file_path: Path to a PGM file.

    Returns:
        Integer contrast range in [0, maxval]. Returns 0 for empty images.

    Raises:
        PgmError: If the file cannot be parsed.
    """
    img = parse_pgm_strict(file_path)
    if not img.pixels:
        return 0
    return max(img.pixels) - min(img.pixels)


def pgm_median_pixel_value(file_path: str | Path) -> int:
    """Return the median pixel value of a PGM image.

    The median is the middle value when all pixels are sorted. For even-length
    pixel arrays, returns the lower of the two middle values (integer result).

    Args:
        file_path: Path to a PGM file.

    Returns:
        Integer median pixel value. Returns 0 for empty images.

    Raises:
        PgmError: If the file cannot be parsed.
    """
    img = parse_pgm_strict(file_path)
    if not img.pixels:
        return 0
    sorted_px = sorted(img.pixels)
    mid = len(sorted_px) // 2
    if len(sorted_px) % 2 == 1:
        return sorted_px[mid]
    return sorted_px[mid - 1]


def pgm_total_pixel_count(file_path: str | Path) -> int:
    """Return the total number of pixels in a PGM image (width * height).

    Args:
        file_path: Path to a PGM file.

    Returns:
        Integer total pixel count. Returns 0 for empty images.

    Raises:
        PgmError: If the file cannot be parsed.
    """
    img = parse_pgm_strict(file_path)
    return img.width * img.height


def pgm_brightness_quartiles(file_path: str | Path) -> dict[str, int]:
    """Return the 25th, 50th, and 75th percentile pixel values of a PGM image.

    Args:
        file_path: Path to a PGM file.

    Returns:
        Dict with 'q25', 'q50', 'q75' integer values. Returns all zeros for empty images.

    Raises:
        PgmError: If the file cannot be parsed.
    """
    img = parse_pgm_strict(file_path)
    if not img.pixels:
        return {"q25": 0, "q50": 0, "q75": 0}
    sorted_px = sorted(img.pixels)
    n = len(sorted_px)
    return {
        "q25": sorted_px[n // 4],
        "q50": sorted_px[n // 2],
        "q75": sorted_px[(3 * n) // 4],
    }


def pgm_is_uniform(file_path: str | Path) -> bool:
    """Return True if all pixels have the same value."""
    img = parse_pgm_strict(file_path)
    if not img.pixels:
        return True
    first = img.pixels[0]
    return all(p == first for p in img.pixels)


def pgm_nonzero_pixel_ratio(file_path: str | Path) -> float:
    """Return the ratio of non-zero pixels to total pixels. 0.0 if no pixels."""
    img = parse_pgm_strict(file_path)
    if not img.pixels:
        return 0.0
    nonzero = sum(1 for p in img.pixels if p > 0)
    return nonzero / len(img.pixels)


def pgm_dynamic_range(file_path: str | Path) -> int:
    """Return the dynamic range (max - min pixel value). 0 if no pixels."""
    img = parse_pgm_strict(file_path)
    if not img.pixels:
        return 0
    return max(img.pixels) - min(img.pixels)


def pgm_pixel_sum(file_path: str | Path) -> int:
    """Return the sum of all pixel values."""
    img = parse_pgm_strict(file_path)
    if not img.pixels:
        return 0
    return sum(img.pixels)


def pgm_zero_pixel_count(file_path: str | Path) -> int:
    """Return the count of pixels with value 0 (pure black).

    Args:
        file_path: Path to a PGM file.

    Returns:
        Integer count of zero-value pixels.
    """
    img = parse_pgm_strict(file_path)
    return sum(1 for p in img.pixels if p == 0)


def pgm_saturated_pixel_count(file_path: str | Path) -> int:
    """Return the count of pixels at the maximum value (saturated/pure white).

    Args:
        file_path: Path to a PGM file.

    Returns:
        Integer count of pixels equal to maxval.
    """
    img = parse_pgm_strict(file_path)
    if not img.pixels:
        return 0
    return sum(1 for p in img.pixels if p >= img.maxval)


def pgm_standard_deviation(file_path: str | Path) -> float:
    """Return the standard deviation of pixel values.

    Args:
        file_path: Path to a PGM file.

    Returns:
        Float standard deviation. Returns 0.0 for empty images.
    """
    img = parse_pgm_strict(file_path)
    n = len(img.pixels)
    if n == 0:
        return 0.0
    mean = sum(img.pixels) / n
    variance = sum((p - mean) ** 2 for p in img.pixels) / n
    return variance ** 0.5


def pgm_brightness_ratio(file_path: str | Path) -> float:
    """Return the ratio of average brightness to max possible (maxval).

    Args:
        file_path: Path to a PGM file.

    Returns:
        Float in [0.0, 1.0]. Returns 0.0 for empty images.
    """
    img = parse_pgm_strict(file_path)
    if not img.pixels or img.maxval == 0:
        return 0.0
    mean = sum(img.pixels) / len(img.pixels)
    return mean / img.maxval


def pgm_has_any_saturated(file_path: str | Path) -> bool:
    """Return True if at least one pixel equals maxval (fully bright)."""
    img = parse_pgm_strict(file_path)
    return any(p == img.maxval for p in img.pixels)


def pgm_is_all_dark(file_path: str | Path) -> bool:
    """Return True if all pixels are strictly below the midpoint (maxval // 2)."""
    img = parse_pgm_strict(file_path)
    if not img.pixels:
        return False
    mid = img.maxval // 2
    return all(p < mid for p in img.pixels)


def pgm_perimeter(file_path: str | Path) -> int:
    """Return the image perimeter in pixels: 2 * (width + height).

    Args:
        file_path: Path to a PGM file.

    Returns:
        Integer perimeter.
    """
    img = parse_pgm_strict(file_path)
    return 2 * (img.width + img.height)


def pgm_unique_value_count(file_path: str | Path) -> int:
    """Return the number of distinct pixel values in the image.

    Args:
        file_path: Path to a PGM file.

    Returns:
        Integer count of unique pixel values. 0 for empty images.
    """
    img = parse_pgm_strict(file_path)
    if not img.pixels:
        return 0
    return len(set(img.pixels))


def pgm_dimension_ratio(file_path: str | Path) -> float:
    """Return width / height ratio. 0.0 if height is 0."""
    img = parse_pgm_strict(file_path)
    if img.height == 0:
        return 0.0
    return img.width / img.height


def pgm_is_square(file_path: str | Path) -> bool:
    """Return True if the PGM image width equals its height."""
    img = parse_pgm_strict(file_path)
    return img.width == img.height


def pgm_is_landscape(file_path: str | Path) -> bool:
    """Return True if the PGM image is wider than it is tall."""
    img = parse_pgm_strict(file_path)
    return img.width > img.height


def pgm_max_dimension(file_path: str | Path) -> int:
    """Return the larger of width and height."""
    img = parse_pgm_strict(file_path)
    return max(img.width, img.height)


def pgm_has_any_zero(file_path: str | Path) -> bool:
    """Return True if at least one pixel has value 0 (pure black)."""
    img = parse_pgm_strict(file_path)
    return any(p == 0 for p in img.pixels)


def pgm_is_all_bright(file_path: str | Path) -> bool:
    """Return True if all pixels are at or above the midpoint (maxval // 2)."""
    img = parse_pgm_strict(file_path)
    if not img.pixels:
        return False
    mid = img.maxval // 2
    return all(p >= mid for p in img.pixels)


def pgm_diagonal(file_path: str | Path) -> float:
    """Return the diagonal length of the image."""
    import math
    img = parse_pgm_strict(file_path)
    return math.sqrt(img.width ** 2 + img.height ** 2)


def pgm_aspect_ratio(file_path: str | Path) -> float:
    """Return width / height. 0.0 if height is 0."""
    img = parse_pgm_strict(file_path)
    if img.height == 0:
        return 0.0
    return img.width / img.height


def pgm_min_dimension(file_path: str | Path) -> int:
    """Return the smaller of width and height."""
    img = parse_pgm_strict(file_path)
    return min(img.width, img.height)


def pgm_brightness_range(file_path: str | Path) -> int:
    """Return the difference between max and min pixel values. 0 if no pixels."""
    img = parse_pgm_strict(file_path)
    if not img.pixels:
        return 0
    return max(img.pixels) - min(img.pixels)


def pgm_area(file_path: str | Path) -> int:
    """Return the area of the image: width * height."""
    img = parse_pgm_strict(file_path)
    return img.width * img.height


def pgm_mean_brightness(file_path: str | Path) -> float:
    """Return the mean pixel value. 0.0 if no pixels."""
    img = parse_pgm_strict(file_path)
    if not img.pixels:
        return 0.0
    return sum(img.pixels) / len(img.pixels)


def pgm_megapixels(file_path: str | Path) -> float:
    """Return image size in megapixels."""
    img = parse_pgm_strict(file_path)
    return (img.width * img.height) / 1_000_000


def pgm_is_tall(file_path: str | Path) -> bool:
    """Return True if height > 2 * width."""
    img = parse_pgm_strict(file_path)
    return img.height > 2 * img.width


def pgm_column_count(file_path: str | Path) -> int:
    """Return the number of columns (width) in the image."""
    img = parse_pgm_strict(file_path)
    return img.width




def pgm_is_wide(file_path: str | Path) -> bool:
    """Return True if width > 2 * height."""
    img = parse_pgm_strict(file_path)
    return img.width > 2 * img.height


def pgm_pixel_density(file_path: str | Path) -> float:
    """Return pixels per byte of file size. 0.0 if file_size is 0."""
    img = parse_pgm_strict(file_path)
    fsize = Path(file_path).stat().st_size
    if fsize == 0:
        return 0.0
    return (img.width * img.height) / fsize


def pgm_row_count(file_path: str | Path) -> int:
    """Return the image height (number of rows)."""
    img = parse_pgm_strict(file_path)
    return img.height


def pgm_is_portrait(file_path: str | Path) -> bool:
    """Return True if height > width."""
    img = parse_pgm_strict(file_path)
    return img.height > img.width


def pgm_is_high_contrast(file_path: str | Path) -> bool:
    """Return True if contrast range exceeds 50% of maxval."""
    img = parse_pgm_strict(file_path)
    if not img.pixels or img.maxval == 0:
        return False
    lo = min(img.pixels)
    hi = max(img.pixels)
    return (hi - lo) > (img.maxval * 0.5)


def pgm_avg_row_brightness(file_path: str | Path) -> list[float]:
    """Return list of average brightness for each row."""
    img = parse_pgm_strict(file_path)
    if img.width == 0 or img.height == 0:
        return []
    result = []
    for r in range(img.height):
        row_start = r * img.width
        row_pixels = img.pixels[row_start:row_start + img.width]
        result.append(sum(row_pixels) / img.width)
    return result


def pgm_dark_pixel_ratio(file_path: str | Path) -> float:
    """Return ratio of pixels below 50% of maxval to total pixels. 0.0 if no pixels."""
    img = parse_pgm_strict(file_path)
    if not img.pixels or img.maxval == 0:
        return 0.0
    threshold = img.maxval * 0.5
    dark = sum(1 for p in img.pixels if p < threshold)
    return dark / len(img.pixels)


def pgm_row_brightness_variance(file_path: str | Path) -> float:
    """Return variance of average row brightness values. 0.0 if fewer than 2 rows."""
    avgs = pgm_avg_row_brightness(file_path)
    if len(avgs) < 2:
        return 0.0
    mean = sum(avgs) / len(avgs)
    return sum((a - mean) ** 2 for a in avgs) / len(avgs)


def pgm_min_brightness(file_path: str | Path) -> int:
    """Return the minimum pixel brightness value. 0 if no pixels."""
    img = parse_pgm_strict(file_path)
    if not img.pixels:
        return 0
    return min(img.pixels)


def pgm_is_bright(file_path: str | Path) -> bool:
    """Return True if mean brightness exceeds 200."""
    img = parse_pgm_strict(file_path)
    if not img.pixels:
        return False
    return sum(img.pixels) / len(img.pixels) > 200


def pgm_brightness_histogram(file_path: str | Path, bins: int = 4) -> list[int]:
    """Return histogram of pixel brightness values in the given number of bins."""
    img = parse_pgm_strict(file_path)
    if not img.pixels or img.maxval == 0 or bins <= 0:
        return [0] * max(bins, 1)
    histogram = [0] * bins
    for p in img.pixels:
        idx = min(int(p * bins / (img.maxval + 1)), bins - 1)
        histogram[idx] += 1
    return histogram


def pgm_contrast_ratio(file_path: str | Path) -> float:
    """Return contrast ratio (max-min)/maxval. 0.0 if no pixels or maxval is 0."""
    img = parse_pgm_strict(file_path)
    if not img.pixels or img.maxval == 0:
        return 0.0
    return (max(img.pixels) - min(img.pixels)) / img.maxval


def pgm_saturated_pixel_ratio(file_path: str | Path) -> float:
    """Return ratio of saturated (maxval) pixels to total pixels. 0.0 if no pixels."""
    img = parse_pgm_strict(file_path)
    if not img.pixels:
        return 0.0
    saturated = sum(1 for p in img.pixels if p >= img.maxval)
    return saturated / len(img.pixels)


def pgm_normalized_mean(file_path: str | Path) -> float:
    """Return mean pixel value normalized to [0.0, 1.0] by dividing by maxval."""
    img = parse_pgm_strict(file_path)
    if not img.pixels or img.maxval == 0:
        return 0.0
    return (sum(img.pixels) / len(img.pixels)) / img.maxval


def pgm_above_mean_ratio(file_path: str | Path) -> float:
    """Return ratio of pixels strictly above the mean brightness. 0.0 if no pixels."""
    img = parse_pgm_strict(file_path)
    if not img.pixels:
        return 0.0
    mean = sum(img.pixels) / len(img.pixels)
    above = sum(1 for p in img.pixels if p > mean)
    return above / len(img.pixels)


def pgm_maxval(file_path: str | Path) -> int:
    """Return the maxval field from the PGM header."""
    img = parse_pgm_strict(file_path)
    return img.maxval


def pgm_midpoint_gray(file_path: str | Path) -> int:
    """Return the mid-gray value: maxval // 2."""
    img = parse_pgm_strict(file_path)
    return img.maxval // 2


def pgm_median_brightness(file_path: str | Path) -> float:
    """Return the median pixel value. 0.0 if no pixels."""
    img = parse_pgm_strict(file_path)
    if not img.pixels:
        return 0.0
    s = sorted(img.pixels)
    n = len(s)
    if n % 2 == 1:
        return float(s[n // 2])
    return (s[n // 2 - 1] + s[n // 2]) / 2.0


def pgm_pixel_value_range(file_path: str | Path) -> int:
    """Return the range (max - min) of pixel values. 0 if no pixels."""
    img = parse_pgm_strict(file_path)
    if not img.pixels:
        return 0
    return max(img.pixels) - min(img.pixels)

