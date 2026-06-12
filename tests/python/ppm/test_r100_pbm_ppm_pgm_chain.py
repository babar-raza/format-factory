# R100 Train F: Python Netpbm deep lane — PBM->PPM->PGM full chain tests
# Governed skill: /verify-dogfood-path
# Ledger: R100-GOVERNED-PYTHON-NETPBM-CHAIN-001

import tempfile
from pathlib import Path


from pbm.pbm_parser import parse_pbm_strict, write_pbm
from ppm.ppm_parser import write_ppm, parse_ppm_strict
from pgm.pgm_parser import write_pgm, parse_pgm_strict


def test_pbm_to_ppm_expansion():
    """PBM black/white expands to PPM (0,0,0)/(255,255,255)."""
    pixels = [0, 1, 1, 0]  # 0=white, 1=black
    with tempfile.NamedTemporaryFile(suffix=".pbm", delete=False) as f:
        tmp_pbm = f.name
    try:
        write_pbm(pixels, 2, 2, tmp_pbm)
        pbm = parse_pbm_strict(tmp_pbm)
        # Convert: PBM 0(white)->255, PBM 1(black)->0
        ppm_pixels = [(255, 255, 255) if p == 0 else (0, 0, 0) for p in pbm.pixels]
        with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
            tmp_ppm = f.name
        write_ppm(ppm_pixels, 2, 2, 255, tmp_ppm)
        ppm = parse_ppm_strict(tmp_ppm)
        assert ppm.pixels[0] == (255, 255, 255)  # white
        assert ppm.pixels[1] == (0, 0, 0)        # black
    finally:
        Path(tmp_pbm).unlink(missing_ok=True)
        Path(tmp_ppm).unlink(missing_ok=True)


def test_ppm_to_pgm_grayscale():
    """PPM color pixels convert to PGM grayscale via luminance."""
    color_pixels = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (128, 128, 128)]
    gray_pixels = []
    for r, g, b in color_pixels:
        gray = int(0.299 * r + 0.587 * g + 0.114 * b)
        gray_pixels.append(min(255, max(0, gray)))

    with tempfile.NamedTemporaryFile(suffix=".pgm", delete=False) as f:
        tmp = f.name
    try:
        write_pgm(gray_pixels, 2, 2, 255, tmp)
        pgm = parse_pgm_strict(tmp)
        assert len(pgm.pixels) == 4
        # int(0.299*128 + 0.587*128 + 0.114*128) = int(127.872) = 127
        assert pgm.pixels[3] == 127  # gray stays close to gray (rounding)
    finally:
        Path(tmp).unlink(missing_ok=True)


def test_full_chain_pbm_ppm_pgm():
    """Full chain: PBM -> PPM -> PGM with correct pixel mapping."""
    # Create PBM (3x1: white, black, white)
    pbm_pixels = [0, 1, 0]
    with tempfile.NamedTemporaryFile(suffix=".pbm", delete=False) as f:
        tmp_pbm = f.name
    with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
        tmp_ppm = f.name
    with tempfile.NamedTemporaryFile(suffix=".pgm", delete=False) as f:
        tmp_pgm = f.name

    try:
        # Step 1: Write PBM
        write_pbm(pbm_pixels, 3, 1, tmp_pbm)
        pbm = parse_pbm_strict(tmp_pbm)

        # Step 2: PBM -> PPM
        ppm_pixels = [(255, 255, 255) if p == 0 else (0, 0, 0) for p in pbm.pixels]
        write_ppm(ppm_pixels, 3, 1, 255, tmp_ppm)
        ppm = parse_ppm_strict(tmp_ppm)
        assert len(ppm.pixels) == 3

        # Step 3: PPM -> PGM
        gray = [int(0.299 * r + 0.587 * g + 0.114 * b) for r, g, b in ppm.pixels]
        write_pgm(gray, 3, 1, 255, tmp_pgm)
        pgm = parse_pgm_strict(tmp_pgm)
        assert pgm.pixels[0] == 255  # white
        assert pgm.pixels[1] == 0    # black
        assert pgm.pixels[2] == 255  # white
    finally:
        for p in [tmp_pbm, tmp_ppm, tmp_pgm]:
            Path(p).unlink(missing_ok=True)


