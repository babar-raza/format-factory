"""
test_ppm_conveyor_deepening.py -- PPM product deepening tests.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-3
Tests parse, probe, write, transform functions for PPM.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

_SAMPLES = _REPO / "samples" / "by-format" / "ppm" / "valid"

from ppm.ppm_parser import (
    parse_ppm, parse_ppm_strict, probe_ppm, write_ppm,
    pixel_count, average_color, get_dimensions,
    to_grayscale, flip_horizontal, invert,
)


def test_parse_ppm_1x1():
    result = parse_ppm(str(_SAMPLES / "1x1-red.ppm"))
    assert result["ok"] is True
    assert result["width"] == 1


def test_parse_ppm_rgbw():
    result = parse_ppm(str(_SAMPLES / "2x2-rgbw.ppm"))
    assert result["ok"] is True
    assert result["width"] == 2


def test_probe_ppm():
    info = probe_ppm(str(_SAMPLES / "1x1-red.ppm"))
    assert info["valid_header"] is True


def test_pixel_count():
    assert pixel_count(str(_SAMPLES / "2x2-rgbw.ppm")) == 4


def test_average_color():
    avg = average_color(str(_SAMPLES / "2x2-rgbw.ppm"))
    assert len(avg) == 3
    assert all(0 <= c <= 255 for c in avg)


def test_get_dimensions():
    dims = get_dimensions(str(_SAMPLES / "3x1-gradient.ppm"))
    assert dims[0] == 3 and dims[1] == 1


def test_write_and_reparse(tmp_path):
    img = parse_ppm_strict(str(_SAMPLES / "2x2-rgbw.ppm"))
    out = tmp_path / "rewrite.ppm"
    write_ppm(img.pixels, img.width, img.height, img.maxval, str(out))
    reparsed = parse_ppm(str(out))
    assert reparsed["ok"] is True


def test_to_grayscale(tmp_path):
    out = tmp_path / "gray.pgm"
    result = to_grayscale(str(_SAMPLES / "2x2-rgbw.ppm"), str(out))
    assert out.exists()


def test_flip_horizontal(tmp_path):
    out = tmp_path / "flipped.ppm"
    flip_horizontal(str(_SAMPLES / "2x2-rgbw.ppm"), str(out))
    assert out.exists()


def test_invert(tmp_path):
    out = tmp_path / "inverted.ppm"
    invert(str(_SAMPLES / "2x2-rgbw.ppm"), str(out))
    assert out.exists()
