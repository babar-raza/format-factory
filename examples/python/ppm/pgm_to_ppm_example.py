"""
pgm_to_ppm_example.py — Example: convert a PGM grayscale image to PPM color.

This example demonstrates the R99 dogfood export workflow:
1. Parse a PGM file using format-factory-pgm
2. Convert grayscale to RGB by replicating gray -> (R=G=B)
3. Write as PPM using format-factory-ppm (dogfood — no external libs)
4. Verify the output is a valid PPM file

dogfood_status: IMPLEMENTED
Source library: format-factory-pgm (parse_pgm_strict)
Write backend: format-factory-ppm (write_ppm)

Requirements:
    pip install aspose-format-factory-pgm aspose-format-factory-ppm

Usage:
    python examples/python/ppm/pgm_to_ppm_example.py

License: Apache-2.0 — Format Factory Python FOSS track
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src" / "python"))


def main() -> None:
    from pgm.pgm_parser import parse_pgm_strict, write_pgm
    from ppm.ppm_parser import parse_ppm_strict, write_ppm

    print("=== PGM -> PPM Dogfood Export Example ===\n")

    # Create a sample 3x3 PGM grayscale image
    gray_pixels = [0, 128, 255, 64, 192, 32, 224, 96, 160]
    w, h, maxval = 3, 3, 255

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        pgm_path = tmp / "gradient.pgm"
        ppm_path = tmp / "gradient.ppm"

        # Write sample PGM
        write_pgm(gray_pixels, w, h, maxval, str(pgm_path))
        print(f"Sample PGM written: {pgm_path.name}")

        # Step 1: Parse PGM using FF pgm library
        pgm_image = parse_pgm_strict(str(pgm_path))
        print(f"Parsed PGM: {pgm_image.width}x{pgm_image.height}, maxval={pgm_image.maxval}")
        print(f"PGM pixels: {list(pgm_image.pixels)}")

        # Step 2: Convert grayscale to RGB (replicate gray to R=G=B)
        color_pixels = [(g, g, g) for g in pgm_image.pixels]

        # Step 3: Write as PPM using FF ppm library
        write_ppm(color_pixels, w, h, maxval, str(ppm_path))
        print(f"\nPPM written: {ppm_path.name}")

        # Step 4: Parse and verify the output
        ppm_image = parse_ppm_strict(str(ppm_path))
        print(f"\nVerification:")
        print(f"  PPM dimensions: {ppm_image.width}x{ppm_image.height}")
        print(f"  PPM maxval: {ppm_image.maxval}")
        print(f"  PPM pixels (R,G,B): {list(ppm_image.pixels)}")

        # Verify pixel mapping: each gray value replicated to (g, g, g)
        for i, g in enumerate(pgm_image.pixels):
            assert ppm_image.pixels[i] == (g, g, g), (
                f"Pixel {i} mismatch: {ppm_image.pixels[i]} != ({g}, {g}, {g})"
            )
        print("  Pixel mapping verification: PASS (gray -> R=G=B)")

        print(f"\ndogfood_status: IMPLEMENTED")
        print(f"dogfood_library: format-factory-ppm (write_ppm)")
        print(f"source_library: format-factory-pgm (parse_pgm_strict)")

    print("\n=== PGM -> PPM Example Complete ===")


if __name__ == "__main__":
    main()
