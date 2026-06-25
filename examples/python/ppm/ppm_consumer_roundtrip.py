"""PPM consumer roundtrip example — example script for customer readiness criterion 3.

Demonstrates parse/inspect/write roundtrip on a valid PPM sample.
Run from repository root: python examples/python/ppm/ppm_consumer_roundtrip.py
"""
from __future__ import annotations
import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

import ppm  # noqa: E402

SAMPLE = _REPO / "samples" / "by-format" / "ppm" / "valid" / "2x2-rgbw.ppm"


def main() -> None:
    path = str(SAMPLE)

    # Parse strict
    img = ppm.parse_ppm_strict(path)
    print(f"Magic: {img.magic}, Size: {img.width}x{img.height}, Maxval: {img.maxval}")
    assert img.width == 2 and img.height == 2
    assert img.maxval > 0
    assert len(img.pixels) == img.width * img.height  # flat list of pixels

    # Dict parse
    d = ppm.parse_ppm(path)
    assert "pixel_count" in d
    assert d["width"] == 2

    # Probe
    probe = ppm.probe_ppm(path)
    assert probe["width"] == 2 and probe["height"] == 2

    # Color analytics
    avg_color = ppm.average_color(path)
    print(f"Average color (R, G, B): {avg_color[0]:.2f}, {avg_color[1]:.2f}, {avg_color[2]:.2f}")
    assert len(avg_color) == 3

    dominant = ppm.ppm_dominant_channel(path)
    print(f"Dominant channel: {dominant}")
    assert dominant in ("red", "green", "blue")

    unique = ppm.ppm_unique_color_count(path)
    print(f"Unique colors: {unique}")
    assert unique >= 1

    is_gray = ppm.is_grayscale(path)
    print(f"Is grayscale: {is_gray}")

    # Write roundtrip (write_ppm takes flat list of (R,G,B) tuples, returns None)
    with tempfile.TemporaryDirectory() as tmp:
        dest = Path(tmp) / "roundtrip.ppm"
        ppm.write_ppm(img.pixels, img.width, img.height, img.maxval, str(dest))
        print(f"Wrote: {dest.name}")
        assert dest.exists()
        assert dest.stat().st_size > 0

        # Parse written file back
        img2 = ppm.parse_ppm_strict(str(dest))
        assert img2.width == img.width
        assert img2.height == img.height
        assert img2.pixels == img.pixels

    print("CONSUMER_PROOF: PASS (PPM roundtrip)")


if __name__ == "__main__":
    main()
