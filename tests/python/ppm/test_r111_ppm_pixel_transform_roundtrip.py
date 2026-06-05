# R111 Wave 6: PPM pixel-transform roundtrip tests
# Tests write_ppm → parse_ppm cycle with various pixel patterns

import pytest
import sys, os, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src/python"))

from ppm.ppm_parser import write_ppm, parse_ppm, parse_ppm_strict


def test_write_read_solid_red():
    pixels = [(255, 0, 0)] * 4
    with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
        path = f.name
    try:
        write_ppm(pixels, 2, 2, 255, path)
        result = parse_ppm(path)
        assert result["ok"] is True
        assert result["width"] == 2
        assert result["height"] == 2
    finally:
        os.unlink(path)


def test_write_read_gradient():
    pixels = [(i, i, i) for i in range(0, 256)]
    with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
        path = f.name
    try:
        write_ppm(pixels, 16, 16, 255, path)
        result = parse_ppm(path)
        assert result["ok"] is True
        assert result["pixel_count"] == 256
    finally:
        os.unlink(path)


def test_write_read_single_pixel():
    pixels = [(42, 100, 200)]
    with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
        path = f.name
    try:
        write_ppm(pixels, 1, 1, 255, path)
        result = parse_ppm(path)
        assert result["ok"] is True
        assert result["width"] == 1
        assert result["height"] == 1
    finally:
        os.unlink(path)


def test_write_read_preserves_dimensions():
    pixels = [(0, 0, 0)] * 30
    with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
        path = f.name
    try:
        write_ppm(pixels, 5, 6, 255, path)
        result = parse_ppm(path)
        assert result["width"] == 5
        assert result["height"] == 6
    finally:
        os.unlink(path)


def test_write_read_strict_returns_object():
    pixels = [(128, 64, 32)] * 9
    with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
        path = f.name
    try:
        write_ppm(pixels, 3, 3, 255, path)
        result = parse_ppm_strict(path)
        assert hasattr(result, "width")
        assert result.width == 3
        assert result.height == 3
    finally:
        os.unlink(path)


def test_write_with_comment():
    pixels = [(0, 0, 0)] * 4
    with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
        path = f.name
    try:
        write_ppm(pixels, 2, 2, 255, path, comment="test comment")
        result = parse_ppm(path)
        assert result["ok"] is True
    finally:
        os.unlink(path)


def test_write_read_maxval_variation():
    pixels = [(100, 100, 100)] * 4
    with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
        path = f.name
    try:
        write_ppm(pixels, 2, 2, 100, path)
        result = parse_ppm(path)
        assert result["ok"] is True
        assert result["maxval"] == 100
    finally:
        os.unlink(path)


def test_write_read_large_image():
    pixels = [(i % 256, (i * 2) % 256, (i * 3) % 256) for i in range(10000)]
    with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
        path = f.name
    try:
        write_ppm(pixels, 100, 100, 255, path)
        result = parse_ppm(path)
        assert result["ok"] is True
        assert result["pixel_count"] == 10000
    finally:
        os.unlink(path)
