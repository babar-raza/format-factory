"""PBM analytics example — 2nd example script for customer readiness criterion 3.

Demonstrates pixel analytics API on a valid PBM sample.
Run from repository root: python examples/python/pbm/pbm_analytics_example.py
"""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

import pbm  # noqa: E402

SAMPLE = _REPO / "samples" / "by-format" / "pbm" / "valid" / "2x2-checker.pbm"


def main() -> None:
    path = str(SAMPLE)

    # Dimensions
    w, h = pbm.get_dimensions(path)
    print(f"Dimensions: {w}x{h}")
    assert w == 2 and h == 2

    # Pixel counts
    black = pbm.count_black(path)
    white = pbm.count_white(path)
    total = pbm.pixel_count(path)
    print(f"Black pixels: {black}, White pixels: {white}, Total: {total}")
    assert black + white == total

    # Ratios
    br = pbm.pbm_black_pixel_ratio(path)
    wr = pbm.pbm_white_pixel_ratio(path)
    print(f"Black ratio: {br:.3f}, White ratio: {wr:.3f}")
    assert abs(br + wr - 1.0) < 1e-9

    # Geometry
    ar = pbm.aspect_ratio(path)
    mp = pbm.pbm_megapixels(path)
    perim = pbm.pbm_perimeter(path)
    print(f"Aspect ratio: {ar:.2f}, Megapixels: {mp:.6f}, Perimeter: {perim}")
    assert ar == 1.0  # 2x2 is square
    assert perim == 8  # 2*(2+2)

    # Predicates
    is_sq = pbm.pbm_is_square(path)
    is_uni = pbm.pbm_is_uniform(path)
    print(f"Is square: {is_sq}, Is uniform: {is_uni}")
    assert is_sq is True
    assert is_uni is False  # checker has both black and white

    # Row analytics
    rows = pbm.pbm_row_black_counts(path)
    print(f"Row black counts: {rows}")
    assert isinstance(rows, list)

    # Stats dict
    stats = pbm.image_pixel_stats(path)
    assert "width" in stats or "pixel_count" in stats or len(stats) > 0

    print("CONSUMER_PROOF: PASS (PBM analytics example)")


if __name__ == "__main__":
    main()
