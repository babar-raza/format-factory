"""PGM consumer roundtrip — TC-D-007 (ALLFORMAT-DEEPENING-20260625).

parse strict → inspect → analytics → write → reload → verify pixels.

Usage:
    python examples/python/pgm/consumer_roundtrip.py
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

import pgm  # noqa: E402

SAMPLE = _REPO / "samples" / "by-format" / "pgm" / "valid" / "2x2-gradient.pgm"


def main() -> int:
    print("=== PGM Consumer Roundtrip Proof ===")

    # Step 1: Strict parse
    img = pgm.parse_pgm_strict(str(SAMPLE))
    print(f"[PARSE] {img.width}x{img.height}, maxval={img.maxval}, magic={img.magic!r}")
    assert img.width > 0 and img.height > 0 and img.maxval > 0

    # Step 2: Dict parse and probe
    d = pgm.parse_pgm(str(SAMPLE))
    assert d["width"] == img.width
    probe = pgm.probe_pgm(str(SAMPLE))
    assert probe["width"] == img.width
    print(f"[INSPECT] pixel_count={d['pixel_count']}")

    # Step 3: Analytics
    avg = pgm.average_gray(str(SAMPLE))
    lo, hi = pgm.min_max_gray(str(SAMPLE))
    dims = pgm.get_dimensions(str(SAMPLE))
    ar = pgm.pgm_aspect_ratio(str(SAMPLE))
    assert lo <= avg <= hi
    print(f"[ANALYTICS] avg_gray={avg:.2f}, min={lo}, max={hi}, aspect={ar:.2f}")

    # Step 4: Write roundtrip
    with tempfile.TemporaryDirectory() as tmp:
        dest = Path(tmp) / "roundtrip.pgm"
        pgm.write_pgm(img.pixels, img.width, img.height, img.maxval, str(dest))
        assert dest.exists() and dest.stat().st_size > 0
        print(f"[WRITE] {dest.stat().st_size} bytes")

        img2 = pgm.parse_pgm_strict(str(dest))
        assert img2.width == img.width and img2.height == img.height
        assert img2.pixels == img.pixels
        print(f"[VERIFY] {img2.width}x{img2.height}, {len(img2.pixels)} pixels match")

    print("\nCONSUMER_PROOF: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
