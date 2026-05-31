"""
pbm_to_pgm_example.py — Example: convert a PBM bitmap to PGM grayscale.

This example demonstrates the R85 dogfood export workflow:
1. Parse a PBM file using format-factory-pbm
2. Convert to PGM using format-factory-pgm (dogfood — no external libs)
3. Verify the output is a valid PGM file

dogfood_status: IMPLEMENTED
Source library: format-factory-pbm (parse_pbm_strict)
Write backend: format-factory-pgm (write_pgm)

Requirements:
    pip install aspose-format-factory-pbm aspose-format-factory-pgm

Usage:
    python examples/python/pbm/pbm_to_pgm_example.py

License: Apache-2.0 — Format Factory Python FOSS track
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

# Allow running from repo root without install
REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src" / "python"))


def main() -> None:
    from pbm import parse_pbm_strict, convert_pbm_to_pgm
    from pgm.pgm_parser import parse_pgm_strict

    print("=== PBM → PGM Dogfood Export Example ===\n")

    # Create a sample 3x3 PBM in memory (text format P1)
    pbm_content = (
        "P1\n"
        "# Created by Format Factory PBM example\n"
        "3 3\n"
        "0 1 0\n"
        "1 0 1\n"
        "0 1 0\n"
    )

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        pbm_path = tmp / "checkerboard.pbm"
        pgm_path = tmp / "checkerboard.pgm"

        # Write sample PBM
        pbm_path.write_text(pbm_content, encoding="ascii")
        print(f"Sample PBM written: {pbm_path.name}")

        # Step 1: Parse PBM using FF pbm library
        pbm_image = parse_pbm_strict(pbm_path)
        print(f"Parsed PBM: {pbm_image.width}x{pbm_image.height}, format={pbm_image.format_type}")
        print(f"PBM pixels (1=black, 0=white): {pbm_image.pixels}")

        # Step 2: Convert to PGM using FF dogfood export
        result = convert_pbm_to_pgm(pbm_path, pgm_path, maxval=255)
        print(f"\ndogfood_status: {result['dogfood_status']}")
        print(f"dogfood_library: {result['dogfood_library']}")
        print(f"Output: {pgm_path.name} ({result['pixel_count']} pixels)")

        # Step 3: Parse and verify the output
        pgm_image = parse_pgm_strict(pgm_path)
        print(f"\nVerification:")
        print(f"  PGM format: {pgm_image.format_type}")
        print(f"  PGM maxval: {pgm_image.maxval}")
        print(f"  PGM pixels (255=white, 0=black): {pgm_image.pixels}")

        # Verify pixel mapping: PBM 0(white)→PGM 255, PBM 1(black)→PGM 0
        expected = [255 if p == 0 else 0 for p in pbm_image.pixels]
        assert pgm_image.pixels == expected, f"Pixel mismatch: {pgm_image.pixels} != {expected}"
        print("  Pixel mapping verification: PASS (PBM 0→255, PBM 1→0)")

        content_preview = pgm_path.read_text(encoding="ascii").split("\n")[:4]
        print(f"\nPGM file header: {content_preview}")

    print("\n=== PBM → PGM Example Complete ===")


if __name__ == "__main__":
    main()
