"""PPM analytics example — 2nd example script for customer readiness criterion 3.

Demonstrates full color analytics API on a valid PPM sample.
Run from repository root: python examples/python/ppm/ppm_analytics_example.py
"""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

import ppm  # noqa: E402

SAMPLE = _REPO / "samples" / "by-format" / "ppm" / "valid" / "2x2-rgbw.ppm"


def main() -> None:
    path = str(SAMPLE)

    # Channel averages
    r = ppm.ppm_red_channel_average(path)
    g = ppm.ppm_green_channel_average(path)
    b = ppm.ppm_blue_channel_average(path)
    print(f"Channel averages: R={r:.2f}, G={g:.2f}, B={b:.2f}")
    assert r >= 0 and g >= 0 and b >= 0

    # Channel sums
    rs = ppm.ppm_red_channel_sum(path)
    gs = ppm.ppm_green_channel_sum(path)
    bs = ppm.ppm_blue_channel_sum(path)
    print(f"Channel sums: R={rs}, G={gs}, B={bs}")

    # Luminance
    lum = ppm.ppm_luminance_average(path)
    print(f"Luminance average: {lum:.4f}")
    assert lum >= 0

    # Predicates
    is_gray = ppm.ppm_is_grayscale(path)
    is_dark = ppm.ppm_is_dark(path)
    has_black = ppm.ppm_has_pure_black(path)
    has_white = ppm.ppm_has_pure_white(path)
    print(f"Is grayscale: {is_gray}, Is dark: {is_dark}, Has black: {has_black}, Has white: {has_white}")

    # Geometry
    total = ppm.pixel_count(path)
    ar = ppm.ppm_aspect_ratio(path)
    mp = ppm.ppm_megapixels(path)
    perim = ppm.ppm_perimeter(path)
    is_sq = ppm.ppm_is_square(path)
    print(f"Pixels: {total}, AR: {ar:.2f}, Megapixels: {mp:.6f}, Perimeter: {perim}, Square: {is_sq}")
    assert is_sq is True  # 2x2
    assert perim == 8

    # Channel range
    ch_range = ppm.ppm_channel_range(path)
    print(f"Channel range: {ch_range}")
    assert isinstance(ch_range, dict)

    # Saturation
    sat = ppm.ppm_saturation_estimate(path)
    print(f"Saturation estimate: {sat:.4f}")

    # Min/max brightness
    mm = ppm.ppm_min_max_brightness(path)
    print(f"Min/max brightness: {mm}")
    assert "min" in mm and "max" in mm

    print("CONSUMER_PROOF: PASS (PPM analytics example)")


if __name__ == "__main__":
    main()
