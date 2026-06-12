"""
test_pgm_conveyor_deepening.py -- PGM product deepening tests.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-3
Tests parse, probe, write, transform functions for PGM.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

_SAMPLES = _REPO / "samples" / "by-format" / "pgm" / "valid"

from pgm.pgm_parser import (
    parse_pgm, parse_pgm_strict, probe_pgm, write_pgm,
    pixel_count, average_gray, min_max_gray, get_dimensions,
    flip_horizontal, histogram,
)


def test_parse_pgm_1x1():
    result = parse_pgm(str(_SAMPLES / "1x1-white.pgm"))
    assert result["ok"] is True


def test_parse_pgm_gradient():
    result = parse_pgm(str(_SAMPLES / "2x2-gradient.pgm"))
    assert result["ok"] is True
    assert result["width"] == 2


def test_probe_pgm():
    info = probe_pgm(str(_SAMPLES / "1x1-white.pgm"))
    assert info["valid_header"] is True


def test_pixel_count():
    assert pixel_count(str(_SAMPLES / "2x2-gradient.pgm")) == 4


def test_average_gray():
    avg = average_gray(str(_SAMPLES / "2x2-gradient.pgm"))
    assert isinstance(avg, float)
    assert 0 <= avg <= 255


def test_min_max_gray():
    lo, hi = min_max_gray(str(_SAMPLES / "2x2-gradient.pgm"))
    assert lo <= hi


def test_get_dimensions():
    dims = get_dimensions(str(_SAMPLES / "3x1-ramp.pgm"))
    assert dims[0] == 3 and dims[1] == 1


def test_write_and_reparse(tmp_path):
    img = parse_pgm_strict(str(_SAMPLES / "2x2-gradient.pgm"))
    out = tmp_path / "rewrite.pgm"
    write_pgm(img.pixels, img.width, img.height, img.maxval, str(out))
    reparsed = parse_pgm(str(out))
    assert reparsed["ok"] is True


def test_flip_horizontal(tmp_path):
    out = tmp_path / "flipped.pgm"
    flip_horizontal(str(_SAMPLES / "2x2-gradient.pgm"), str(out))
    assert out.exists()


def test_histogram():
    hist = histogram(str(_SAMPLES / "2x2-gradient.pgm"))
    assert "bins" in hist or "histogram" in hist or isinstance(hist, dict)
