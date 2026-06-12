"""
test_xcf_conveyor_deepening.py -- XCF product deepening tests.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-1
Tests parse, probe, capabilities for XCF parser.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

_SAMPLES = _REPO / "samples" / "by-format" / "xcf" / "valid"

from xcf.xcf_parser import parse_xcf, parse_xcf_strict, probe_xcf


def test_parse_xcf_rgb():
    result = parse_xcf(str(_SAMPLES / "1x1-red-rgb.xcf"))
    assert result["ok"] is True
    assert result["width"] == 1
    assert result["height"] == 1


def test_parse_xcf_gray():
    result = parse_xcf(str(_SAMPLES / "2x2-gray.xcf"))
    assert result["ok"] is True
    assert result["width"] == 2
    assert result["height"] == 2


def test_parse_xcf_rgba():
    result = parse_xcf(str(_SAMPLES / "1x1-rgba-blue.xcf"))
    assert result["ok"] is True


def test_parse_xcf_strict_returns_image():
    img = parse_xcf_strict(str(_SAMPLES / "1x1-red-rgb.xcf"))
    assert img.width == 1
    assert img.height == 1


def test_probe_xcf_valid():
    info = probe_xcf(str(_SAMPLES / "1x1-red-rgb.xcf"))
    assert info["valid_header"] is True
    assert info["width"] == 1


def test_probe_xcf_nonexistent():
    info = probe_xcf("/nonexistent/file.xcf")
    assert info["exists"] is False


def test_parse_xcf_bad_file(tmp_path):
    fp = tmp_path / "bad.xcf"
    fp.write_bytes(b"not an xcf file")
    result = parse_xcf(str(fp))
    assert result["ok"] is False


def test_image_type_rgb():
    img = parse_xcf_strict(str(_SAMPLES / "1x1-red-rgb.xcf"))
    assert img.image_type in (0, "RGB")  # 0 = RGB


def test_layer_count():
    result = parse_xcf(str(_SAMPLES / "1x1-red-rgb.xcf"))
    assert result["ok"] is True
    assert "num_layers" in result
    assert result["num_layers"] >= 1


def test_probe_file_size():
    info = probe_xcf(str(_SAMPLES / "1x1-red-rgb.xcf"))
    assert "file_size" in info
