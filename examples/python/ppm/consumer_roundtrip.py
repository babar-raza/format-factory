"""PPM consumer roundtrip — TC-D-008 (ALLFORMAT-DEEPENING-20260625).

parse strict → inspect → color analytics → write → reload → verify pixels.

Usage:
    python examples/python/ppm/consumer_roundtrip.py
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

import ppm  # noqa: E402

SAMPLE = _REPO / "samples" / "by-format" / "ppm" / "valid" / "2x2-rgbw.ppm"


def main() -> int:
    print("=== PPM Consumer Roundtrip Proof ===")

    # Step 1: Strict parse
    img = ppm.parse_ppm_strict(str(SAMPLE))
    print(f"[PARSE] {img.width}x{img.height}, maxval={img.maxval}, magic={img.magic!r}")
    assert img.width > 0 and img.height > 0 and img.maxval > 0
    assert len(img.pixels) == img.width * img.height

    # Step 2: Dict parse and probe
    d = ppm.parse_ppm(str(SAMPLE))
    assert d["width"] == img.width
    probe = ppm.probe_ppm(str(SAMPLE))
    assert probe["width"] == img.width
    print(f"[INSPECT] pixel_count={d['pixel_count']}")

    # Step 3: Color analytics
    avg_color = ppm.average_color(str(SAMPLE))
    dominant = ppm.ppm_dominant_channel(str(SAMPLE))
    unique = ppm.ppm_unique_color_count(str(SAMPLE))
    is_gray = ppm.is_grayscale(str(SAMPLE))
    assert len(avg_color) == 3
    assert dominant in ("red", "green", "blue")
    print(f"[ANALYTICS] avg={avg_color[0]:.1f},{avg_color[1]:.1f},{avg_color[2]:.1f} dominant={dominant!r} unique={unique}")

    # Step 4: Write roundtrip
    with tempfile.TemporaryDirectory() as tmp:
        dest = Path(tmp) / "roundtrip.ppm"
        ppm.write_ppm(img.pixels, img.width, img.height, img.maxval, str(dest))
        assert dest.exists() and dest.stat().st_size > 0
        print(f"[WRITE] {dest.stat().st_size} bytes")

        img2 = ppm.parse_ppm_strict(str(dest))
        assert img2.width == img.width and img2.height == img.height
        assert img2.pixels == img.pixels
        print(f"[VERIFY] {img2.width}x{img2.height}, {len(img2.pixels)} pixels match")

    print("\nCONSUMER_PROOF: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
