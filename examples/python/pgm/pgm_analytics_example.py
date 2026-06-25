"""PGM analytics example — 2nd example script for customer readiness criterion 3.

Demonstrates the full grayscale analytics API on a valid PGM sample.
Run from repository root: python examples/python/pgm/pgm_analytics_example.py
"""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

import pgm  # noqa: E402

SAMPLE = _REPO / "samples" / "by-format" / "pgm" / "valid" / "2x2-gradient.pgm"


def main() -> None:
    path = str(SAMPLE)

    # Brightness stats
    avg = pgm.pgm_average_brightness(path)
    median = pgm.pgm_median_pixel_value(path)
    lo, hi = pgm.min_max_gray(path)
    contrast = pgm.pgm_contrast_range(path)
    std = pgm.pgm_standard_deviation(path)
    print(f"Avg: {avg:.2f}, Median: {median}, Min: {lo}, Max: {hi}")
    print(f"Contrast: {contrast}, Std dev: {std:.4f}")
    assert lo <= median <= hi
    assert contrast == hi - lo

    # Pixel counts
    total = pgm.pixel_count(path)
    above = pgm.count_above_threshold(path, 100)
    zeros = pgm.pgm_zero_pixel_count(path)
    print(f"Total pixels: {total}, Above-100: {above}, Zeros: {zeros}")
    assert above <= total

    # Geometry
    ar = pgm.pgm_aspect_ratio(path)
    mp = pgm.pgm_megapixels(path)
    perim = pgm.pgm_perimeter(path)
    is_sq = pgm.pgm_is_square(path)
    print(f"AR: {ar:.2f}, Megapixels: {mp:.6f}, Perimeter: {perim}, Square: {is_sq}")
    assert is_sq is True
    assert perim == 8

    # Histogram
    hist = pgm.histogram(path)
    assert isinstance(hist, dict) and len(hist) > 0

    # Quartiles
    q = pgm.pgm_brightness_quartiles(path)
    print(f"Quartiles: {q}")
    assert isinstance(q, dict)

    # Unique values
    unique = pgm.pgm_unique_value_count(path)
    print(f"Unique pixel values: {unique}")
    assert unique >= 1

    # Stats
    stats = pgm.image_pixel_stats(path)
    assert len(stats) > 0

    print("CONSUMER_PROOF: PASS (PGM analytics example)")


if __name__ == "__main__":
    main()
