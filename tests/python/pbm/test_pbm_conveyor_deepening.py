"""
test_pbm_conveyor_deepening.py -- PBM product deepening tests.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-3
Tests parse, probe, write, transform functions for PBM.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

_SAMPLES = _REPO / "samples" / "by-format" / "pbm" / "valid"

from pbm.pbm_parser import (
    parse_pbm, parse_pbm_strict, probe_pbm, write_pbm,
    pixel_count, count_black, count_white, get_dimensions,
    flip_horizontal, invert, image_pixel_stats,
)


def test_parse_pbm_1x1():
    result = parse_pbm(str(_SAMPLES / "1x1-black.pbm"))
    assert result["ok"] is True
    assert result["width"] == 1


def test_parse_pbm_checker():
    result = parse_pbm(str(_SAMPLES / "2x2-checker.pbm"))
    assert result["ok"] is True
    assert result["width"] == 2


def test_probe_pbm():
    info = probe_pbm(str(_SAMPLES / "1x1-black.pbm"))
    assert info["valid_header"] is True


def test_pixel_count():
    assert pixel_count(str(_SAMPLES / "2x2-checker.pbm")) == 4


def test_count_black_and_white():
    b = count_black(str(_SAMPLES / "2x2-checker.pbm"))
    w = count_white(str(_SAMPLES / "2x2-checker.pbm"))
    assert b + w == 4


def test_get_dimensions():
    dims = get_dimensions(str(_SAMPLES / "3x2-pattern.pbm"))
    assert dims == (3, 2)


def test_write_and_reparse(tmp_path):
    img = parse_pbm_strict(str(_SAMPLES / "2x2-checker.pbm"))
    out = tmp_path / "rewrite.pbm"
    write_pbm(img.pixels, img.width, img.height, str(out))
    assert out.exists()
    reparsed = parse_pbm(str(out))
    assert reparsed["ok"] is True


def test_flip_horizontal(tmp_path):
    out = tmp_path / "flipped.pbm"
    result = flip_horizontal(str(_SAMPLES / "2x2-checker.pbm"), str(out))
    assert out.exists()


def test_invert(tmp_path):
    out = tmp_path / "inverted.pbm"
    result = invert(str(_SAMPLES / "2x2-checker.pbm"), str(out))
    assert out.exists()


def test_image_pixel_stats():
    stats = image_pixel_stats(str(_SAMPLES / "2x2-checker.pbm"))
    assert "total_pixels" in stats