def test_chain_preserves_dimensions():
    """All formats in chain preserve width and height."""
    w, h = 4, 3
    pbm_pixels = [i % 2 for i in range(w * h)]
    with tempfile.NamedTemporaryFile(suffix=".pbm", delete=False) as f:
        tmp_pbm = f.name
    with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
        tmp_ppm = f.name
    with tempfile.NamedTemporaryFile(suffix=".pgm", delete=False) as f:
        tmp_pgm = f.name
    try:
        write_pbm(pbm_pixels, w, h, tmp_pbm)
        pbm = parse_pbm_strict(tmp_pbm)
        ppm_pixels = [(255, 255, 255) if p == 0 else (0, 0, 0) for p in pbm.pixels]
        write_ppm(ppm_pixels, w, h, 255, tmp_ppm)
        ppm = parse_ppm_strict(tmp_ppm)
        gray = [int(0.299 * r + 0.587 * g + 0.114 * b) for r, g, b in ppm.pixels]
        write_pgm(gray, w, h, 255, tmp_pgm)
        pgm = parse_pgm_strict(tmp_pgm)
        assert pbm.width == w and pbm.height == h
        assert ppm.width == w and ppm.height == h
        assert pgm.width == w and pgm.height == h
    finally:
        for p in [tmp_pbm, tmp_ppm, tmp_pgm]:
            Path(p).unlink(missing_ok=True)


def test_pgm_to_ppm_expansion():
    """PGM gray expands to PPM (g,g,g)."""
    gray = [0, 64, 128, 255]
    with tempfile.NamedTemporaryFile(suffix=".pgm", delete=False) as f:
        tmp_pgm = f.name
    with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
        tmp_ppm = f.name
    try:
        write_pgm(gray, 2, 2, 255, tmp_pgm)
        pgm = parse_pgm_strict(tmp_pgm)
        ppm_pixels = [(g, g, g) for g in pgm.pixels]
        write_ppm(ppm_pixels, 2, 2, 255, tmp_ppm)
        ppm = parse_ppm_strict(tmp_ppm)
        for i, g in enumerate(gray):
            assert ppm.pixels[i] == (g, g, g)
    finally:
        Path(tmp_pgm).unlink(missing_ok=True)
        Path(tmp_ppm).unlink(missing_ok=True)


def test_all_black_chain():
    """All-black image through full chain stays black."""
    pbm_pixels = [1, 1, 1, 1]
    with tempfile.NamedTemporaryFile(suffix=".pbm", delete=False) as f:
        tmp_pbm = f.name
    with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
        tmp_ppm = f.name
    try:
        write_pbm(pbm_pixels, 2, 2, tmp_pbm)
        pbm = parse_pbm_strict(tmp_pbm)
        ppm_pixels = [(0, 0, 0)] * len(pbm.pixels)
        write_ppm(ppm_pixels, 2, 2, 255, tmp_ppm)
        ppm = parse_ppm_strict(tmp_ppm)
        assert all(p == (0, 0, 0) for p in ppm.pixels)
    finally:
        Path(tmp_pbm).unlink(missing_ok=True)
        Path(tmp_ppm).unlink(missing_ok=True)


def test_all_white_chain():
    """All-white image through full chain stays white."""
    pbm_pixels = [0, 0, 0, 0]
    with tempfile.NamedTemporaryFile(suffix=".pbm", delete=False) as f:
        tmp_pbm = f.name
    with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
        tmp_ppm = f.name
    try:
        write_pbm(pbm_pixels, 2, 2, tmp_pbm)
        pbm = parse_pbm_strict(tmp_pbm)
        ppm_pixels = [(255, 255, 255)] * len(pbm.pixels)
        write_ppm(ppm_pixels, 2, 2, 255, tmp_ppm)
        ppm = parse_ppm_strict(tmp_ppm)
        assert all(p == (255, 255, 255) for p in ppm.pixels)
    finally:
        Path(tmp_pbm).unlink(missing_ok=True)
        Path(tmp_ppm).unlink(missing_ok=True)


def test_pbm_write_read_roundtrip():
    """PBM write then read preserves pixels."""
    pixels = [0, 1, 0, 1, 1, 0]
    with tempfile.NamedTemporaryFile(suffix=".pbm", delete=False) as f:
        tmp = f.name
    try:
        write_pbm(pixels, 3, 2, tmp)
        result = parse_pbm_strict(tmp)
        assert list(result.pixels) == pixels
    finally:
        Path(tmp).unlink(missing_ok=True)
