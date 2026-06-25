"""PGM consumer roundtrip example — example script for customer readiness criterion 3.

Demonstrates parse/inspect/write roundtrip on a valid PGM sample.
Run from repository root: python examples/python/pgm/pgm_consumer_roundtrip.py
"""
from __future__ import annotations
import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

import pgm  # noqa: E402

SAMPLE = _REPO / "samples" / "by-format" / "pgm" / "valid" / "2x2-gradient.pgm"


def main() -> None:
    path = str(SAMPLE)

    # Parse strict
    img = pgm.parse_pgm_strict(path)
    print(f"Magic: {img.magic}, Size: {img.width}x{img.height}, Maxval: {img.maxval}")
    assert img.width == 2 and img.height == 2
    assert img.maxval > 0

    # Dict parse
    d = pgm.parse_pgm(path)
    assert "pixel_count" in d
    assert d["width"] == 2

    # Probe (no pixel decode)
    probe = pgm.probe_pgm(path)
    assert probe["width"] == 2 and probe["height"] == 2

    # Analytics
    avg = pgm.average_gray(path)
    lo, hi = pgm.min_max_gray(path)
    print(f"Average gray: {avg:.2f}, Min: {lo}, Max: {hi}")
    assert lo <= avg <= hi

    dims = pgm.get_dimensions(path)
    assert dims == (2, 2)

    ar = pgm.pgm_aspect_ratio(path)
    assert ar == 1.0  # 2x2 is square
    print(f"Aspect ratio: {ar}")

    # Write roundtrip
    with tempfile.TemporaryDirectory() as tmp:
        dest = Path(tmp) / "roundtrip.pgm"
        result = pgm.write_pgm(img.pixels, img.width, img.height, img.maxval, str(dest))
        print(f"Wrote: {dest.name}")
        assert dest.exists()
        assert dest.stat().st_size > 0

        # Parse written file back
        img2 = pgm.parse_pgm_strict(str(dest))
        assert img2.width == img.width
        assert img2.height == img.height
        assert img2.pixels == img.pixels

    print("CONSUMER_PROOF: PASS (PGM roundtrip)")


if __name__ == "__main__":
    main()
