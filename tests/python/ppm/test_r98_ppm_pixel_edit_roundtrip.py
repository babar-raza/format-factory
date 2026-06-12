# R98 Train P: PPM pixel edit API + write roundtrip tests
# Governed skill: /add-roundtrip-test
# Ledger: R98-GOVERNED-PYTHON-PPM-PIXEL-EDIT-ROUNDTRIP-001
# Priority: 3 (edit-save roundtrip for PPM)

import tempfile
from pathlib import Path


from ppm.ppm_parser import (
    write_ppm,
    parse_ppm_strict,
)


def _make_image(width=3, height=2, maxval=255):
    """Create a simple test PPM image with a gradient pattern."""
    pixels = []
    for row in range(height):
        for col in range(width):
            r = (row * width + col) * 10 % (maxval + 1)
            g = (row * 20) % (maxval + 1)
            b = (col * 30) % (maxval + 1)
            pixels.append((r, g, b))
    return pixels, width, height, maxval


def test_write_then_parse_roundtrip():
    """Write a PPM file and parse it back; pixels match."""
    pixels, w, h, mv = _make_image()
    with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
        tmp = f.name
    try:
        write_ppm(pixels, w, h, mv, tmp)
        img = parse_ppm_strict(tmp)
        assert img.width == w
        assert img.height == h
        assert img.maxval == mv
        for i, (r, g, b) in enumerate(pixels):
            assert img.pixels[i] == (r, g, b), f"Pixel {i} mismatch"
    finally:
        Path(tmp).unlink(missing_ok=True)


def test_edit_pixel_then_write():
    """Modify a pixel in the list, write, parse back."""
    pixels, w, h, mv = _make_image()
    # Edit pixel at (0, 0)
    pixels[0] = (255, 0, 128)
    with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
        tmp = f.name
    try:
        write_ppm(pixels, w, h, mv, tmp)
        img = parse_ppm_strict(tmp)
        assert img.pixels[0] == (255, 0, 128)
    finally:
        Path(tmp).unlink(missing_ok=True)


def test_edit_multiple_pixels():
    """Modify multiple pixels and verify all persist after write."""
    pixels, w, h, mv = _make_image(4, 3)
    pixels[0] = (100, 100, 100)
    pixels[5] = (200, 200, 200)
    pixels[11] = (50, 50, 50)
    with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
        tmp = f.name
    try:
        write_ppm(pixels, w, h, mv, tmp)
        img = parse_ppm_strict(tmp)
        assert img.pixels[0] == (100, 100, 100)
        assert img.pixels[5] == (200, 200, 200)
        assert img.pixels[11] == (50, 50, 50)
    finally:
        Path(tmp).unlink(missing_ok=True)


def test_all_black_image():
    """All-black image writes and reads correctly."""
    w, h = 4, 4
    pixels = [(0, 0, 0)] * (w * h)
    with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
        tmp = f.name
    try:
        write_ppm(pixels, w, h, 255, tmp)
        img = parse_ppm_strict(tmp)
        assert all(p == (0, 0, 0) for p in img.pixels)
    finally:
        Path(tmp).unlink(missing_ok=True)


def test_all_white_image():
    """All-white image writes and reads correctly."""
    w, h = 2, 2
    pixels = [(255, 255, 255)] * (w * h)
    with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
        tmp = f.name
    try:
        write_ppm(pixels, w, h, 255, tmp)
        img = parse_ppm_strict(tmp)
        assert all(p == (255, 255, 255) for p in img.pixels)
    finally:
        Path(tmp).unlink(missing_ok=True)


def test_single_pixel_image():
    """1x1 image roundtrip."""
    pixels = [(42, 128, 200)]
    with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
        tmp = f.name
    try:
        write_ppm(pixels, 1, 1, 255, tmp)
        img = parse_ppm_strict(tmp)
        assert img.width == 1
        assert img.height == 1
        assert img.pixels[0] == (42, 128, 200)
    finally:
        Path(tmp).unlink(missing_ok=True)


def test_comment_preserved_in_output():
    """Comment in written file appears in raw text."""
    pixels = [(0, 0, 0)]
    with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
        tmp = f.name
    try:
        write_ppm(pixels, 1, 1, 255, tmp, comment="R98 test comment")
        content = Path(tmp).read_text()
        assert "R98 test comment" in content
    finally:
        Path(tmp).unlink(missing_ok=True)


def test_low_maxval_roundtrip():
    """Image with maxval=15 roundtrips correctly."""
    pixels = [(0, 7, 15), (15, 0, 8), (3, 12, 1), (10, 5, 14)]
    with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
        tmp = f.name
    try:
        write_ppm(pixels, 2, 2, 15, tmp)
        img = parse_ppm_strict(tmp)
        assert img.maxval == 15
        for i, p in enumerate(pixels):
            assert img.pixels[i] == p
    finally:
        Path(tmp).unlink(missing_ok=True)
