# R99 Train F: Python Netpbm PPM-PGM cross-format conversion tests
# Governed skill: /add-roundtrip-test
# Ledger: R99-GOVERNED-PYTHON-NETPBM-PPM-PGM-CONVERSION-001

import tempfile
from pathlib import Path


from ppm.ppm_parser import write_ppm, parse_ppm_strict
from pgm.pgm_parser import write_pgm, parse_pgm_strict


def test_ppm_to_pgm_grayscale_conversion():
    """Convert PPM pixels to grayscale and write as PGM."""
    # Create a color image
    pixels = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (128, 128, 128)]
    w, h = 2, 2

    # Convert to grayscale using BT.601 weights
    gray_pixels = []
    for r, g, b in pixels:
        gray = int(0.299 * r + 0.587 * g + 0.114 * b)
        gray = min(255, max(0, gray))
        gray_pixels.append(gray)

    with tempfile.NamedTemporaryFile(suffix=".pgm", delete=False) as f:
        tmp = f.name
    try:
        write_pgm(gray_pixels, w, h, 255, tmp)
        img = parse_pgm_strict(tmp)
        assert img.width == 2
        assert img.height == 2
        assert len(img.pixels) == 4
    finally:
        Path(tmp).unlink(missing_ok=True)


def test_pgm_to_ppm_color_expansion():
    """Expand grayscale PGM pixels to PPM color (gray replicated to R=G=B)."""
    gray_pixels = [0, 64, 128, 255]
    w, h = 2, 2

    # Convert gray to RGB by replicating
    color_pixels = [(g, g, g) for g in gray_pixels]

    with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
        tmp = f.name
    try:
        write_ppm(color_pixels, w, h, 255, tmp)
        img = parse_ppm_strict(tmp)
        for i, g in enumerate(gray_pixels):
            assert img.pixels[i] == (g, g, g)
    finally:
        Path(tmp).unlink(missing_ok=True)


def test_ppm_to_pgm_roundtrip():
    """PPM -> grayscale -> PGM -> expand -> PPM. Gray values should be preserved."""
    original_gray = [50, 100, 150, 200]
    w, h = 2, 2

    # Start with gray-only PPM
    ppm_pixels = [(g, g, g) for g in original_gray]
    with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as pf:
        ppm_path = pf.name
    with tempfile.NamedTemporaryFile(suffix=".pgm", delete=False) as gf:
        pgm_path = gf.name
    with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as pf2:
        ppm2_path = pf2.name

    try:
        # Write PPM
        write_ppm(ppm_pixels, w, h, 255, ppm_path)

        # Read PPM, convert to gray, write PGM
        ppm_img = parse_ppm_strict(ppm_path)
        gray = [int(0.299 * r + 0.587 * g + 0.114 * b)
                for r, g, b in ppm_img.pixels]
        write_pgm(gray, w, h, 255, pgm_path)

        # Read PGM, expand to color, write PPM
        pgm_img = parse_pgm_strict(pgm_path)
        color = [(p, p, p) for p in pgm_img.pixels]
        write_ppm(color, w, h, 255, ppm2_path)

        # Verify
        final = parse_ppm_strict(ppm2_path)
        for i, g in enumerate(original_gray):
            assert final.pixels[i] == (g, g, g)
    finally:
        for p in [ppm_path, pgm_path, ppm2_path]:
            Path(p).unlink(missing_ok=True)


def test_ppm_write_read_preserves_dimensions():
    """PPM file preserves width/height through write/read."""
    pixels = [(i * 10 % 256, i * 20 % 256, i * 30 % 256) for i in range(12)]
    with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
        tmp = f.name
    try:
        write_ppm(pixels, 4, 3, 255, tmp)
        img = parse_ppm_strict(tmp)
        assert img.width == 4
        assert img.height == 3
        assert len(img.pixels) == 12
    finally:
        Path(tmp).unlink(missing_ok=True)


def test_pgm_write_read_preserves_dimensions():
    """PGM file preserves width/height through write/read."""
    pixels = [i * 10 % 256 for i in range(6)]
    with tempfile.NamedTemporaryFile(suffix=".pgm", delete=False) as f:
        tmp = f.name
    try:
        write_pgm(pixels, 3, 2, 255, tmp)
        img = parse_pgm_strict(tmp)
        assert img.width == 3
        assert img.height == 2
    finally:
        Path(tmp).unlink(missing_ok=True)


def test_grayscale_pure_white():
    """Pure white PPM converts to max gray value."""
    pixels = [(255, 255, 255)]
    gray = int(0.299 * 255 + 0.587 * 255 + 0.114 * 255)
    assert gray == 255  # Should be exactly 255 for pure white


def test_grayscale_pure_black():
    """Pure black PPM converts to zero gray value."""
    pixels = [(0, 0, 0)]
    gray = int(0.299 * 0 + 0.587 * 0 + 0.114 * 0)
    assert gray == 0


def test_pgm_maxval_roundtrip():
    """PGM with non-255 maxval roundtrips correctly."""
    pixels = [0, 7, 15]
    with tempfile.NamedTemporaryFile(suffix=".pgm", delete=False) as f:
        tmp = f.name
    try:
        write_pgm(pixels, 3, 1, 15, tmp)
        img = parse_pgm_strict(tmp)
        assert img.maxval == 15
        assert list(img.pixels) == [0, 7, 15]
    finally:
        Path(tmp).unlink(missing_ok=True)
