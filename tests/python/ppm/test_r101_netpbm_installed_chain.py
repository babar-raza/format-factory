# R101 Train F: Netpbm Python installed chain workflow tests
# Governed skill: /verify-dogfood-path
# Ledger: R101-GOVERNED-PYTHON-NETPBM-INSTALLED-CHAIN-001
# Gap: GAP-NETPBM-PYTHON-INSTALLED-CHAIN-001

import tempfile
from pathlib import Path

import pytest

from pbm.pbm_parser import parse_pbm_strict, write_pbm
from pgm.pgm_parser import parse_pgm_strict, write_pgm
from ppm.ppm_parser import parse_ppm_strict, write_ppm


def test_pbm_write_parse_roundtrip():
    """Write a PBM image and parse it back; pixels match."""
    pixels = [0, 1, 1, 0, 1, 0]
    w, h = 3, 2
    with tempfile.NamedTemporaryFile(suffix=".pbm", delete=False) as f:
        tmp = f.name
    try:
        write_pbm(pixels, w, h, tmp)
        img = parse_pbm_strict(tmp)
        assert img.width == w
        assert img.height == h
        assert list(img.pixels) == pixels
    finally:
        Path(tmp).unlink(missing_ok=True)


def test_pgm_write_parse_roundtrip():
    """Write a PGM image and parse it back; pixels match."""
    pixels = [0, 64, 128, 192, 255, 32]
    w, h = 3, 2
    with tempfile.NamedTemporaryFile(suffix=".pgm", delete=False) as f:
        tmp = f.name
    try:
        write_pgm(pixels, w, h, 255, tmp)
        img = parse_pgm_strict(tmp)
        assert img.width == w
        assert img.height == h
        assert list(img.pixels) == pixels
    finally:
        Path(tmp).unlink(missing_ok=True)


def test_ppm_write_parse_roundtrip():
    """Write a PPM image and parse it back; pixels match."""
    pixels = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (128, 128, 128)]
    w, h = 2, 2
    with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
        tmp = f.name
    try:
        write_ppm(pixels, w, h, 255, tmp)
        img = parse_ppm_strict(tmp)
        assert img.width == w
        assert img.height == h
        for i, p in enumerate(pixels):
            assert img.pixels[i] == p
    finally:
        Path(tmp).unlink(missing_ok=True)


def test_pbm_to_pgm_chain():
    """PBM→PGM: write PBM, read it, convert pixel values, write as PGM."""
    pbm_pixels = [0, 1, 1, 0]
    w, h = 2, 2
    with tempfile.NamedTemporaryFile(suffix=".pbm", delete=False) as f:
        pbm_path = f.name
    with tempfile.NamedTemporaryFile(suffix=".pgm", delete=False) as f:
        pgm_path = f.name
    try:
        write_pbm(pbm_pixels, w, h, pbm_path)
        img = parse_pbm_strict(pbm_path)
        pgm_pixels = [p * 255 for p in img.pixels]
        write_pgm(pgm_pixels, img.width, img.height, 255, pgm_path)
        pgm_img = parse_pgm_strict(pgm_path)
        assert pgm_img.width == w
        assert pgm_img.height == h
        assert pgm_img.pixels[0] == 0
        assert pgm_img.pixels[1] == 255
    finally:
        Path(pbm_path).unlink(missing_ok=True)
        Path(pgm_path).unlink(missing_ok=True)


def test_pgm_to_ppm_chain():
    """PGM→PPM: write PGM grayscale, convert to PPM color."""
    pgm_pixels = [0, 128, 255, 64]
    w, h = 2, 2
    with tempfile.NamedTemporaryFile(suffix=".pgm", delete=False) as f:
        pgm_path = f.name
    with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
        ppm_path = f.name
    try:
        write_pgm(pgm_pixels, w, h, 255, pgm_path)
        img = parse_pgm_strict(pgm_path)
        ppm_pixels = [(p, p, p) for p in img.pixels]
        write_ppm(ppm_pixels, img.width, img.height, 255, ppm_path)
        ppm_img = parse_ppm_strict(ppm_path)
        assert ppm_img.width == w
        assert ppm_img.pixels[0] == (0, 0, 0)
        assert ppm_img.pixels[1] == (128, 128, 128)
    finally:
        Path(pgm_path).unlink(missing_ok=True)
        Path(ppm_path).unlink(missing_ok=True)


def test_ppm_to_pgm_grayscale_chain():
    """PPM→PGM: write PPM, read, compute grayscale, write as PGM."""
    ppm_pixels = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 255)]
    w, h = 2, 2
    with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
        ppm_path = f.name
    with tempfile.NamedTemporaryFile(suffix=".pgm", delete=False) as f:
        pgm_path = f.name
    try:
        write_ppm(ppm_pixels, w, h, 255, ppm_path)
        img = parse_ppm_strict(ppm_path)
        pgm_pixels = [int(0.299 * r + 0.587 * g + 0.114 * b) for r, g, b in img.pixels]
        write_pgm(pgm_pixels, img.width, img.height, 255, pgm_path)
        pgm_img = parse_pgm_strict(pgm_path)
        assert pgm_img.width == w
        assert pgm_img.pixels[0] == int(0.299 * 255)  # red -> 76
    finally:
        Path(ppm_path).unlink(missing_ok=True)
        Path(pgm_path).unlink(missing_ok=True)


def test_full_pbm_pgm_ppm_chain():
    """PBM→PGM→PPM: full three-format chain."""
    pbm_pixels = [1, 0, 0, 1]
    w, h = 2, 2
    with tempfile.NamedTemporaryFile(suffix=".pbm", delete=False) as f:
        pbm_path = f.name
    with tempfile.NamedTemporaryFile(suffix=".pgm", delete=False) as f:
        pgm_path = f.name
    with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
        ppm_path = f.name
    try:
        write_pbm(pbm_pixels, w, h, pbm_path)
        pbm_img = parse_pbm_strict(pbm_path)
        pgm_pixels = [p * 255 for p in pbm_img.pixels]
        write_pgm(pgm_pixels, w, h, 255, pgm_path)
        pgm_img = parse_pgm_strict(pgm_path)
        ppm_pixels = [(p, p, p) for p in pgm_img.pixels]
        write_ppm(ppm_pixels, w, h, 255, ppm_path)
        ppm_img = parse_ppm_strict(ppm_path)
        assert ppm_img.pixels[0] == (255, 255, 255)  # pbm 1 -> 255
        assert ppm_img.pixels[1] == (0, 0, 0)        # pbm 0 -> 0
    finally:
        Path(pbm_path).unlink(missing_ok=True)
        Path(pgm_path).unlink(missing_ok=True)
        Path(ppm_path).unlink(missing_ok=True)


def test_single_pixel_all_formats():
    """1x1 image roundtrip through all three formats."""
    with tempfile.NamedTemporaryFile(suffix=".pbm", delete=False) as f:
        pbm_path = f.name
    with tempfile.NamedTemporaryFile(suffix=".pgm", delete=False) as f:
        pgm_path = f.name
    with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
        ppm_path = f.name
    try:
        write_pbm([1], 1, 1, pbm_path)
        assert parse_pbm_strict(pbm_path).pixels[0] == 1
        write_pgm([200], 1, 1, 255, pgm_path)
        assert parse_pgm_strict(pgm_path).pixels[0] == 200
        write_ppm([(100, 150, 200)], 1, 1, 255, ppm_path)
        assert parse_ppm_strict(ppm_path).pixels[0] == (100, 150, 200)
    finally:
        Path(pbm_path).unlink(missing_ok=True)
        Path(pgm_path).unlink(missing_ok=True)
        Path(ppm_path).unlink(missing_ok=True)
